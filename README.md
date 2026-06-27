# GhostProof

Browser-based synthetic media detection for images, video, audio, and text — built privacy-first, so you can check what you're looking at without shipping your data off to a third party by default.

GhostProof scans content as you browse and gives you an authenticity score, a risk level, and *why* — concrete evidence, not just a number. It's structured as a production-style MVP across four cooperating services:

- `extension/` — Chrome Manifest V3 extension. Discovers images, video, audio, and text on the page you're viewing, scans them in the background, and overlays a risk badge with an evidence panel.
- `frontend/` — Next.js dashboard for scan history, evidence review, and operational monitoring.
- `backend/` — FastAPI API for scan orchestration, persistence, auth-ready boundaries, and sync/async job lifecycle.
- `ai-services/` — Python inference package (`ghostproof_ai`) with modality-specific detection pipelines, plus an optional standalone inference service.
- `shared/` — cross-client schemas and TypeScript contracts so the extension, dashboard, and backend agree on one data shape.
- `docker/` — container definitions.
- `docs/` — architecture, API, ML, roadmap, deployment notes.

GhostProof does not claim perfect detection. It combines model outputs, forensic heuristics, metadata, and explainability into risk estimates with evidence — and it's explicit about its current limitations (see [Current Detection Approach](#current-detection-approach) below).

## Why privacy-first

Most "send us your media and we'll tell you if it's fake" tools require uploading the actual file to a third-party server. GhostProof is built to avoid that by default:

- **Metadata over content.** The extension's content script extracts signals about media on the page (dimensions, duration, alt text, surrounding text) rather than the raw file. By default it sends metadata to the backend, not the image/video/audio bytes themselves.
- **`enable_remote_fetch` is opt-in, not default.** Every analysis request carries an explicit flag for whether the backend is allowed to fetch the source URL itself. The extension currently sends `enable_remote_fetch: false` for every scan — nothing is fetched server-side unless a future flow turns this on deliberately.
- **Per-request privacy modes.** Every scan declares a `privacy_mode`: `standard`, `strict`, or `local_only`. The extension defaults to `strict` for images/video/audio and `standard` for text, and `local_only` is reserved for fully on-device analysis paths.
- **Local inference by default.** `GHOSTPROOF_INFERENCE_MODE=local` runs detection inside the backend process itself — no network hop to a separate AI vendor or service is required to get a result.
- **Content integrity, not surveillance.** Every report carries a `content_hash` (what was analyzed) and a `tamper_hash` (whether the report itself has been altered), so results are auditable without needing to retain the original media.
- **Locked-down CORS.** The API only answers browser-origin requests from the dashboard (`localhost:3000`) and the extension (`chrome-extension://*`) — not the open web.

The roadmap (below) goes further: redact-before-upload and stricter allowlist controls are explicitly planned so users keep control over what ever leaves the browser.

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

Local services:

| Service       | URL                          |
|---------------|-------------------------------|
| Backend API   | `http://localhost:8000`       |
| API docs      | `http://localhost:8000/docs`  |
| AI service    | `http://localhost:8100`       |
| Dashboard     | `http://localhost:3000`       |

## Local Development

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ../ai-services -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

AI service:

```bash
cd ai-services
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn service.main:app --reload --port 8100
```

Dashboard:

```bash
cd frontend
npm install
npm run dev
```

Extension:

```bash
cd extension
npm install
npm run build
```

Load `extension/dist` as an unpacked extension in Chrome. The build reads `VITE_GHOSTPROOF_API_URL` (defaults to `http://localhost:8000`) — set it before building if your backend runs on a different port.

> If port 8000 is already taken by something else on your machine, the extension will silently fail every scan (it just shows "API unreachable" in the popup). Either free the port or rebuild with `VITE_GHOSTPROOF_API_URL` pointed at wherever the backend actually is.

## How a scan works

1. The extension's content script finds candidate media on the page (`extension/src/content/mediaExtractor.ts`) and assigns each one a stable ID.
2. It sends a scan request to the backend (`POST /api/v1/analyze`) with the media type, optional source URL, optional text content, and metadata — honoring the privacy mode described above.
3. The backend's `DetectionOrchestrator` (`ai-services/ghostproof_ai/orchestrator.py`) routes the request to the matching modality pipeline (image, video, audio, or text), computes a weighted risk score (`ghostproof_ai/risk/scoring.py`), and attaches explainable evidence.
4. The response — risk level, authenticity score, evidence, content hash, tamper hash — is persisted to the backend's database and pushed back to the page. Medium-risk-and-above results render an on-page badge; every result (regardless of risk level) is stored in the extension's local scan history, viewable from the popup.

## Current Detection Approach

Today, every modality pipeline (`ai-services/ghostproof_ai/pipelines/`) runs on **deterministic heuristics**, not trained ML models — they're tagged `model_version: "heuristic-fallback-v1"` in every response so this is never hidden from API consumers. Concretely:

- **Text**: scores based on length, repetition, and structural signals.
- **Image**: scores based on metadata (dimensions, EXIF-style signals) rather than pixel content.
- **Video**: scores based on duration and frame-count metadata; it explicitly flags `VIDEO_FRAME_SAMPLING_REQUIRED` evidence when no real frame data was supplied, because the client doesn't currently extract or send temporal/lip-sync/face-warp signals.
- **Audio**: scores based on duration and channel metadata.

This keeps the system fast, dependency-light, and able to run fully offline — but it means risk scores today are a reasonable placeholder, not a validated deepfake/AI-content classifier. The single highest-leverage improvement to detection *accuracy* is swapping these heuristic pipelines for real trained models (a pretrained AI-image classifier, a voice-clone detector, a fine-tuned AI-text classifier, frame-sampled temporal-consistency checks for video) — see [Production Next Steps](#production-next-steps).

## MVP Scope

- Real browser content discovery for image, video, audio, and visible text.
- Backend scan API with synchronous and async job modes.
- Modular AI pipelines with deterministic heuristic fallbacks.
- Explainable risk outputs, evidence lists, heatmap/timestamp structures, and confidence metrics.
- Persistent scan records through SQLAlchemy models.
- Redis-ready job/cache boundary.
- Dashboard with risk overview, timeline, and evidence panels.
- Docker Compose with Postgres, Redis, backend, AI service, and dashboard.

## Production Next Steps

- Replace fallback heuristics with validated model artifacts (real image/audio/text/video classifiers in place of metadata-only heuristics).
- Add authentication and tenant isolation.
- Add signed model registry and model drift monitoring.
- Add streaming video/audio chunk analysis with real client-side frame/temporal sampling.
- Add privacy modes: local-only scan, redact-before-upload, and allowlist controls.
- Add adversarial robustness suite and calibration dataset.
