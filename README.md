# AI Tutoring System

A Streamlit-based multi-agent tutoring app with content generation, question setting, feedback evaluation, and knowledge-base search.

## Prereqs
- Python 3.10 or 3.11 (recommended)
- A Google Generative AI API key in the env var `GEMINI_API_KEY` (for content/questions/feedback). If not set, parts of the app will fall back to simple heuristics but AI features may fail.

## Setup
```powershell
# From the repo root
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

# Download NLTK data (one-time)
python download_nltk_data.py

# Set your API key for this session (or use a .env file)
$env:GEMINI_API_KEY = "<your_api_key_here>"
```

Optionally create a `.env` file in the project root:
```
GEMINI_API_KEY=<your_api_key_here>
```




## Run
```powershell
streamlit run app.py
```

The app will start on http://localhost:8501 (or the port configured in `.streamlit/config.toml`).

## Notes
- Data persists under `data/sessions` as JSON files.
- If you see NLTK lookup errors (e.g., `punkt`), re-run `python download_nltk_data.py`.
- If Google API calls fail, ensure `google-genai` is installed and `GEMINI_API_KEY` is set.


## FastAPI backend (React client)

This repo also includes a FastAPI backend under `server/` and a React client under `client/`.

Run the API locally:

```powershell
cd server
uvicorn server.main:app --host 127.0.0.1 --port 8001 --reload
```

Run the React client:

```powershell
cd client
npm install
npm run dev
```

The client expects `VITE_API_BASE_URL` (e.g., `http://127.0.0.1:8001`). In dev, you can either:
1) Set `VITE_API_BASE_URL=http://127.0.0.1:8001` in `client/.env.local`, or
2) Use the Vite proxy at `/api` (already configured) and call the API with a base URL of `/api`.

### Plans and limits

- New users start on plan `free`.
- Free plan: up to 10 content generations per month.
- Questions generation and feedback evaluation require a paid plan (`standard` or `premium`).

### Optional: Stripe billing

Set these environment variables (e.g., in `.env`) to enable Stripe subscription checkout and webhooks:

```
STRIPE_SECRET_KEY=sk_live_or_test
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_STANDARD=price_...
STRIPE_PRICE_PREMIUM=price_...
```

Dev flow without webhooks: the server also exposes `POST /billing/confirm` which accepts `{ session_id }` and will verify the Checkout Session and update the user's plan. The React client will call this automatically when you land back on `/dashboard?session=success&session_id=...`.

Optionally, you can provide Stripe price IDs from the client-side env (useful if you don't want to set price IDs on the server):

```
# client/.env.local
VITE_STRIPE_PRICE_STANDARD=price_...
VITE_STRIPE_PRICE_PREMIUM=price_...
VITE_API_BASE_URL=http://127.0.0.1:8001
```

If both server-side `STRIPE_PRICE_*` and client-side `VITE_STRIPE_PRICE_*` are set, the client will pass its price ID explicitly and the server will accept it.

Endpoints:

- `GET /billing/me` – get current plan and usage
- `POST /billing/checkout/session` – create a checkout session (`{ price: "standard" | "premium" }`)
- `POST /billing/portal` – open the customer billing portal
- `POST /billing/webhook` – Stripe webhook to update user plan (configure in Stripe dashboard)
- `GET /billing/prices` – dev helper to list active Stripe Price IDs you can use

If you see a 400 with message "Invalid or unconfigured price":
- Provide `priceId` explicitly when calling `/billing/checkout/session`, or
- Set server envs `STRIPE_PRICE_STANDARD` / `STRIPE_PRICE_PREMIUM`, or
- Set client envs `VITE_STRIPE_PRICE_STANDARD` / `VITE_STRIPE_PRICE_PREMIUM` (the client will pass `priceId`).

