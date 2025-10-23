# 🎓 Tutor AI

An AI tutoring system with a FastAPI backend and a modern React (Vite + TypeScript + Chakra UI) frontend. It creates personalized study content, generates question sets, evaluates answers with feedback, and tracks progress. MongoDB backs the data layer, and optional Atlas Search + Vector Search enables semantic reuse and speed.

## ✨ Why Tutor‑AI (value in one minute)

Most AI study sites stop at “generate notes” or “ask a bot.” Tutor‑AI is built as a full learning workflow: it produces structured lessons, turns them into balanced assessments, evaluates your answers with constructive feedback, and tracks progress—all with privacy controls and aggressive cost/latency optimization.

What makes it more valuable than typical alternatives:
- 📚 **Learn better**: structured lessons (overview → key concepts → examples → applications → tips → summary).
- ✅ **Assess fairly**: Bloom/difficulty‑aware questions; MCQs auto‑normalized to 4 clear options with mapped answers.
- 💡 **Get real feedback**: concise explanations plus optional study suggestions, not just a score.
- 🔒 **Safe, fast, and cost‑smart**: privacy/PII safeguards and semantic reuse that cuts LLM calls; resilient fallbacks.

## Preview

Here’s a quick preview of the dashboard:

![Preview Video](vedio.gif)  

## 📚 Contents

- [For Users](#for-users)
- [Why Tutor‑AI](#why-tutorai-value-in-one-minute)
- [For Developers](#for-developers)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## 👥 For Users

### 🌟 How it's different (at a glance)

- 📖 **Learn with structure, not noise**: generated content is readable, skimmable, and designed for revision.
- 🎯 **Questions fit your goal**: choose types, Bloom levels, and a difficulty mix; we enforce quality on MCQs.
- 🎓 **Feedback that teaches**: beyond correct/incorrect, you get short explanations and optional study tips.
- ⚡ **Quicker results over time**: similar topics reuse cached, verified material to save time and tokens.
- 🔐 **Safer by default**: we detect/ redact PII and moderate unsafe prompts.

### 🚀 What you can do

- ✏️ Create study content tailored to your topic, level, and goals
- ❓ Generate question sets and practice quizzes for the content
- 📝 Submit answers and receive feedback with actionable suggestions
- 📊 Track progress and recent activity on your dashboard
- 💳 Upgrade plans if you reach free limits

### ⚡ Quick start

1) 🌐 Open the site (local dev uses http://localhost:5173 by default)
2) 🔑 Sign up or log in
3) 📝 Go to "Content" and enter a topic (e.g., "Logistic Regression basics"), choose difficulty and objectives, then generate
4) ❓ From the generated content, click "Generate Questions" to get a practice set
5) ✍️ Answer questions in "Questions" or "Content View" and submit for feedback
6) 📈 Visit "Progress" to see scores and history; revisit any content later

**💡 Tips**
- ⚡ If you've generated similar content before, the system may instantly reuse existing results to save time and tokens
- 🚫 If you hit a limit on the free plan, you'll be redirected to Pricing; upgrading unlocks higher quotas
- 👤 Your profile menu (top-right) lets you view plan, usage, and manage billing (if enabled)

**🆘 Support**
- ⚠️ If a screen shows "Payment Required (402)", you're over quota for your current plan
- 🔄 If something looks stuck, refresh the page; your content and results are saved

---

## 👨‍💻 For Developers

This project has two apps:
- **Backend**: FastAPI in `server/` with MongoDB (Motor), JWT auth, and multi-agent logic in `agents/`
- **Frontend**: React + Vite + TypeScript + Chakra UI in `client/`

### 📋 Prerequisites

- 🐍 Python 3.11 (recommended)
- 📦 Node.js 18+ (or 20+)
- 🍃 MongoDB (local or Atlas). Atlas is recommended to enable search + vector features
- 🔑 An API key for the AI provider (Google Gemini) if you'll run generation locally

### 📁 Project structure (high level)

```
Tutor-AI/
  client/                 # React + Vite + TypeScript + Chakra UI
    src/
      pages/              # Landing, Login, Signup, Dashboard, Content, Questions, Feedback, Progress
      components/         # Navbar, PricingPlans, Markdown, Profile modal, etc.
      api/                # Axios client
      context/            # Auth context (JWT, plan, usage)
  server/                 # FastAPI app
    routers/              # auth, content, questions, answers, progress, billing
    main.py               # FastAPI app entry
    config.py             # Env/config flags
    database.py           # Motor client and indices
    auth.py               # JWT helpers
    schemas.py            # Pydantic models
  agents/                 # content_generator, question_setter, feedback_evaluator
  utils/                  # information_retrieval, nlp_processor, security
  database/               # session manager helpers
```

### ⚙️ Environment configuration

Create a `.env` at the repo root:

```env
# Mongo
MONGODB_URI=mongodb+srv://<user>:<pass>@cluster0.xxxx.mongodb.net
MONGODB_DB=tutor_ai

# CORS and auth
ALLOWED_ORIGINS=http://localhost:5173
JWT_SECRET=change-me

# AI provider (Gemini)
GEMINI_API_KEY=your_gemini_key

# Optional: Atlas Search + Vector Search
ATLAS_SEARCH_ENABLED=true
ATLAS_SEARCH_INDEX=default

# Optional: Stripe billing (dev/prod as needed)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_PRICE_STANDARD=price_...
STRIPE_PRICE_PREMIUM=price_...
```

For the client, create `client/.env.local`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8001
# Optional display-only price IDs
VITE_STRIPE_PRICE_STANDARD=price_...
VITE_STRIPE_PRICE_PREMIUM=price_...
```

### 🚀 Backend setup and run (Windows PowerShell)

```powershell
# From repo root
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

# (Optional) Download NLTK datasets used by NLP helpers
python download_nltk_data.py

# Start FastAPI (reload for dev)
uvicorn server.main:app --host 127.0.0.1 --port 8001 --reload
```

📖 API docs (OpenAPI/Swagger) are at: http://127.0.0.1:8001/docs

**🔗 Key endpoints**
- 🔐 Auth: `POST /auth/signup`, `POST /auth/login`, `GET /auth/me`
- 📝 Content: `POST /content/generate`, `GET /content/{id}`
- ❓ Questions: `POST /questions/generate`
- ✍️ Answers/Feedback: `POST /answers/submit`
- 📊 Progress: `GET /progress/me`
- 💳 Billing: `GET /billing/me`, `POST /billing/checkout/session`, `POST /billing/confirm`, `POST /billing/portal`,
  `POST /billing/webhook`, `POST /billing/subscription/cancel`, `POST /billing/subscription/resume`

### 🎨 Frontend setup and run

```powershell
cd client
npm install
npm run dev
```

The app starts at http://localhost:5173. Ensure `VITE_API_BASE_URL` points to your backend base URL.

### 🔍 Notes on search, vectors, and caching

- Atlas Search + Vector Search (if `ATLAS_SEARCH_ENABLED=true`) is used to reuse similar content and question sets across users.
- On cache writes, content embeddings are stored; a backfill utility exists to add embeddings for old records: `utils/backfill_embeddings.py`.
- Global caches:
  - `generated_content` for study materials
  - `generated_questions` for question sets
- The backend attempts:
  1) Exact cache hit (by hash/parameters)
  2) Similar cache hit (semantic candidates via Atlas + IR blend)
  3) Generate and persist

#### 💎 Why this matters to you

- ⚡ **Faster answers**: repeated or similar topics return instantly from cache.
- 💰 **Lower cost**: fewer LLM calls for teams/classes working on overlapping material.
- ✅ **Higher quality**: semantic candidates are re‑ranked with TF‑IDF cosine and token Jaccard to avoid wrong matches.

### 🔒 Responsible AI and safety (overview)

- ✔️ Input validation and basic moderation
- 🔐 PII detection/redaction paths in NLP modules
- ⚙️ Configurable privacy modes and CORS origins
- 🎯 Deterministic parsing for question generation (natural responses with robust parsing)

### 🚀 Deployment (brief)

- 🌐 Use environment variables above
- 🔧 Expose FastAPI behind a reverse proxy (e.g., Nginx) and serve the frontend build (`npm run build` in `client/`)
- 🔍 Configure Atlas Search index name via `ATLAS_SEARCH_INDEX`
- 💳 Configure Stripe webhooks to point to `/billing/webhook` in production

---

## 🛠️ Troubleshooting

**❌ Backend won't start**
- Check `.env` values (MongoDB URI/DB, JWT_SECRET)
- Ensure MongoDB is reachable and the user has permissions
- Verify Python 3.11+ and that `pip install -r requirements.txt` succeeded

**🔐 401/403 errors**
- Ensure the client includes the JWT in Authorization header and that CORS is set via `ALLOWED_ORIGINS`

**💳 402 Payment Required (client toast and redirect)**
- You've reached plan limits; switch account or upgrade through Pricing

**🐌 Slow or repeated generations**
- Atlas Search + Vector Search can be enabled to semantically reuse prior results: set `ATLAS_SEARCH_ENABLED=true`

**💰 Stripe price errors**
- Ensure `STRIPE_PRICE_*` values exist (server) or `VITE_STRIPE_PRICE_*` (client) if displayed on UI

---

## 📄 License

Licensed under the Apache License, Version 2.0. See the `LICENSE` file for details.

