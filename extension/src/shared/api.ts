import type { AnalyzeRequest, MediaCandidate, ScanReport } from "./types";

const API_URL = import.meta.env.VITE_GHOSTPROOF_API_URL ?? "http://localhost:8000";

export async function analyzeCandidate(candidate: MediaCandidate): Promise<ScanReport> {
  const payload: AnalyzeRequest = {
    media_type: candidate.mediaType,
    source_url: candidate.sourceUrl,
    content: candidate.content,
    metadata: {
      ...candidate.metadata,
      extension_candidate_id: candidate.id,
      page_url: candidate.metadata.pageUrl ?? candidate.metadata.page_url
    },
    options: {
      explain: true,
      privacy_mode: candidate.mediaType === "text" ? "standard" : "strict",
      enable_remote_fetch: false
    }
  };

  const response = await fetch(`${API_URL}/api/v1/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    throw new Error(`GhostProof API error ${response.status}`);
  }

  return response.json() as Promise<ScanReport>;
}
