# Course Companion - Quick Start Guide

Get up and running in 5 minutes!

## Prerequisites
- Node.js 18+
- Python 3.11+

## Quick Start

### 1. Start Backend
```bash
cd src/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Start Frontend (new terminal)
```bash
cd src/web-frontend
npm install
npm run dev
```

### 3. Verify
- Frontend: http://localhost:3000
- Backend: http://localhost:8000/health
- API Docs: http://localhost:8000/docs

## What's Included
- 9 complete chapters
- Real backend API integration
- Responsive web app
- Zero-Backend-LLM compliant
