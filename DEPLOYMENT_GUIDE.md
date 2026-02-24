# Complete Deployment Guide

Deploy backend to Render and frontend to Vercel in ~15 minutes.

---

## Overview

| Component | Platform | Cost | Time |
|-----------|----------|------|------|
| Backend API | Render | $14/month | 10 min |
| Frontend Web | Vercel | $0 (Hobby) | 5 min |
| Database | Render PostgreSQL | Included | Auto |

---

## Prerequisites

- GitHub account with repository pushed
- [Render](https://render.com) account (free)
- [Vercel](https://vercel.com) account (free)

---

## Step 1: Deploy Backend to Render

### 1.1 Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub (recommended) or email

### 1.2 Create Web Service

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub account
3. Select repository: `course-companion-fte-hackathon-iv`
4. Configure:
   - **Name:** `course-companion-api`
   - **Root Directory:** `src/backend`
   - **Runtime:** `Python 3`
   - **Region:** `Oregon` (or closest to you)
   - **Plan:** `Starter` ($7/month)
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 1.3 Create Database

1. Click **"New +"** → **"PostgreSQL"**
2. Configure:
   - **Name:** `course-companion-db`
   - **Region:** Same as web service
   - **Plan:** `Starter` ($7/month)
3. Click **"Create Database"**
4. Wait for database to be ready (~2 minutes)

### 1.4 Connect Database to Web Service

1. Go to your web service dashboard
2. Click **"Environment"** tab
3. Click **"Add From Database"**
4. Select `course-companion-db`
5. This auto-adds `DATABASE_URL`

### 1.5 Add Environment Variables

In Render dashboard → Environment, add:

| Key | Value |
|-----|-------|
| `APP_ENV` | `production` |
| `DEBUG` | `false` |
| `SECRET_KEY` | Click "Generate" |
| `JWT_SECRET_KEY` | Click "Generate" |
| `CONTENT_STORAGE_MODE` | `local` |
| `CONTENT_DIR` | `/opt/render/project/src/sample-content` |
| `CORS_ORIGINS` | `["https://chat.openai.com"]` (update after Vercel deploy) |

### 1.6 Deploy

1. Click **"Create Web Service"**
2. Wait for build (~5 minutes)
3. Copy your backend URL: `https://course-companion-api-xxxx.onrender.com`

### 1.7 Initialize Database

1. In Render dashboard, click **"Shell"** tab
2. Run:
   ```bash
   python -m scripts.init_db
   ```
3. Verify success message

### 1.8 Verify Backend

```bash
# Health check
curl https://your-backend.onrender.com/health

# List modules
curl https://your-backend.onrender.com/api/v1/modules

# API docs
open https://your-backend.onrender.com/docs
```

---

## Step 2: Deploy Frontend to Vercel

### 2.1 Create Vercel Account
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub (recommended)

### 2.2 Import Project

1. Click **"Add New..."** → **"Project"**
2. Find and import: `course-companion-fte-hackathon-iv`
3. Click **"Import"**

### 2.3 Configure Build

- **Framework Preset:** Next.js (auto-detected)
- **Root Directory:** `src/web-frontend`
- **Build Command:** `npm run build`
- **Output Directory:** `.next`

### 2.4 Set Environment Variables

Click **"Environment Variables"** → Add:

| Key | Value |
|-----|-------|
| `NEXT_PUBLIC_API_BASE_URL` | `https://your-backend.onrender.com/api` |
| `NEXT_PUBLIC_MCP_PROXY_URL` | `https://your-backend.onrender.com/api/v3/mcp` |

### 2.5 Deploy

1. Click **"Deploy"**
2. Wait for build (~3 minutes)
3. Copy your frontend URL: `https://course-companion-xxxx.vercel.app`

---

## Step 3: Connect Frontend to Backend

### 3.1 Update Backend CORS

1. Go to Render dashboard → Your web service → **Environment**
2. Edit `CORS_ORIGINS`:
   ```
   ["https://chat.openai.com","https://your-app.vercel.app"]
   ```
3. Click **"Save Changes"**
4. Service will auto-redeploy (~1 minute)

### 3.2 Test Integration

1. Open your Vercel app: `https://your-app.vercel.app`
2. Navigate to **Modules** page
3. Should see 3 modules loaded from backend
4. Navigate to **Chapters** page
5. Should see 9 chapters loaded from backend

---

## Verification Checklist

### Backend (Render)
- [ ] Health endpoint returns healthy: `/health`
- [ ] API docs load: `/docs`
- [ ] Modules endpoint returns data: `/api/v1/modules`
- [ ] Chapters endpoint returns data: `/api/v1/chapters`
- [ ] Database initialized successfully

### Frontend (Vercel)
- [ ] Homepage loads without errors
- [ ] Modules page shows 3 modules
- [ ] Chapters page shows 9 chapters
- [ ] Chapter detail pages render content
- [ ] No CORS errors in browser console

---

## Cost Summary

| Resource | Platform | Plan | Monthly Cost |
|----------|----------|------|--------------|
| Web Service | Render | Starter | $7 |
| PostgreSQL | Render | Starter | $7 |
| Web App | Vercel | Hobby | $0 |
| **Total** | | | **$14/month** |

---

## Troubleshooting

### Backend Issues

**Build fails:**
```
# Check logs in Render dashboard → Logs
# Verify requirements.txt exists in src/backend/
```

**Database connection error:**
```
# Ensure DATABASE_URL is set in Environment
# Check database is in same region as web service
```

**500 errors:**
```
# Check Logs tab for error messages
# Verify all environment variables are set
```

### Frontend Issues

**Build fails:**
```bash
# Test locally
cd src/web-frontend
npm run build
```

**API calls fail:**
- Check `NEXT_PUBLIC_API_BASE_URL` is correct
- Verify backend CORS includes Vercel URL
- Check backend is healthy

**404 on pages:**
- Verify Root Directory is `src/web-frontend`
- Check vercel.json exists

---

## Custom Domain (Optional)

### Render Backend
1. Settings → Custom Domain
2. Add your domain
3. Configure DNS (CNAME)
4. SSL is automatic

### Vercel Frontend
1. Settings → Domains
2. Add your domain
3. Configure DNS (A/CNAME records)
4. SSL is automatic

---

## Monitoring

### Render
- **Logs:** Real-time application logs
- **Health:** Automatic health checks
- **Metrics:** CPU, memory, request count

### Vercel
- **Deployments:** Build logs and status
- **Analytics:** (Pro plan) visitor insights
- **Speed:** Automatic performance monitoring

---

## Next Steps

1. **Test all features:** Browse chapters, mark complete, etc.
2. **Share with users:** Distribute your Vercel URL
3. **Monitor usage:** Check Render and Vercel dashboards
4. **Iterate:** Push to GitHub for automatic redeployments

---

## Support

- **Render:** [docs.render.com](https://docs.render.com)
- **Vercel:** [vercel.com/docs](https://vercel.com/docs)
- **Project Issues:** Check GitHub repository

---

**Deployment Time:** ~15 minutes  
**Total Cost:** $14/month  
**Status:** Production-ready ✅
