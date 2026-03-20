"""OpenAI SDK wrapper for LLM calls with fallback and rate control."""

import json
import logging
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


FILTER_EXTRACTION_TOOL = {
    "type": "function",
    "function": {
        "name": "extract_query_filters",
        "description": "Extract structured filters and semantic intent from a natural language query about family offices.",
        "parameters": {
            "type": "object",
            "properties": {
                "semantic_query": {
                    "type": "string",
                    "description": "The semantic/topical part of the query for embedding search (e.g., 'AI technology focus', 'healthcare investments'). Leave empty if query is purely structured."
                },
                "regions": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["North America", "Europe", "Asia-Pacific", "Middle East", "Latin America", "Africa"]},
                    "description": "Filter by geographic regions."
                },
                "types": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["SFO", "MFO"]},
                    "description": "Filter by family office type (SFO=Single, MFO=Multi)."
                },
                "countries": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Filter by specific countries."
                },
                "aum_min": {
                    "type": "number",
                    "description": "Minimum AUM in billions USD."
                },
                "aum_max": {
                    "type": "number",
                    "description": "Maximum AUM in billions USD."
                },
                "check_size_min": {
                    "type": "number",
                    "description": "Minimum check size in millions USD."
                },
                "sectors": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Sectors of interest (e.g., 'Technology', 'Healthcare', 'Real Estate')."
                },
                "direct_investment": {
                    "type": "string",
                    "enum": ["Yes", "No"],
                    "description": "Filter by whether FO does direct investments."
                },
                "co_invest_frequency": {
                    "type": "string",
                    "enum": ["Low", "Medium", "High"],
                    "description": "Filter by co-investment frequency."
                },
                "esg_level": {
                    "type": "string",
                    "description": "Filter by ESG/impact level."
                }
            },
            "required": ["semantic_query"]
        }
    }
}


class LLMClient:
    """OpenAI-compatible LLM client with automatic fallback and rate control."""

    FALLBACK_MODEL = "gpt-4.1-mini"
    MAX_TOKENS_FILTER = 300
    MAX_TOKENS_ANSWER = 1500
    MAX_RETRIES = 2

    def __init__(self, model: str = "gpt-4o", api_key: str | None = None,
                 api_base: str | None = None, fallback_api_key: str | None = None):
        self.model = model
        self.fallback_api_key = fallback_api_key
        self._using_fallback = False

        # Primary client
        self.client = AsyncOpenAI(
            api_key=api_key or "sk-placeholder",
            base_url=api_base or None,
            max_retries=self.MAX_RETRIES,
        )

        # Fallback client (always points to OpenAI directly)
        self.fallback_client = None
        if fallback_api_key:
            self.fallback_client = AsyncOpenAI(
                api_key=fallback_api_key,
                max_retries=self.MAX_RETRIES,
            )

    async def _call_with_fallback(self, **kwargs):
        """Try the primary model; if it fails, fall back."""
        try:
            return await self.client.chat.completions.create(model=self.model, **kwargs)
        except Exception as primary_err:
            if self.fallback_client and self.model != self.FALLBACK_MODEL:
                logger.warning("Primary model '%s' failed (%s), falling back to %s",
                               self.model, type(primary_err).__name__, self.FALLBACK_MODEL)
                result = await self.fallback_client.chat.completions.create(
                    model=self.FALLBACK_MODEL, **kwargs
                )
                self._using_fallback = True
                return result
            raise

    async def extract_filters(self, query: str) -> dict:
        """Use function calling to extract structured filters from a natural language query."""
        # Try function calling first
        try:
            response = await self._call_with_fallback(
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a query analyzer for a family office intelligence database. "
                            "Extract structured filters and semantic intent from the user's natural language query. "
                            "Be precise with filter extraction. Only include filters that are explicitly or clearly implied in the query."
                        )
                    },
                    {"role": "user", "content": query}
                ],
                tools=[FILTER_EXTRACTION_TOOL],
                tool_choice={"type": "function", "function": {"name": "extract_query_filters"}},
                temperature=0,
                max_tokens=self.MAX_TOKENS_FILTER,
            )
            tool_call = response.choices[0].message.tool_calls[0]
            return json.loads(tool_call.function.arguments)
        except Exception:
            pass

        # Fallback: prompt-based JSON extraction (for local models without tool support)
        try:
            response = await self._call_with_fallback(
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a query analyzer. Extract filters from the user's query about family offices.\n"
                            "Return ONLY a valid JSON object with these optional fields:\n"
                            '- "semantic_query": the topical/semantic part for search (string)\n'
                            '- "regions": list of regions like "North America", "Europe", "Asia-Pacific", "Middle East", "Latin America", "Africa"\n'
                            '- "types": list of "SFO" or "MFO"\n'
                            '- "aum_min": minimum AUM in billions (number)\n'
                            '- "aum_max": maximum AUM in billions (number)\n'
                            '- "check_size_min": minimum check size in millions (number)\n'
                            '- "sectors": list of sectors like "Technology", "Healthcare", "Real Estate"\n'
                            '- "direct_investment": "Yes" or "No"\n'
                            '- "co_invest_frequency": "Low", "Medium", or "High"\n'
                            "Return ONLY the JSON, no markdown, no explanation."
                        )
                    },
                    {"role": "user", "content": query}
                ],
                temperature=0,
                max_tokens=self.MAX_TOKENS_FILTER,
            )
            text = response.choices[0].message.content.strip()
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()
            return json.loads(text)
        except Exception:
            return {"semantic_query": query}

    def _build_answer_prompt(self, query: str, context: str, filter_summary: str = "") -> list[dict]:
        """Build the message list for answer generation."""
        system_prompt = (
            "You are a family office intelligence analyst. Answer the user's query using ONLY the data provided below.\n\n"
            "FORMATTING RULES (follow strictly):\n"
            "- Start with a brief 1-2 sentence summary answering the question.\n"
            "- When listing family offices, use numbered items with each on its OWN LINE.\n"
            "- For each family office entry, use this exact format:\n"
            "  1. **Name** (Type)\n"
            "     - Headquarters: City, Country\n"
            "     - Sector Focus: sectors here\n"
            "     - AUM: $XB\n"
            "     - Key Detail: relevant info for the query\n"
            "\n"
            "- Use blank lines between numbered items for readability.\n"
            "- Bold (**text**) family office names and important figures.\n"
            "- End with a brief concluding insight if relevant.\n"
            "- Be specific -- cite names, numbers, and details from the data.\n"
            "- If the data doesn't fully answer the question, say so honestly.\n\n"
            f"RETRIEVED DATA:\n{context}"
        )
        if filter_summary:
            system_prompt += f"\n\nFILTERS APPLIED:\n{filter_summary}"
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query},
        ]

    async def generate_answer(self, query: str, context: str, filter_summary: str = "") -> str:
        """Generate a grounded answer from retrieved context."""
        messages = self._build_answer_prompt(query, context, filter_summary)
        try:
            response = await self._call_with_fallback(
                messages=messages,
                temperature=0.1,
                max_tokens=self.MAX_TOKENS_ANSWER,
            )
            return response.choices[0].message.content
        except Exception as e:
            return (
                f"Unable to generate a synthesized answer due to an LLM error ({type(e).__name__}). "
                "However, the retrieved family office records above contain the relevant data for your query."
            )

    async def generate_answer_stream(self, query: str, context: str, filter_summary: str = ""):
        """Stream a grounded answer token-by-token. Yields string chunks."""
        messages = self._build_answer_prompt(query, context, filter_summary)
        client = self.client
        model = self.model

        try:
            stream = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.1,
                max_tokens=self.MAX_TOKENS_ANSWER,
                stream=True,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    yield delta.content
        except Exception:
            # Try fallback model for streaming
            if self.fallback_client and self.model != self.FALLBACK_MODEL:
                try:
                    stream = await self.fallback_client.chat.completions.create(
                        model=self.FALLBACK_MODEL,
                        messages=messages,
                        temperature=0.1,
                        max_tokens=self.MAX_TOKENS_ANSWER,
                        stream=True,
                    )
                    async for chunk in stream:
                        delta = chunk.choices[0].delta
                        if delta and delta.content:
                            yield delta.content
                except Exception:
                    yield "Unable to generate a streaming answer due to an LLM error."
            else:
                yield "Unable to generate a streaming answer due to an LLM error."
