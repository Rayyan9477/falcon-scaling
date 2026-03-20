"""Data ingestion: XLSX -> rich-text documents -> numpy vector index."""

import json
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

from core.embeddings import EmbeddingModel


def load_dataset(path: str) -> pd.DataFrame:
    """Load the family office XLSX dataset into a DataFrame."""
    df = pd.read_excel(path, sheet_name="Family Office Intelligence", engine="openpyxl")
    return df


def row_to_document(row: pd.Series) -> str:
    """Convert a single DataFrame row into a rich-text document for embedding."""

    def safe(val, default="N/A"):
        if pd.isna(val) or val is None or str(val).strip() == "":
            return default
        return str(val).strip()

    doc = (
        f"{safe(row.get('Family Office Name'))} is a "
        f"{'Single Family Office (SFO)' if safe(row.get('Type (SFO/MFO)')) == 'SFO' else 'Multi-Family Office (MFO)'} "
        f"founded by the {safe(row.get('Founding Family'))} "
        f"in {safe(row.get('Year Est.'))}, headquartered in {safe(row.get('HQ City'))}, "
        f"{safe(row.get('HQ Country'))} ({safe(row.get('Region'))}). "
        f"Website: {safe(row.get('Website'))}. "
        f"Assets Under Management: ${safe(row.get('AUM ($B)'))}B. "
        f"Estimated Family Net Worth: ${safe(row.get('Est. Family Net Worth ($B)'))}B. "
        f"Employees: {safe(row.get('Employee Count (Est.)'))}.\n\n"

        f"DECISION MAKERS: Primary: {safe(row.get('Primary Decision Maker'))} "
        f"({safe(row.get('Primary DM Title'))}). "
        f"Secondary: {safe(row.get('Secondary Decision Maker'))} "
        f"({safe(row.get('Secondary DM Title'))}).\n\n"

        f"INVESTMENT PROFILE: Strategy: {safe(row.get('Investment Strategy'))}. "
        f"Sector Focus: {safe(row.get('Sector Focus'))}. "
        f"Geographic Focus: {safe(row.get('Geographic Focus'))}. "
        f"Asset Classes: {safe(row.get('Asset Classes'))}. "
        f"Check Size: ${safe(row.get('Check Size Min ($M)'))}M - ${safe(row.get('Check Size Max ($M)'))}M. "
        f"Investment Stage: {safe(row.get('Investment Stage'))}. "
        f"Direct Investment: {safe(row.get('Direct Investment'))}. "
        f"Co-Invest Frequency: {safe(row.get('Co-Invest Frequency'))}.\n\n"

        f"RELATIONSHIPS: LP Status: {safe(row.get('LP Status'))}. "
        f"GP/Direct: {safe(row.get('GP/Direct Status'))}. "
        f"Fund Relationships: {safe(row.get('Fund Relationships'))}. "
        f"Co-Investors: {safe(row.get('Co-Investor Relationships'))}.\n\n"

        f"SIGNALS: Recent News: {safe(row.get('Recent News (2024-2025)'))}. "
        f"Recent Deals: {safe(row.get('Recent Deals'))}. "
        f"Last Deal: {safe(row.get('Last Deal Date'))}.\n\n"

        f"BACKGROUND: Source of Wealth: {safe(row.get('Source of Wealth'))} "
        f"({safe(row.get('Wealth Origin Sector'))}). "
        f"ESG/Impact: {safe(row.get('ESG/Impact Level'))}. "
        f"Next-Gen: {safe(row.get('Next-Gen Involvement'))}. "
        f"Philanthropy: {safe(row.get('Philanthropy Focus'))}. "
        f"Data Confidence: {safe(row.get('Data Confidence'))}."
    )
    return doc


def row_to_metadata(row: pd.Series) -> dict:
    """Extract structured metadata from a row for filtering."""

    def safe_str(val, default=""):
        if pd.isna(val) or val is None:
            return default
        return str(val).strip()

    def safe_float(val, default=0.0):
        try:
            f = float(val)
            return default if pd.isna(f) else f
        except (ValueError, TypeError):
            return default

    return {
        "fo_name": safe_str(row.get("Family Office Name")),
        "type": safe_str(row.get("Type (SFO/MFO)")),
        "founding_family": safe_str(row.get("Founding Family")),
        "hq_city": safe_str(row.get("HQ City")),
        "hq_country": safe_str(row.get("HQ Country")),
        "region": safe_str(row.get("Region")),
        "aum_b": safe_float(row.get("AUM ($B)")),
        "check_min_m": safe_float(row.get("Check Size Min ($M)")),
        "check_max_m": safe_float(row.get("Check Size Max ($M)")),
        "sector_focus": safe_str(row.get("Sector Focus")),
        "investment_strategy": safe_str(row.get("Investment Strategy")),
        "direct_investment": safe_str(row.get("Direct Investment")),
        "co_invest_frequency": safe_str(row.get("Co-Invest Frequency")),
        "esg_level": safe_str(row.get("ESG/Impact Level")),
        "data_confidence": safe_str(row.get("Data Confidence")),
        "primary_dm": safe_str(row.get("Primary Decision Maker")),
        "primary_dm_title": safe_str(row.get("Primary DM Title")),
    }


def build_index(dataset_path: str, index_dir: str, embedding_model: EmbeddingModel) -> tuple:
    """
    Build numpy vector index from the dataset.
    Returns (embeddings_matrix, documents, metadata_list, dataframe).
    """
    df = load_dataset(dataset_path)

    documents = []
    metadata_list = []
    for _, row in df.iterrows():
        documents.append(row_to_document(row))
        metadata_list.append(row_to_metadata(row))

    # Embed all documents via OpenAI API
    embeddings = embedding_model.encode(documents)

    # Normalize for cosine similarity
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1
    embeddings = embeddings / norms

    # Save to disk
    index_path = Path(index_dir)
    index_path.mkdir(parents=True, exist_ok=True)

    np.save(str(index_path / "embeddings.npy"), embeddings)

    with open(index_path / "documents.pkl", "wb") as f:
        pickle.dump(documents, f)

    with open(index_path / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata_list, f, ensure_ascii=False, indent=2)

    return embeddings, documents, metadata_list, df


def load_index(index_dir: str) -> tuple | None:
    """Load existing vector index from disk. Returns None if not found."""
    index_path = Path(index_dir)

    emb_file = index_path / "embeddings.npy"
    docs_file = index_path / "documents.pkl"
    meta_file = index_path / "metadata.json"

    if not all(f.exists() for f in [emb_file, docs_file, meta_file]):
        return None

    embeddings = np.load(str(emb_file))

    with open(docs_file, "rb") as f:
        documents = pickle.load(f)

    with open(meta_file, "r", encoding="utf-8") as f:
        metadata_list = json.load(f)

    return embeddings, documents, metadata_list
