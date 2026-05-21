export type MediaType = "image" | "video" | "audio" | "text" | "multimodal";
export type RiskLevel = "low" | "medium" | "high" | "critical";

export interface Evidence {
  code: string;
  title: string;
  description: string;
  modality: MediaType;
  severity: number;
  location?: Record<string, unknown>;
  recommendation?: string;
}

export interface ScanHistoryItem {
  scan_id: string;
  media_type: MediaType;
  risk_level: RiskLevel;
  authenticity_score: number;
  ai_probability: number;
  confidence: number;
  summary: string;
  source_url?: string;
  content_hash: string;
  tamper_hash: string;
  created_at: string;
}

export interface DashboardReport extends ScanHistoryItem {
  evidence?: Evidence[];
}
