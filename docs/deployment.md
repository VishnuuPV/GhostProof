# Deployment Strategy

## Local

Use Docker Compose for Postgres, Redis, backend, AI service, and dashboard.

## Production

- Backend: stateless FastAPI pods behind API gateway.
- AI service: GPU-enabled worker pool with autoscaling.
- Redis: queue and cache layer.
- Postgres: managed database with point-in-time recovery.
- Object storage: evidence artifacts, frame thumbnails, heatmaps.
- CDN: dashboard static assets.
- Extension: Chrome Web Store package built from `extension/dist`.

## Security Controls

- Validate media size and MIME type before inference.
- Hash media and URLs for deduplication.
- Redact page text in strict privacy mode.
- Use signed scan logs: `previous_hash + report_hash`.
- Disable remote media fetching for restricted tenants.
- Separate public API auth from internal AI service credentials.
