# Tutor AI

Multi Agent AI tutoring system with a Python FastAPI backend and a modern React (Vite + TypeScript + Chakra UI) frontend. Generate personalized content, set practice questions, and receive actionable feedback—all in one place.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Plans and Pricing](#plans-and-pricing)
- [Project Structure](#project-structure)
- [Backend (FastAPI)](#backend-fastapi)
	- [Setup](#setup)
	- [Run](#run)
	- [Notable Endpoints](#notable-endpoints)
- [Frontend (React + Vite + TypeScript)](#frontend-react--vite--typescript)
	- [Setup & Run](#setup--run)
- [Usage Flow](#usage-flow)
- [Quotas & Enforcement](#quotas--enforcement)
- [Billing Notes](#billing-notes)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Overview

Tutor AI helps learners create study materials, practice with intelligent question sets, and track progress with feedback and analytics. It includes:

- React frontend (`client/`) for the user experience
- FastAPI backend (`server/`) for APIs, auth, persistence, and billing
- MongoDB storage (via Motor) for users, content, questions, and progress
- Optional Stripe subscriptions for Standard/Premium plans

## Key Features

- Personalized content generation (topics, difficulty, objectives)
- Intelligent question generation (types, distribution, Bloom levels)
- Feedback and scoring for submitted answers
- Progress dashboard and recent activity
- Authentication with JWT
- Plans and quotas (free vs paid) with server-side enforcement
- Billing: Stripe Checkout, Billing Portal, cancel/resume at period end

## Plans and Pricing

| Plan     | Price       | Content Generations | Question Generations | Feedback Evaluations | Notes          |
|----------|-------------|---------------------|----------------------|----------------------|----------------|
| Free     | Free        | 10                  |  —                   | —                    | Basic features |
| Standard | $10/month   | 100                 | 100                  | 100                  | Standard features |
| Premium  | $50/month   | Unlimited           | Unlimited            | Unlimited            | Premium features |

When limits are exceeded or a paid-only feature is accessed on the Free plan, the server returns HTTP 402 (Payment Required). The client intercepts 402 responses and redirects to the Pricing page.

## Project Structure

```
Tutor-AI/
	client/                # React + Vite + TS + Chakra UI frontend
		src/
			pages/             # Pages (Landing, Login, Signup, Dashboard, Content, Questions, Feedback, Progress)
			components/        # Reusable UI (Navbar, PricingPlans, etc.)
			api/               # Axios API client and types
			context/           # Auth context (JWT, plan, usage, subscription)
	server/                # FastAPI backend
		routers/             # Feature routers (auth, content, questions, answers, progress, billing)
		main.py              # App wiring
		config.py            # Environment configuration
		database.py          # Mongo (Motor) connection
		auth.py              # Auth helpers
		schemas.py           # Pydantic models
	agents/                # Multi-agent content/question/feedback logic
	utils/                 # NLP/information retrieval helpers
	database/              # Session management helpers
	requirements.txt       # Python dependencies
```

## Backend (FastAPI)

Prereqs:
- Python 3.10+ (3.11 recommended)
- MongoDB (set `MONGODB_URI`)

### Setup
```powershell
# From repo root
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

# (Optional) Download NLTK data for NLP helpers
python download_nltk_data.py

# Configure environment (create .env at project root)
```

Create a `.env` file at the project root:

```env
MONGODB_URI=mongodb+srv://... (or mongodb://localhost:27017)
MONGODB_DB=tutor_ai
JWT_SECRET=change-me
ALLOWED_ORIGINS=http://localhost:5173

# Optional: AI provider key if used by agents
GEMINI_API_KEY=your_key

# Optional: Stripe billing
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_STANDARD=price_...
STRIPE_PRICE_PREMIUM=price_...
```

### Run
```powershell
uvicorn server.main:app --host 127.0.0.1 --port 8001 --reload
```

### Notable Endpoints
- Auth: `/auth/signup`, `/auth/login`, `/auth/me`, `/auth/profile`
- Content: `/content/generate`, `/content/{id}`
- Questions: `/questions/generate`
- Answers/Feedback: `/answers/submit`
- Progress: `/progress/me`
- Billing:
	- `GET /billing/me` – plan, usage, optional subscription summary
	- `POST /billing/checkout/session` – start Stripe Checkout (price=standard|premium)
	- `POST /billing/confirm` – confirm session in dev (no webhooks)
	- `POST /billing/portal` – open Billing Portal
	- `POST /billing/webhook` – Stripe webhook (prod)
	- `POST /billing/subscription/cancel` – schedule/immediate cancel
	- `POST /billing/subscription/resume` – undo cancel-at-period-end

## Frontend (React + Vite + TypeScript)

Prereqs:
- Node 18+

### Setup & Run
```powershell
cd client
npm install

# Configure client env (client/.env.local)
```

Create `client/.env.local`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8001
VITE_STRIPE_PRICE_STANDARD=price_...  # optional
VITE_STRIPE_PRICE_PREMIUM=price_...   # optional
```

```powershell
npm run dev
```

The dev server runs at http://localhost:5173. If `VITE_API_BASE_URL` is not set, the client can use the dev proxy `/api` configured in Vite.

## Usage Flow

1) Create an account (Signup) and login
2) Generate content (topic, difficulty, objectives)
3) Create question sets for the content
4) Submit answers to receive feedback and scores
5) Track progress on the Dashboard
6) Upgrade to Standard/Premium for higher or unlimited limits

## Quotas & Enforcement

- Free users are limited and certain routes are paid-only
- Server raises HTTP 402 when over quota or for paid-only features
- Client intercepts 402 and redirects to the Pricing page

## Billing Notes

- Development without webhooks: after Stripe Checkout returns to `/dashboard?session_id=...`, the client calls `POST /billing/confirm` to update the plan
- Production: configure `STRIPE_WEBHOOK_SECRET` and point Stripe webhooks to `/billing/webhook`
- Manage/cancel subscription via Billing Portal or the Settings modal (sidebar)

## Security

- JWT-based auth (HS256) with configurable expiry
- CORS origins controlled by `ALLOWED_ORIGINS`

## Troubleshooting

- Backend not starting (exit code 1):
	- Check `.env` values (MongoDB URI, JWT_SECRET)
	- Ensure MongoDB is reachable
	- Verify Python version and that `requirements.txt` is installed
- 402 Payment Required on client:
	- You’ve hit a limit or a paid-only feature on a free plan
	- Upgrade via Pricing or log in as a paid user
- Stripe: "Invalid or unconfigured price":
	- Provide `priceId` from client env, or set server `STRIPE_PRICE_*`


## License

Licensed under the Apache License, Version 2.0. See the `LICENSE` file for details.

