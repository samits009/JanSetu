# JanSetu System Status

This document describes the stabilization-sprint boundary. It is not a Phase 6 plan.

| Area | Status | Current implementation |
| --- | --- | --- |
| Database | REAL | PostgreSQL with async SQLAlchemy and Alembic migrations |
| Eligibility | REAL | Deterministic policy rule engine |
| Evidence | REAL | Persisted documents/evidence and evidence matching service |
| Applications | REAL/MOCK | Persisted state machine; government submission provider is mocked |
| Consent | REAL | Persisted consent records, explicit grant endpoint, high-impact checks |
| Audit | REAL | Persisted citizen and scheme audit events for implemented actions |
| Agent | MOCK/REAL | Tool loop and domain tools are real; API currently uses `MockAIProvider` |
| Government adapters | MOCK | `MockGovernmentApplicationProvider` only |
| Document processing | INCOMPLETE | Document listing is real; upload/OCR/storage contract is not implemented |
| Citizen auth | INCOMPLETE | Frontend uses configured demo citizen UUID |
| Admin auth | MOCK | Development mock token; production mode fails closed without a real provider |
| Scheme ingestion | REAL/MOCK | Deterministic local JSON fixture ingestion is implemented; web/HTML ingestion is incomplete |
| Gemini | INCOMPLETE | Provider abstraction exists; it is not the active agent or ingestion provider |
| Scheme APIs | REAL | Versioned read, refresh, review, publish, source, and audit flows are implemented |

## PostgreSQL connection contract

- Windows host development: `127.0.0.1:5433`
- Backend inside Docker Compose: `db:5432`
- Test database: separate database `jansetu_test` on the configured host port

Credentials are supplied through environment variables and are not documented here.
