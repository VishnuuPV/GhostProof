# GhostProof

Browser-based synthetic media detection system for images, video, audio, and text.

GhostProof is structured as a production-style MVP:

- `extension/` Chrome Manifest V3 extension for page scanning, right-click analysis, popup UI, and warning overlays.
- `frontend/` Next.js dashboard for scan history, evidence review, and operational monitoring.
- `backend/` FastAPI API for scan orchestration, persistence, auth-ready boundaries, and job lifecycle.
- `ai-services/` Python inference package and optional standalone AI service.
- `shared/` cross-client schemas and TypeScript contracts.
- `docker/` container definitions.
- `docs/` architecture, API, ML, roadmap, deployment notes.

GhostProof does not claim perfect detection. It combines model outputs, forensic heuristics, metadata, and explainability into risk estimates with evidence.

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

Local services:

- Backend API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- AI service: `http://localhost:8100`
- Dashboard: `http://localhost:3000`

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

Load `extension/dist` as unpacked extension in Chrome.

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

- Replace fallback heuristics with validated model artifacts.
- Add authentication and tenant isolation.
- Add signed model registry and model drift monitoring.
- Add streaming video/audio chunk analysis.
- Add privacy modes: local-only scan, redact-before-upload, and allowlist controls.
- Add adversarial robustness suite and calibration dataset.
