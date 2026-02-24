# Vercel Deployment Guide

## Quick Deploy

### Option 1: Vercel Dashboard (Easiest)

1. **Go to [vercel.com](https://vercel.com) and sign in**

2. **Import Project:**
   - Click "Add New..." → "Project"
   - Import your GitHub repository: `course-companion-fte-hackathon-iv`
   - Framework Preset: `Next.js` (auto-detected)
   - Root Directory: `src/web-frontend`
   - Click "Deploy"

3. **Configure Environment Variables:**
   Go to Settings → Environment Variables → Add:
   ```
   NEXT_PUBLIC_API_BASE_URL = https://your-backend.onrender.com/api
   NEXT_PUBLIC_MCP_PROXY_URL = https://your-backend.onrender.com/api/v3/mcp
   ```

4. **Redeploy** (if env vars added after first deploy)

### Option 2: Vercel CLI

```bash
# Login to Vercel
cd src/web-frontend
vercel login

# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

## Environment Variables

| Variable | Value | Required |
|----------|-------|----------|
| `NEXT_PUBLIC_API_BASE_URL` | Your Render backend URL | ✅ |
| `NEXT_PUBLIC_MCP_PROXY_URL` | Your Render backend MCP URL | Optional |
| `NEXT_PUBLIC_AUTH_ENABLED` | `true` | Optional |

## Build Settings

- **Framework:** Next.js 14 (auto-detected)
- **Build Command:** `npm run build`
- **Output Directory:** `.next`
- **Install Command:** `npm install`
- **Node Version:** 18.x

## Post-Deployment

### 1. Update Backend CORS

Add your Vercel URL to backend CORS:

```bash
# In Render dashboard → Environment
CORS_ORIGINS=["https://your-app.vercel.app","https://chat.openai.com"]
```

### 2. Verify Deployment

```bash
# Homepage
curl https://your-app.vercel.app

# Modules page
curl https://your-app.vercel.app/modules

# Chapters page
curl https://your-app.vercel.app/chapters
```

### 3. Test API Connection

Open browser console on your Vercel app and check for API calls to your Render backend.

## Custom Domain (Optional)

1. Go to Settings → Domains
2. Add your domain
3. Configure DNS as instructed
4. SSL is automatic

## Pricing

| Plan | Cost | Features |
|------|------|----------|
| Hobby | $0 | Unlimited deployments, 100GB bandwidth |
| Pro | $20/month | More bandwidth, analytics |

## Troubleshooting

### Build Fails
```bash
# Test build locally
npm run build

# Check Node version
node --version  # Should be 18+
```

### API Calls Fail
- Verify `NEXT_PUBLIC_API_BASE_URL` is set correctly
- Check backend CORS includes your Vercel URL
- Ensure backend is deployed and healthy

### 404 on Pages
- Verify Root Directory is `src/web-frontend`
- Check `next.config.js` exists

## Preview Deployments

Every push to a branch creates a preview:

```bash
# Push feature branch
git push origin feature/my-feature

# Vercel creates preview at:
# https://course-companion-<hash>.vercel.app
```

## Support

- [Vercel Docs](https://vercel.com/docs)
- [Next.js Deployment](https://vercel.com/docs/frameworks/nextjs)
