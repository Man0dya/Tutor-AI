# Contributing to Tutor-AI

Thanks for your interest in contributing! This guide explains how to set up the project, propose changes, and submit pull requests.

## Project Stack

- Frontend: React (Vite + TypeScript + Chakra UI)
- Backend: FastAPI (Python), MongoDB (Motor), JWT auth, optional Stripe billing

## Prerequisites

- Node.js 18+ and npm (recommended)
- Python 3.11+ (recommended)
- MongoDB connection URI (Atlas or local)
- Optional: Stripe test keys for billing flows

## Local Setup

### Backend

1) Create and activate a virtual environment (PowerShell):

```
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install Python dependencies:

```
pip install --upgrade pip
pip install -r requirements.txt
```

3) Create `.env` at repo root:

```
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=tutor_ai
JWT_SECRET=change-me
ALLOWED_ORIGINS=http://localhost:5173

# Optional: Stripe billing (dev/testing)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_STANDARD=price_...
STRIPE_PRICE_PREMIUM=price_...
```

4) Run the API:

```
uvicorn server.main:app --host 127.0.0.1 --port 8001 --reload
```

### Frontend

1) Install deps:

```
cd client
npm install
```

2) Create `client/.env.local`:

```
VITE_API_BASE_URL=http://127.0.0.1:8001
VITE_STRIPE_PRICE_STANDARD=price_...  # optional
VITE_STRIPE_PRICE_PREMIUM=price_...   # optional
```

3) Start the dev server:

```
npm run dev
```

Open http://localhost:5173

## Branching & Commits

- Base branch: `Manodya-New`
- Use descriptive branch names: `feat/billing-portal`, `fix/quota-check`, `docs/readme-polish`
- Commit style: Conventional Commits
  - `feat: add premium plan badge`
  - `fix: prevent 402 redirect loop on refresh`
  - `docs: update setup steps for Windows`

## Pull Requests

- Link issues with “Closes #123” when applicable
- Include a brief summary, rationale, and test notes
- Add screenshots/GIFs for UI changes
- Keep PRs focused and reasonably small

### PR Checklist

- [ ] Builds locally (client + server)
- [ ] No new TypeScript errors (client)
- [ ] Main flows tested manually (login, content, questions, feedback)
- [ ] 402 handling verified (redirects to Pricing when appropriate)
- [ ] Docs updated if needed (README/ARCHITECTURE)
- [ ] No secrets in code/logs or screenshots

## Code Style & Conventions

### Frontend (TypeScript/React)

- Functional components and hooks
- Strongly type props/state; avoid `any`
- UI via Chakra UI; keep custom CSS minimal (`client/src/styles.css`)
- Shared UI in `client/src/components/`; pages in `client/src/pages/`
- API calls via `client/src/api/client.ts`; intercept 402 to redirect to Pricing

### Backend (Python/FastAPI)

- Feature routers in `server/routers/*`
- Pydantic models in `server/schemas.py`
- Enforce quotas server-side; use HTTP 402 for payment-required cases
- Return clear error messages; prefer explicit schemas over raw dicts
- Health endpoint `/health` should not crash when DB is down; indicate status instead

## Reporting Issues

- Use the Bug report template for defects; include steps, expected/actual behavior, environment info, and relevant logs (redact secrets)
- Use the Feature request template for enhancements; explain the problem and proposed solution

## Security

Please do not file public issues for security vulnerabilities. Email the maintainers as described in `SECURITY.md`.

## Code of Conduct

Participation in this project is governed by the [Code of Conduct](./CODE_OF_CONDUCT.md).

## License

By contributing, you agree that your contributions will be licensed under the Apache-2.0 License (see `LICENSE`).
