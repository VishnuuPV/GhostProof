# GhostProof Product Spec

## 1. Full Project Architecture

GhostProof is a monorepo with separate browser, dashboard, backend, AI, shared schema, docs, and Docker boundaries.

Runtime path:

1. Content script discovers page media.
2. Extension background worker submits scan request.
3. Backend validates and orchestrates inference.
4. AI service runs modality pipeline.
5. Risk engine combines scores.
6. Explainability engine emits evidence.
7. Extension overlays badge and popup history.
8. Dashboard reads persistent scan history.

## 2. Folder Structure

```text
/extension     Chrome MV3 scanner and popup
/frontend      Next.js security dashboard
/backend       FastAPI API, jobs, persistence
/ai-services   inference pipelines and AI service
/models        future model artifacts
/shared        schemas, TypeScript contracts, sample payloads
/docker        container builds
/docs          architecture, API, deployment, roadmap
```

## 3. Backend API Design

- `POST /api/v1/analyze`: immediate scan for browser extension and dashboard tests.
- `POST /api/v1/jobs`: async scan for heavy video/audio.
- `GET /api/v1/jobs/{job_id}`: job lifecycle.
- `GET /api/v1/history`: scan records for dashboard.
- `GET /api/v1/health`: API and AI-service status.

## 4. Database Schema

`scan_records`:

- scan ID primary key
- media type
- risk level
- authenticity score
- AI probability
- confidence
- summary
- source URL
- content hash
- report JSON
- previous hash
- tamper hash
- created timestamp

## 5. Frontend Component Structure

- `RiskGauge`: aggregate synthetic risk and confidence.
- `StatCard`: security metric tiles.
- `EvidencePanel`: explainability queue.
- `ModalityMatrix`: image/video/audio/text coverage.
- `ScanTimeline`: chronological scan history.

## 6. Browser Extension Structure

- `content/mediaExtractor.ts`: DOM discovery.
- `content/overlay.ts`: warning badge and evidence drawer.
- `background/index.ts`: context menu, API calls, storage.
- `popup/Popup.tsx`: extension status and scan history.
- `public/manifest.json`: Manifest V3 permissions and scripts.

## 7. AI Pipeline Architecture

Each pipeline implements `BasePipeline.analyze(input) -> ModalityResult`.

- Image: metadata, dimensions, optional pixel frequency analysis.
- Video: temporal instability, lip-sync, face-warp hooks.
- Audio: harmonics, prosody, speaker mismatch hooks.
- Text: entropy, burstiness, repetition, predictability.

## 8. Risk Scoring Logic

`RiskScorer` uses weighted modality probability and confidence. Video and audio get stronger weights because manipulation harm is often higher. Confidence affects final risk level so metadata-only scans do not overclaim.

## 9. Explainability Workflow

Pipelines emit structured `Evidence` with:

- code
- title
- description
- modality
- severity
- location
- recommendation

`ExplanationEngine` ranks evidence and creates human-readable summary. UI never returns only "fake"; it shows reasons and confidence.

## 10. Suggested ML Models

See `docs/ml-models.md`.

Short list:

- EfficientNet/ConvNeXt forensic image classifier.
- Frequency-domain GAN/diffusion artifact classifier.
- TimeSformer/X3D video temporal classifier.
- SyncNet-style lip-sync comparison.
- wav2vec2/RawNet2 spoofing classifier.
- RoBERTa/DeBERTa text classifier with calibration.

## 11. Deployment Strategy

Docker Compose runs Postgres, Redis, backend, AI service, and dashboard. Production should split API and inference workers, add object storage for evidence assets, and deploy GPU pools for heavy modalities.

## 12. Docker Setup

- `docker/backend.Dockerfile`
- `docker/ai-service.Dockerfile`
- `docker/frontend.Dockerfile`
- `docker-compose.yml`

## 13. Development Roadmap

See `docs/roadmap.md`.

Primary track:

- MVP heuristic inference.
- ONNX/Torch model integration.
- tenant auth and privacy controls.
- streaming inference and GPU scale.
- drift monitoring and human review.

## 14. MVP Scope

Included:

- Browser scan flow.
- REST scan API.
- modular modality pipelines.
- risk engine.
- explainability objects.
- dashboard.
- persistence model.
- Docker stack.

Excluded until model phase:

- accuracy claims.
- production model artifacts.
- real facial landmark extraction.
- full waveform/video upload pipeline.

## 15. Production Scalability Recommendations

- Use signed model registry.
- Queue heavy jobs through Redis/Celery or Kafka.
- Cache by media hash.
- Store heatmaps and frame thumbnails in object storage.
- Add rate limits and tenant policies.
- Calibrate thresholds per content domain.
- Add false-positive review loop.
- Add local-only extension inference for privacy-sensitive tenants.
