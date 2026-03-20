export interface FilterParams {
  regions?: string[];
  types?: string[];
  countries?: string[];
  aum_min?: number;
  aum_max?: number;
  check_size_min?: number;
  sectors?: string[];
  direct_investment?: string;
  co_invest_frequency?: string;
  esg_level?: string;
}

export interface QueryRequest {
  query: string;
  filters?: FilterParams;
  top_k?: number;
}

export interface FamilyOfficeResult {
  name: string;
  type: string;
  region: string;
  country: string;
  aum_b: number;
  sector_focus: string;
  relevance_score: number;
  summary: string;
}

export interface QueryAnalysis {
  original_query: string;
  semantic_query?: string;
  extracted_filters: Record<string, unknown>;
  total_candidates_after_filter: number;
}

export interface QueryResponse {
  answer: string;
  sources: FamilyOfficeResult[];
  query_analysis: QueryAnalysis;
  total_matches: number;
}

export interface FilterOptions {
  regions: string[];
  types: string[];
  countries: string[];
  sectors: string[];
  aum_range: { min: number; max: number };
  co_invest_frequencies: string[];
  esg_levels: string[];
}

export interface StatsResponse {
  total_records: number;
  total_fields: number;
  type_breakdown: Record<string, number>;
  region_breakdown: Record<string, number>;
  aum_stats: { min: number; max: number; avg: number; median: number };
  confidence_breakdown: Record<string, number>;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: FamilyOfficeResult[];
  queryAnalysis?: QueryAnalysis;
  timestamp: Date;
}

export interface HistoryEntry {
  id: string;
  query: string;
  answer: string;
  sources: FamilyOfficeResult[];
  query_analysis: QueryAnalysis | null;
  total_matches: number;
  timestamp: string;
}
