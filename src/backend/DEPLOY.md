# Railway Deployment Guide

## Course Companion Backend - Zero-Backend-LLM Architecture

### Prerequisites

- [Railway CLI](https://docs.railway.app/develop/cli) installed
- Railway account (sign up at https://railway.app)
- GitHub repository connected to Railway (recommended)

---

## Quick Deploy Steps

### 1. Install Railway CLI

```bash
# macOS/Linux
curl -fsSL https://railway.app/install.sh | sh

# Or with npm
npm install -g @railway/cli
```

### 2. Login to Railway

```bash
railway login
```

### 3. Initialize Project

```bash
cd src/backend
railway init
```

Select "Empty Project" when prompted.

### 4. Add PostgreSQL Database

```bash
railway add
```

Select **PostgreSQL** from the list of plugins.

### 5. Set Environment Variables

```bash
# Required variables
railway variables set APP_ENV=production
railway variables set DEBUG=false
railway variables set SECRET_KEY=$(openssl rand -hex 32)
railway variables set JWT_SECRET_KEY=$(openssl rand -hex 32)

# R2 Storage (get these from Cloudflare dashboard)
railway variables set R2_ENDPOINT=https://your-account-id.r2.cloudflarestorage.com
railway variables set R2_ACCESS_KEY=your-access-key
railway variables set R2_SECRET_KEY=your-secret-key
railway variables set R2_BUCKET_NAME=course-companion-content

# CORS (add your frontend URL)
railway variables set CORS_ORIGINS='["https://chat.openai.com","https://your-frontend.railway.app"]'
```

**Note:** `DATABASE_URL` is automatically set by Railway when you add PostgreSQL.

### 6. Deploy

```bash
railway up
```

Or connect to GitHub for automatic deploys:

```bash
railway link
```

Then push to your repository - Railway will auto-deploy.

### 7. Initialize Database

After deployment, run the database initialization:

```bash
railway run python -m scripts.init_db
```

### 8. Get Your API URL

```bash
railway open
```

Your API will be available at: `https://your-project.railway.app`

---

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Auto | Set by Railway PostgreSQL addon |
| `SECRET_KEY` | Yes | App encryption key |
| `JWT_SECRET_KEY` | Yes | JWT token signing key |
| `R2_ENDPOINT` | Yes | Cloudflare R2 endpoint URL |
| `R2_ACCESS_KEY` | Yes | R2 access key |
| `R2_SECRET_KEY` | Yes | R2 secret key |
| `R2_BUCKET_NAME` | Yes | R2 bucket name |
| `APP_ENV` | No | `development` or `production` |
| `DEBUG` | No | `true` or `false` |
| `CORS_ORIGINS` | No | JSON array of allowed origins |
| `REDIS_URL` | No | Redis URL for caching |

---

## Verify Deployment

### Health Check

```bash
curl https://your-project.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "app": "course-companion",
  "version": "1.0.0",
  "environment": "production",
  "constitutional_compliance": {
    "zero_backend_llm": true,
    "content_verbatim": true,
    "deterministic_only": true
  }
}
```

### API Documentation

Visit: `https://your-project.railway.app/docs`

### ChatGPT Plugin Manifest

Visit: `https://your-project.railway.app/.well-known/ai-plugin.json`

---

## Troubleshooting

### Database Connection Issues

If you see connection errors, verify:

1. PostgreSQL addon is active: `railway status`
2. DATABASE_URL is set: `railway variables`
3. The URL format is correct (Railway auto-converts it)

### View Logs

```bash
railway logs
```

### Restart Service

```bash
railway restart
```

### Check Service Status

```bash
railway status
```

---

## Cost Estimate

Railway Pricing (as of 2024):
- **Hobby Plan**: $5/month (includes $5 credit)
- **PostgreSQL**: ~$0.000231/hour (~$0.17/month for small instance)
- **Compute**: ~$0.000463/vCPU/minute

**Estimated Monthly Cost**: $5-10 for low traffic

---

## Production Checklist

- [ ] Set strong `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Configure Cloudflare R2 with course content
- [ ] Set `APP_ENV=production` and `DEBUG=false`
- [ ] Configure CORS for your frontend domains
- [ ] Set up monitoring/alerting (Railway dashboard)
- [ ] Enable auto-deploys from GitHub
- [ ] Test all API endpoints
- [ ] Verify ChatGPT plugin manifest
