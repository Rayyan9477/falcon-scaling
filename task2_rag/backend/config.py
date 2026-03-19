"""Application configuration via Pydantic BaseSettings (env-driven)."""

from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM (LiteLLM — model-agnostic)
    llm_model: str = "gpt-4o-mini"
    llm_api_key: str = ""
    llm_api_base: str = ""  # Custom API base URL (e.g., http://localhost:1234/v1 for LM Studio)

    # Embeddings
    embedding_model: str = "all-MiniLM-L6-v2"

    # Dataset
    dataset_path: str = str(Path(__file__).resolve().parent.parent.parent / "data" / "family_office_dataset.xlsx")

    # FAISS index
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
