# Migrations

Production deployment should replace `Base.metadata.create_all` with Alembic.

Initial schema:

- `scan_records`
  - immutable scan ID
  - modality, risk level, score, confidence
  - JSON report
  - content hash
  - previous hash
  - tamper hash
  - created timestamp
