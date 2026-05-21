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

export interface ModalityResult {
  media_type: MediaType;
  ai_probability: number;
  authenticity_score: number;
  confidence: number;
  reasons: string[];
  evidence: Evidence[];
  suspicious_regions: Array<Record<string, unknown>>;
  manipulated_timestamps: Array<Record<string, unknown>>;
  features: Record<string, unknown>;
  model_version: string;
}

export interface ScanReport {
  scan_id: string;
  created_at: string;
  media_type: MediaType;
  risk_level: RiskLevel;
  authenticity_score: number;
  ai_probability: number;
  confidence: number;
  summary: string;
  modality_scores: Record<string, ModalityResult>;
  evidence: Evidence[];
  content_hash: string;
  tamper_hash?: string;
}

export interface MediaCandidate {
  id: string;
  mediaType: MediaType;
  sourceUrl?: string;
  content?: string;
  metadata: Record<string, unknown>;
}

export interface AnalyzeRequest {
  media_type: MediaType;
  source_url?: string;
  content?: string;
  metadata: Record<string, unknown>;
  options?: {
    explain?: boolean;
    privacy_mode?: "standard" | "strict" | "local_only";
    max_frames?: number;
    enable_remote_fetch?: boolean;
  };
}
