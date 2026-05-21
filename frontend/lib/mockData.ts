import type { DashboardReport } from "./types";

export const mockReports: DashboardReport[] = [
  {
    scan_id: "scan_demo_video",
    media_type: "video",
    risk_level: "high",
    authenticity_score: 28,
    ai_probability: 0.72,
    confidence: 0.84,
    summary: "High risk driven by temporal instability and face warping indicators.",
    source_url: "https://news.example/video/interview",
    content_hash: "demo-video",
    tamper_hash: "demo-video-chain",
    created_at: new Date(Date.now() - 1000 * 60 * 8).toISOString(),
    evidence: [
      {
        code: "VIDEO_TEMPORAL_INSTABILITY",
        title: "Temporal instability",
        description: "Face-region geometry shifts across adjacent frames.",
        modality: "video",
        severity: 0.78
      }
    ]
  },
  {
    scan_id: "scan_demo_image",
    media_type: "image",
    risk_level: "medium",
    authenticity_score: 59,
    ai_probability: 0.41,
    confidence: 0.69,
    summary: "Medium risk driven by missing metadata and generated asset dimensions.",
    source_url: "https://social.example/post/123",
    content_hash: "demo-image",
    tamper_hash: "demo-image-chain",
    created_at: new Date(Date.now() - 1000 * 60 * 22).toISOString(),
    evidence: [
      {
        code: "IMAGE_METADATA_ABSENT",
        title: "Missing capture metadata",
        description: "No camera lineage metadata supplied.",
        modality: "image",
        severity: 0.38
      }
    ]
  },
  {
    scan_id: "scan_demo_text",
    media_type: "text",
    risk_level: "low",
    authenticity_score: 82,
    ai_probability: 0.18,
    confidence: 0.63,
    summary: "No high-severity synthetic text indicators were detected.",
    source_url: "https://blog.example/analysis",
    content_hash: "demo-text",
    tamper_hash: "demo-text-chain",
    created_at: new Date(Date.now() - 1000 * 60 * 41).toISOString(),
    evidence: []
  }
];
