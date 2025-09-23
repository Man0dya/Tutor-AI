# Quickstart

1. Install Node.js 18+ (https://nodejs.org/)
2. In a terminal at `client/`, run:

```
npm install
npm run dev
```

3. Backend: ensure FastAPI is running at `http://127.0.0.1:8000`.
4. Open http://127.0.0.1:5173 in your browser.

If your backend runs elsewhere, create a `.env` file in `client/`:

```
VITE_API_BASE_URL=http://127.0.0.1:8000
```
