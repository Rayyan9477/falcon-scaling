"""In-memory query history store with JSON persistence."""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


class QueryHistory:
    """Stores query history in memory with optional JSON file persistence."""

    MAX_ENTRIES = 200

    def __init__(self, persist_path: str | None = None):
        self._history: list[dict] = []
        self._persist_path = Path(persist_path) if persist_path else None
        if self._persist_path and self._persist_path.exists():
            try:
                with open(self._persist_path, "r", encoding="utf-8") as f:
                    self._history = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._history = []

    def add(self, query: str, answer: str, sources: list[dict],
            query_analysis: dict | None = None, total_matches: int = 0) -> dict:
        """Add a query-answer pair to history. Returns the entry."""
        entry = {
            "id": str(uuid.uuid4()),
            "query": query,
            "answer": answer,
            "sources": sources,
            "query_analysis": query_analysis,
            "total_matches": total_matches,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._history.append(entry)

        # Trim oldest entries if over limit
        if len(self._history) > self.MAX_ENTRIES:
            self._history = self._history[-self.MAX_ENTRIES:]

        self._persist()
        return entry

    def get_all(self, limit: int = 50, offset: int = 0) -> list[dict]:
        """Return history entries, newest first."""
        reversed_history = list(reversed(self._history))
        return reversed_history[offset:offset + limit]

    def get_by_id(self, entry_id: str) -> dict | None:
        """Return a specific history entry."""
        for entry in self._history:
            if entry["id"] == entry_id:
                return entry
        return None

    def clear(self) -> int:
        """Clear all history. Returns count of deleted entries."""
        count = len(self._history)
        self._history = []
        self._persist()
        return count

    def _persist(self):
        """Write history to disk if persist_path is configured."""
        if self._persist_path:
            self._persist_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._persist_path, "w", encoding="utf-8") as f:
                json.dump(self._history, f, ensure_ascii=False, indent=2)
