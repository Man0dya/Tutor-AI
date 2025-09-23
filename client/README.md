# Tutor AI - React Frontend

## Dev

- Install Node.js 18+
- Install deps

```
npm install
```

- Start dev server

```
npm run dev
```

Backend assumed at `http://127.0.0.1:8000`. During dev, calls to `/api/*` are proxied to FastAPI.

Configure a custom API URL by creating `.env` with:

```
VITE_API_BASE_URL=http://127.0.0.1:8000
```
