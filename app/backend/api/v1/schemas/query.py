"""Pydantic schemas for API request/response models."""

from pydantic import BaseModel, Field


class FilterParams(BaseModel):
    regions: list[str] | None = None
    types: list[str] | None = None
    countries: list[str] | None = None
    aum_min: float | None = None
    aum_max: float | None = None
    check_size_min: float | None = None
    sectors: list[str] | None = None
    direct_investment: str | None = None
    co_invest_frequency: str | None = None
    esg_level: str | None = None


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000, description="Natural language query")
    filters: FilterParams | None = None
    top_k: int = Field(default=10, ge=1, le=50)


class FamilyOfficeResult(BaseModel):
    name: str
    type: str
    region: str
    country: str
    aum_b: float
    sector_focus: str
    relevance_score: float
    summary: str


class QueryAnalysis(BaseModel):
    original_query: str
    semantic_query: str | None = None
    extracted_filters: dict = {}
    total_candidates_after_filter: int = 0


class QueryResponse(BaseModel):
    answer: str
    sources: list[FamilyOfficeResult]
    query_analysis: QueryAnalysis
    total_matches: int


class FilterOptions(BaseModel):
    regions: list[str]
    types: list[str]
    countries: list[str]
    sectors: list[str]
    aum_range: dict
    co_invest_frequencies: list[str]
    esg_levels: list[str]


class HealthResponse(BaseModel):
    status: str
    records: int
    index_loaded: bool
    model: str


class StatsResponse(BaseModel):
    total_records: int
    total_fields: int
    type_breakdown: dict
    region_breakdown: dict
    aum_stats: dict
    confidence_breakdown: dict


class HistoryEntry(BaseModel):
    id: str
    query: str
    answer: str
    sources: list[FamilyOfficeResult] = []
    query_analysis: QueryAnalysis | None = None
    total_matches: int = 0
    timestamp: str
