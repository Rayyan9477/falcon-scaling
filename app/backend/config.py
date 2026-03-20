"""Application configuration via Pydantic BaseSettings (env-driven)."""

from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM (OpenAI SDK — supports any OpenAI-compatible endpoint)
    llm_model: str = "gpt-4.1"
    llm_api_key: str = ""
    llm_api_base: str = ""  # Custom API base URL (e.g., http://localhost:1234/v1 for LM Studio)
    llm_fallback_api_key: str = ""  # Separate OpenAI key for fallback if primary model is unavailable

    # Embeddings (OpenAI)
    embedding_model: str = "text-embedding-3-small"

    # Dataset (look in backend/data/ first, fall back to repo root data/)
    dataset_path: str = str(Path(__file__).resolve().parent / "data" / "family_office_dataset.xlsx")

    # Vector index (numpy embeddings cache)
    index_dir: str = str(Path(__file__).resolve().parent / "index")

    # Server
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    model_config = {
        "env_file": str(Path(__file__).resolve().parent / ".env"),
        "env_file_encoding": "utf-8",
    }


settings = Settings()
