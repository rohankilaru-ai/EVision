# EVision Deployment Guide

This guide will help you deploy EVision to the cloud so you can access it from anywhere.

## Quick Deploy (Recommended)

### Option 1: Deploy to Vercel (Frontend) + Render (Backend)

**Frontend - Vercel (Free)**

1. Go to [vercel.com](https://vercel.com)
2. Sign in with GitHub
3. Click "Add New Project"
4. Import your `EVision` repository
5. Configure:
   - Root Directory: `frontend`
   - Framework Preset: Next.js
   - Build Command: `npm run build`
   - Output Directory: `.next`
6. Add Environment Variables:
   ```
   NEXT_PUBLIC_API_URL=https://evision-backend.onrender.com/api/v1
   NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id
   ```
7. Click "Deploy"
8. Your frontend will be live at: `https://evision-{your-name}.vercel.app`

**Backend - Render (Free)**

1. Go to [render.com](https://render.com)
2. Sign in with GitHub
3. Click "New +" → "Web Service"
4. Connect your `EVision` repository
5. Configure:
   - Name: `evision-backend`
   - Root Directory: `backend`
   - Runtime: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add Environment Variables:
   ```
   DATABASE_URL=(Render will provide after you create a PostgreSQL database)
   SECRET_KEY=(auto-generate a random string)
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   ALLOWED_ORIGINS=["https://evision-{your-name}.vercel.app"]
   DEBUG=False
   ```
7. Create PostgreSQL Database:
   - Click "New +" → "PostgreSQL"
   - Name: `evision-db`
   - Copy the "Internal Database URL"
   - Add it as `DATABASE_URL` in your web service
8. Click "Create Web Service"
9. Your backend will be live at: `https://evision-backend.onrender.com`

### Option 2: Deploy Everything to Railway

1. Go to [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Choose your `EVision` repository
5. Railway will auto-detect and deploy both services
6. Add environment variables in the Railway dashboard
7. Your app will be live at: `https://evision.up.railway.app`

### Option 3: Deploy to Fly.io

1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Sign up: `fly auth signup`
3. Deploy backend:
   ```bash
   cd backend
   fly launch --name evision-backend
   fly deploy
   ```
4. Deploy frontend:
   ```bash
   cd ../frontend
   fly launch --name evision-frontend
   fly deploy
   ```

## Manual Deployment Steps

### 1. Create Deployment Configs

Already created in the repository:
- `.github/workflows/deploy-frontend.yml` - Auto-deploy frontend
- `.github/workflows/deploy-backend.yml` - Auto-deploy backend
- `vercel.json` - Vercel configuration
- `render.yaml` - Render configuration

### 2. Set Up GitHub Secrets

For automated deployments, add these secrets in GitHub:
- Settings → Secrets and variables → Actions → New repository secret

**For Vercel:**
- `VERCEL_TOKEN` - Get from vercel.com/account/tokens

**For Render:**
- `RENDER_DEPLOY_HOOK` - Get from Render dashboard → Settings → Deploy Hook

### 3. Set Up Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create OAuth 2.0 credentials
3. Add authorized redirect URIs:
   - `https://your-frontend-url.vercel.app/login`
   - `https://your-frontend-url.vercel.app/auth/callback`
4. Copy Client ID and Secret to your deployment platforms

### 4. Deploy

**Automatic:**
- Just push to your GitHub repository
- GitHub Actions will automatically deploy

**Manual Vercel:**
```bash
cd frontend
npm install -g vercel
vercel login
vercel --prod
```

**Manual Render:**
- Push to GitHub
- Render auto-deploys on push

## Environment Variables Reference

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=https://your-backend-url.com/api/v1
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id
```

### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@host:5432/evision
SECRET_KEY=your-secret-key-min-32-characters
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=https://your-frontend-url.com/auth/callback
ALLOWED_ORIGINS=["https://your-frontend-url.com"]
DEBUG=False
```

## Post-Deployment

1. Test your deployment:
   - Visit your frontend URL
   - Check API docs at: `https://your-backend-url.com/docs`
   - Test health endpoint: `https://your-backend-url.com/health`

2. Set up monitoring (optional):
   - Render provides basic monitoring
   - Vercel provides analytics
   - Consider adding Sentry for error tracking

## Troubleshooting

**Database connection fails:**
- Verify DATABASE_URL is correct
- Ensure PostgreSQL database is created
- Check database is in same region as backend

**CORS errors:**
- Add frontend URL to ALLOWED_ORIGINS
- Ensure no trailing slashes in URLs

**Build fails:**
- Check build logs in deployment platform
- Verify all dependencies in requirements.txt / package.json
- Test build locally first

**OAuth not working:**
- Verify redirect URIs match exactly (including https://)
- Check Google Cloud Console credentials
- Ensure environment variables are set correctly

## Cost Estimates

**Free Tier Limits:**
- Vercel: Unlimited deployments, 100GB bandwidth/month
- Render: 750 hours/month free (enough for 1 service 24/7)
- Railway: $5 free credit/month
- Fly.io: 3 VMs free

**Recommended for production:**
- Vercel Pro: $20/month
- Render Standard: $7/month per service
- PostgreSQL: $7/month (Render)

**Total cost for free tier: $0**
**Total cost for production: ~$35-50/month**
