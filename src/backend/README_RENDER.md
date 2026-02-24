# Render Deployment Guide

## Quick Deploy

### Option 1: Render Dashboard (Recommended)

1. **Go to [render.com](https://render.com) and sign in**

2. **Create a new Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select repository: `course-companion-fte-hackathon-iv`
   - Root Directory: `src/backend`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Configure Environment Variables:**
   ```
   APP_ENV=production
   DEBUG=false
   SECRET_KEY=<generate-random>
   JWT_SECRET_KEY=<generate-random>
   CONTENT_STORAGE_MODE=local
   CONTENT_DIR=/opt/render/project/src/sample-content
   CORS_ORIGINS=["https://your-vercel-app.vercel.app","https://chat.openai.com"]
   ```

4. **Add PostgreSQL Database:**
   - Click "New +" → "PostgreSQL"
   - Name: `course-companion-db`
   - Copy the internal database URL
   - Add to web service env vars as `DATABASE_URL`

5. **Deploy:**
   - Click "Create Web Service"
   - Wait for build and deployment
   - Initialize database: `render run python -m scripts.init_db`

### Option 2: Render CLI (Infrastructure as Code)

```bash
# Install Render CLI
npm install -g @render-cloud/cli

# Login
render login

# Deploy using render.yaml
cd src/backend
render up
```

## Environment Variables

| Variable | Value | Notes |
|----------|-------|-------|
| `APP_ENV` | `production` | Required |
| `DEBUG` | `false` | Required |
| `SECRET_KEY` | Auto-generate | Use Render's generateValue |
| `JWT_SECRET_KEY` | Auto-generate | Use Render's generateValue |
| `CONTENT_STORAGE_MODE` | `local` | Use local filesystem |
| `CONTENT_DIR` | `/opt/render/project/src/sample-content` | Render path |
| `CORS_ORIGINS` | Your frontend URL | Add Vercel URL after deploy |
| `DATABASE_URL` | From PostgreSQL | Auto-injected if using render.yaml |

## Post-Deployment

### 1. Initialize Database
```bash
# In Render dashboard → Shell
python -m scripts.init_db
```

### 2. Verify Deployment
```bash
# Health check
curl https://your-app.onrender.com/health

# API docs
curl https://your-app.onrender.com/docs

# List modules
curl https://your-app.onrender.com/api/v1/modules
```

### 3. Update Frontend
Update `.env.local` in web-frontend:
```env
NEXT_PUBLIC_API_BASE_URL=https://your-app.onrender.com/api
```

## Pricing

| Resource | Plan | Cost |
|----------|------|------|
| Web Service | Starter | $7/month |
| PostgreSQL | Starter | $7/month |
| **Total** | | **~$14/month** |

## Troubleshooting

### Build Fails
- Check `requirements.txt` is in `src/backend/`
- Verify Python version is 3.11

### Database Connection Error
- Ensure DATABASE_URL is set
- Check database is in same region

### CORS Errors
- Add frontend URL to CORS_ORIGINS
- Format: `["https://app.vercel.app"]`

## Support

- [Render Docs](https://render.com/docs)
- [Python Services](https://render.com/docs/python)
- [PostgreSQL](https://render.com/docs/postgresql)
