"""LiteLLM wrapper for model-agnostic LLM calls."""

import json
import os
import litellm

# Suppress litellm verbose logs
import logging
logging.getLogger("LiteLLM").setLevel(logging.WARNING)
logging.getLogger("litellm").setLevel(logging.WARNING)


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
    """Model-agnostic LLM client via LiteLLM."""

    def __init__(self, model: str = "gpt-4o-mini", api_key: str | None = None, api_base: str | None = None):
        self.model = model
        self.api_base = api_base or None  # e.g., "http://localhost:1234/v1" for LM Studio

        if api_key:
            # Set the appropriate env var based on model prefix
            if "gpt" in model or "o1" in model or "o3" in model or model.startswith("openai/"):
                os.environ["OPENAI_API_KEY"] = api_key
            elif "claude" in model:
                os.environ["ANTHROPIC_API_KEY"] = api_key
            elif "groq" in model:
                os.environ["GROQ_API_KEY"] = api_key
            else:
                os.environ["OPENAI_API_KEY"] = api_key

        # For local models (LM Studio, Ollama, etc.), set the base URL
        if self.api_base:
            os.environ["OPENAI_API_BASE"] = self.api_base

    async def extract_filters(self, query: str) -> dict:
        """Use function calling to extract structured filters from a natural language query.
        Falls back to JSON-prompt extraction for local models that don't support tool calling."""
        # Try function calling first (works with OpenAI, Anthropic, Groq)
        try:
            response = await litellm.acompletion(
                model=self.model,
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
            )
            tool_call = response.choices[0].message.tool_calls[0]
            return json.loads(tool_call.function.arguments)
        except Exception:
            pass

        # Fallback: prompt-based JSON extraction (for local models like Qwen, Llama, etc.)
        try:
            response = await litellm.acompletion(
                model=self.model,
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
            )
            text = response.choices[0].message.content.strip()
            # Extract JSON from response (handle markdown code blocks)
            if "```" in text:
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
                text = text.strip()
            return json.loads(text)
        except Exception:
            # Final fallback: treat entire query as semantic search
            return {"semantic_query": query}

    async def generate_answer(self, query: str, context: str, filter_summary: str = "") -> str:
        """Generate a grounded answer from retrieved context."""
        system_prompt = (
            "You are a family office intelligence analyst. Answer the user's query using ONLY the data provided below. "
            "Be specific — cite family office names, numbers, and details from the data. "
            "If the data doesn't contain enough information to fully answer, say so honestly. "
            "Format your response clearly with numbered results when listing family offices.\n\n"
            f"RETRIEVED DATA:\n{context}"
        )
        if filter_summary:
            system_prompt += f"\n\nFILTERS APPLIED:\n{filter_summary}"

        try:
            response = await litellm.acompletion(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.1,
                max_tokens=2000,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Unable to generate a synthesized answer due to an LLM error ({type(e).__name__}). However, the retrieved family office records above contain the relevant data for your query."
