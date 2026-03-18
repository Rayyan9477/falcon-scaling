"""LiteLLM wrapper for model-agnostic LLM calls."""

import json
import os
import litellm

# Suppress litellm verbose logs
litellm.set_verbose = False


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

    def __init__(self, model: str = "gpt-4o-mini", api_key: str | None = None):
        self.model = model
        if api_key:
            # Set the appropriate env var based on model prefix
            if "gpt" in model or "o1" in model or "o3" in model:
                os.environ["OPENAI_API_KEY"] = api_key
            elif "claude" in model:
                os.environ["ANTHROPIC_API_KEY"] = api_key
            elif "groq" in model:
                os.environ["GROQ_API_KEY"] = api_key
            else:
                os.environ["OPENAI_API_KEY"] = api_key

    async def extract_filters(self, query: str) -> dict:
        """Use function calling to extract structured filters from a natural language query."""
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
            # Fallback: treat entire query as semantic
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
