# JanSetu MVP

JanSetu is a mobile-first welfare continuity agent prototype based on the Stitch-generated UI supplied for the project.

## What is functional in this MVP

- Responsive PWA-style shell
- Home / Welfare Command Center
- Benefit portfolio and detail views
- Benefit survival / migration view
- Document and evidence inventory
- Demo document-processing interaction
- Application Autopilot
- Closed-loop rejection recovery
- Consent-oriented trust center
- Hindi-first microcopy with English support labels
- Client-side state transitions between the core flows

## Demo flow

1. Open Home.
2. Click **Let JanSetu Handle It**.
3. Open **Application Autopilot**.
4. Review the simulated government response.
5. Click **Approve & Resubmit**.
6. See the recovery workflow move to `resubmitted`.
7. Open Documents and upload the demo school certificate.
8. Return to Benefits and inspect evidence coverage.

## Run locally

Requirements:

- Node.js 20+
- npm 10+

```bash
npm install
npm run dev
```

Then open the local Vite URL shown in the terminal.

## Production roadmap

This repository intentionally separates the UI and domain logic so real adapters can replace mock behavior.

Next backend layers should include:

- PostgreSQL for users, households, documents, benefits and applications
- Object storage for encrypted documents
- A deterministic eligibility/rules engine
- Scheme and policy ingestion pipeline
- Government API adapters
- Browser automation adapters for legacy portals
- Consent + audit service
- Event-driven application state machine
- Notification service
- Multilingual speech pipeline
- LLM agent orchestration layer

The LLM should extract/plan/explain. It should not be the authoritative eligibility engine.
