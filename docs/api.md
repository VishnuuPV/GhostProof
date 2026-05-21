# GhostProof API

Base URL: `/api/v1`

## `POST /analyze`

Runs immediate analysis. Use for small text snippets, image URLs, and extension scans.

```json
{
  "media_type": "text",
  "source_url": "https://example.com/article",
  "content": "Text to analyze",
  "metadata": {
    "page_title": "Example"
  },
  "options": {
    "explain": true,
    "privacy_mode": "standard"
  }
}
```

Response:

```json
{
  "scan_id": "scan_...",
  "media_type": "text",
  "risk_level": "medium",
  "authenticity_score": 64.2,
  "confidence": 0.71,
  "summary": "Predictable sentence rhythm and repeated phrasing increased synthetic-text risk.",
  "modality_scores": {
    "text": {
      "ai_probability": 0.36,
      "authenticity_score": 64.2,
      "confidence": 0.71,
      "reasons": ["low burstiness", "repeated phrase pattern"],
      "evidence": []
    }
  }
}
```

## `POST /jobs`

Creates async scan job. Use for video/audio or large media.

## `GET /jobs/{job_id}`

Returns job status and report when complete.

## `GET /history`

Returns recent scan reports.

## `GET /health`

Returns backend status and AI service connectivity.
