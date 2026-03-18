"""Query engine: dual retrieval (FAISS semantic + Pandas structured) + LLM answer generation."""

import faiss
import numpy as np
import pandas as pd

from core.embeddings import EmbeddingModel
from core.llm import LLMClient


class QueryEngine:
    """Orchestrates query analysis, dual retrieval, and answer generation."""

    def __init__(
        self,
        faiss_index: faiss.Index,
        documents: list[str],
        metadata: list[dict],
        df: pd.DataFrame,
        embedding_model: EmbeddingModel,
        llm_client: LLMClient,
    ):
        self.index = faiss_index
        self.documents = documents
        self.metadata = metadata
        self.df = df
        self.embedder = embedding_model
        self.llm = llm_client

    def _apply_structured_filters(self, filters: dict) -> list[int]:
        """Apply structured filters on the DataFrame, return matching row indices."""
        mask = pd.Series([True] * len(self.df), index=self.df.index)

        regions = filters.get("regions")
        if regions:
            mask &= self.df["Region"].isin(regions)

        types = filters.get("types")
        if types:
            mask &= self.df["Type (SFO/MFO)"].isin(types)

        countries = filters.get("countries")
        if countries:
            mask &= self.df["HQ Country"].isin(countries)

        aum_min = filters.get("aum_min")
        if aum_min is not None:
            mask &= pd.to_numeric(self.df["AUM ($B)"], errors="coerce").fillna(0) >= aum_min

        aum_max = filters.get("aum_max")
        if aum_max is not None:
            mask &= pd.to_numeric(self.df["AUM ($B)"], errors="coerce").fillna(0) <= aum_max

        check_size_min = filters.get("check_size_min")
        if check_size_min is not None:
            mask &= pd.to_numeric(self.df["Check Size Min ($M)"], errors="coerce").fillna(0) >= check_size_min

        sectors = filters.get("sectors")
        if sectors:
            sector_mask = pd.Series([False] * len(self.df), index=self.df.index)
            for sector in sectors:
                sector_mask |= self.df["Sector Focus"].str.contains(sector, case=False, na=False)
            mask &= sector_mask

        direct = filters.get("direct_investment")
        if direct:
            mask &= self.df["Direct Investment"] == direct

        coinvest = filters.get("co_invest_frequency")
        if coinvest:
            mask &= self.df["Co-Invest Frequency"] == coinvest

        esg = filters.get("esg_level")
        if esg:
            mask &= self.df["ESG/Impact Level"].str.contains(esg, case=False, na=False)

        # Use np.where to get positional integers matching FAISS IDs (not pandas label index)
        return list(np.where(mask.values)[0])

    def _semantic_search(self, query: str, candidate_ids: list[int] | None = None, top_k: int = 10) -> list[tuple[int, float]]:
        """Run FAISS similarity search. Optionally restrict to candidate_ids."""
        query_embedding = self.embedder.encode_query(query)
        faiss.normalize_L2(query_embedding)

        if candidate_ids is not None and len(candidate_ids) == 0:
            return []

        if candidate_ids is not None:
            # Search all vectors, then filter to candidates (200 records — trivial cost)
            candidate_set = set(candidate_ids)
            k = len(self.documents)
            scores, indices = self.index.search(query_embedding, k)
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx in candidate_set:
                    results.append((int(idx), float(score)))
                if len(results) >= top_k:
                    break
            return results
        else:
            k = min(len(self.documents), top_k)
            scores, indices = self.index.search(query_embedding, k)
            return [(int(idx), float(score)) for idx, score in zip(indices[0], scores[0]) if idx >= 0]

    def _format_results(self, result_ids: list[tuple[int, float]]) -> tuple[str, list[dict]]:
        """Format retrieved results into context string and structured source list."""
        context_parts = []
        sources = []

        for idx, score in result_ids:
            if idx < 0 or idx >= len(self.metadata):
                continue
            meta = self.metadata[idx]
            doc = self.documents[idx]

            context_parts.append(f"--- Family Office #{len(context_parts)+1} ---\n{doc}")

            sources.append({
                "name": meta["fo_name"],
                "type": meta["type"],
                "region": meta["region"],
                "country": meta["hq_country"],
                "aum_b": meta["aum_b"],
                "sector_focus": meta["sector_focus"],
                "relevance_score": round(score, 4),
                "summary": f"{meta['fo_name']} ({meta['type']}) - {meta['hq_country']} - AUM: ${meta['aum_b']}B - {meta['sector_focus'][:80]}",
            })

        context = "\n\n".join(context_parts)
        return context, sources

    async def query(self, user_query: str, ui_filters: dict | None = None, top_k: int = 10) -> dict:
        """
        Full query pipeline:
        1. LLM extracts structured filters from NL query
        2. Dual retrieval (Pandas filter + FAISS semantic)
        3. LLM generates grounded answer
        """
        # Step 1: Extract filters from query via LLM
        extracted = await self.llm.extract_filters(user_query)

        # Merge UI-provided filters with LLM-extracted filters (UI takes precedence)
        if ui_filters:
            for key, val in ui_filters.items():
                if val is not None and val != [] and val != "":
                    extracted[key] = val

        semantic_query = extracted.get("semantic_query", user_query)

        # Step 2: Dual retrieval
        has_structured_filters = any(
            extracted.get(k) for k in [
                "regions", "types", "countries", "aum_min", "aum_max",
                "check_size_min", "sectors", "direct_investment",
                "co_invest_frequency", "esg_level"
            ]
        )

        candidate_ids = []
        if has_structured_filters:
            # Apply structured filters first
            candidate_ids = self._apply_structured_filters(extracted)
            filter_summary = f"Filtered to {len(candidate_ids)} candidates from structured filters."

            if semantic_query:
                # Hybrid: semantic search within filtered candidates
                results = self._semantic_search(semantic_query, candidate_ids, top_k)
            else:
                # Pure structured: return filtered candidates ranked by AUM
                results = [(idx, 1.0) for idx in candidate_ids[:top_k]]
        else:
            # Pure semantic search
            filter_summary = "No structured filters applied."
            results = self._semantic_search(semantic_query or user_query, top_k=top_k)

        # Step 3: Format and generate answer
        context, sources = self._format_results(results)

        if not sources:
            answer = "No family offices matched your query with the given filters. Try broadening your search criteria."
        else:
            answer = await self.llm.generate_answer(user_query, context, filter_summary)

        return {
            "answer": answer,
            "sources": sources,
            "query_analysis": {
                "original_query": user_query,
                "semantic_query": semantic_query,
                "extracted_filters": {k: v for k, v in extracted.items() if k != "semantic_query" and v},
                "total_candidates_after_filter": len(candidate_ids) if has_structured_filters else len(self.documents),
            },
            "total_matches": len(sources),
        }

    def get_filter_options(self) -> dict:
        """Return available filter values for the UI dropdowns."""
        return {
            "regions": sorted(self.df["Region"].dropna().unique().tolist()),
            "types": sorted(self.df["Type (SFO/MFO)"].dropna().unique().tolist()),
            "countries": sorted(self.df["HQ Country"].dropna().unique().tolist()),
            "sectors": self._extract_unique_sectors(),
            "aum_range": {
                "min": float(pd.to_numeric(self.df["AUM ($B)"], errors="coerce").fillna(0).min()),
                "max": float(pd.to_numeric(self.df["AUM ($B)"], errors="coerce").fillna(0).max()),
            },
            "co_invest_frequencies": sorted(self.df["Co-Invest Frequency"].dropna().unique().tolist()),
            "esg_levels": sorted(self.df["ESG/Impact Level"].dropna().unique().tolist()),
        }

    def _extract_unique_sectors(self) -> list[str]:
        """Extract unique individual sectors from comma-separated sector focus strings."""
        sectors = set()
        for val in self.df["Sector Focus"].dropna():
            for s in str(val).split(","):
                s = s.strip()
                if s:
                    sectors.add(s)
        return sorted(sectors)

    def get_stats(self) -> dict:
        """Return dataset statistics."""
        df = self.df
        aum = pd.to_numeric(df["AUM ($B)"], errors="coerce").fillna(0)
        return {
            "total_records": len(df),
            "total_fields": len(df.columns),
            "type_breakdown": df["Type (SFO/MFO)"].value_counts().to_dict(),
            "region_breakdown": df["Region"].value_counts().to_dict(),
            "aum_stats": {
                "min": round(float(aum.min()), 1),
                "max": round(float(aum.max()), 1),
                "avg": round(float(aum.mean()), 1),
                "median": round(float(aum.median()), 1),
            },
            "confidence_breakdown": df["Data Confidence"].value_counts().to_dict(),
        }
