# 🚀 VideoCraft Deployment Guide - Vercel + Railway

## 🎯 Deployment Strategy

**Frontend (React)** → **Vercel** (Optimized for React/Next.js)  
**Backend (FastAPI)** → **Railway** (Python-friendly with persistent storage)  
**Domain** → **Custom domain** or **Free .vercel.app subdomain**

---

## 📋 Prerequisites

- [ ] **GitHub Repository** (push your code to GitHub)
- [ ] **Vercel Account** (free at vercel.com)
- [ ] **Railway Account** (free at railway.app)
- [ ] **Domain Name** (optional - can use free subdomains)

---

## 🚀 Part 1: Backend Deployment (Railway)

### Step 1: Prepare Backend for Railway

First, let's create Railway-specific configuration files:

#### 1.1 Create Railway Configuration

```bash
# Already exists in deployment/ folder
railway.toml
Procfile
requirements.txt
```

#### 1.2 Update Environment Variables

Create production environment file:

```env
# backend/.env.production
DATABASE_URL=postgresql://railway_generated_url
RAILWAY_ENVIRONMENT=production
HOST=0.0.0.0
PORT=$PORT
DEBUG=false
MAX_UPLOAD_SIZE=104857600  # 100MB for Railway limits
CORS_ORIGINS=["https://your-domain.vercel.app", "https://videocraft.vercel.app"]
```

### Step 2: Deploy to Railway

#### 2.1 Connect GitHub to Railway

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click **"New Project"**
4. Select **"Deploy from GitHub repo"**
5. Choose your **VideoCraft** repository
6. Select **"Deploy Now"**

#### 2.2 Configure Railway Settings

```bash
# Railway will auto-detect Python and install dependencies
# Configure these environment variables in Railway dashboard:

PORT=8000
PYTHONPATH=/app
DATABASE_URL=postgresql://...  # Railway provides this
MAX_UPLOAD_SIZE=104857600
DEBUG=false
```

#### 2.3 Set Custom Start Command

In Railway dashboard → Settings → Deploy:
```bash
cd backend && python simple_main_backup.py --host 0.0.0.0 --port $PORT
```

---

## 🌐 Part 2: Frontend Deployment (Vercel)

### Step 1: Prepare Frontend for Vercel

#### 1.1 Create Vercel Configuration

Create `vercel.json` in project root:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "build"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/frontend/$1"
    }
  ],
  "env": {
    "REACT_APP_API_URL": "https://your-railway-backend.railway.app"
  }
}
```

#### 1.2 Update Frontend Environment

Create `frontend/.env.production`:

```env
REACT_APP_API_URL=https://videocraft-backend.railway.app
REACT_APP_MAX_FILE_SIZE=104857600
GENERATE_SOURCEMAP=false
PUBLIC_URL=https://videocraft.vercel.app
```

### Step 2: Deploy to Vercel

#### 2.1 Connect GitHub to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub
3. Click **"New Project"**
4. Import your **VideoCraft** repository
5. Configure build settings:

```bash
# Build Settings
Framework Preset: Create React App
Root Directory: frontend/
Build Command: npm run build
Output Directory: build
Install Command: npm install
```

#### 2.2 Configure Environment Variables

In Vercel dashboard → Settings → Environment Variables:

```env
REACT_APP_API_URL=https://videocraft-backend-production.up.railway.app
REACT_APP_MAX_FILE_SIZE=104857600
NODE_ENV=production
```

---

## 🔗 Part 3: Connect Frontend & Backend

### Step 3.1: Update CORS Settings

Update your backend CORS configuration:

```python
# backend/simple_main_backup.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://videocraft.vercel.app",  # Your Vercel domain
        "https://your-custom-domain.com", # Your custom domain
        "http://localhost:3001"  # Local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Step 3.2: Update API Base URL

Update frontend API configuration:

```javascript
// frontend/src/services/api.js
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://videocraft-backend.railway.app';

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes for large uploads
  headers: {
    'Content-Type': 'application/json',
  },
});
```

---

## 🌍 Part 4: Custom Domain Setup

### Option 1: Use Free Subdomains

**Frontend**: `videocraft.vercel.app` (automatic)  
**Backend**: `videocraft-backend.railway.app` (automatic)

### Option 2: Custom Domain

#### 4.1 Configure Custom Domain for Frontend (Vercel)

1. In Vercel dashboard → Settings → Domains
2. Add your domain: `videocraft.com`
3. Configure DNS records:

```dns
Type: CNAME
Name: www
Value: cname.vercel-dns.com

Type: A
Name: @
Value: 76.76.19.61
```

#### 4.2 Configure Custom Domain for Backend (Railway)

1. In Railway dashboard → Settings → Domains
2. Add custom domain: `api.videocraft.com`
3. Configure DNS:

```dns
Type: CNAME
Name: api
Value: your-project.railway.app
```

---

## ⚙️ Part 5: Production Optimizations

### 5.1 Backend Optimizations

```python
# backend/simple_main_backup.py production settings
import os

# Production configuration
if os.getenv("RAILWAY_ENVIRONMENT") == "production":
    # Optimize for production
    app.debug = False
    
    # Add request size limits for Railway
    from fastapi import Request
    from fastapi.exceptions import RequestValidationError
    
    @app.middleware("http")
    async def limit_upload_size(request: Request, call_next):
        if request.method == "POST" and "upload" in str(request.url):
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > 104857600:  # 100MB
                raise RequestValidationError("File too large")
        return await call_next(request)
```

### 5.2 Frontend Optimizations

```javascript
// frontend/src/config/production.js
export const PRODUCTION_CONFIG = {
  API_URL: process.env.REACT_APP_API_URL,
  MAX_FILE_SIZE: 100 * 1024 * 1024, // 100MB for Railway
  CHUNK_SIZE: 1024 * 1024, // 1MB chunks for uploads
  TIMEOUT: 300000, // 5 minutes
};
```

---

## 🔍 Part 6: Monitoring & Maintenance

### 6.1 Railway Monitoring

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and monitor
railway login
railway status
railway logs
```

### 6.2 Vercel Monitoring

```bash
# Install Vercel CLI
npm install -g vercel

# Monitor deployments
vercel --prod
vercel logs
```

### 6.3 Set Up Alerts

**Railway**:
- Go to Project → Observability
- Set up CPU/Memory alerts
- Configure uptime monitoring

**Vercel**:
- Go to Project → Functions → Monitoring
- Set up performance alerts
- Monitor build times

---

## 💰 Cost Estimation

### Free Tier Limits

**Railway**:
- ✅ $5/month free credit
- ✅ 512MB RAM
- ✅ Shared CPU
- ✅ 1GB disk space

**Vercel**:
- ✅ 100GB bandwidth/month
- ✅ 1000 serverless function invocations
- ✅ Free custom domain

### Paid Upgrades

**Railway Pro ($5-20/month)**:
- 8GB RAM
- More CPU
- 100GB disk
- Priority support

**Vercel Pro ($20/month)**:
- Unlimited bandwidth
- Advanced analytics
- Password protection
- Team collaboration

---

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] Code pushed to GitHub
- [ ] Environment variables configured
- [ ] CORS settings updated
- [ ] File size limits adjusted for Railway
- [ ] Production builds tested locally

### Railway Backend Deployment
- [ ] Railway account created
- [ ] GitHub repository connected
- [ ] Environment variables set
- [ ] Custom start command configured
- [ ] Database connected (if needed)
- [ ] Health check endpoint working

### Vercel Frontend Deployment
- [ ] Vercel account created
- [ ] Build settings configured
- [ ] Environment variables set
- [ ] Custom domain configured (optional)
- [ ] API connectivity tested

### Post-Deployment
- [ ] Frontend can reach backend API
- [ ] File uploads working within limits
- [ ] CORS configured correctly
- [ ] Custom domains working
- [ ] SSL certificates active
- [ ] Monitoring and alerts set up

---

## 🔧 Troubleshooting

### Common Issues

**Backend (Railway)**:
```bash
# Build failures
railway logs --tail

# Memory issues
railway config set RAILWAY_MEMORY_LIMIT=1024

# Port binding issues
railway config set PORT=8000
```

**Frontend (Vercel)**:
```bash
# Build failures
vercel logs

# Environment variable issues
vercel env ls

# Domain configuration
vercel domains ls
```

### Quick Fixes

```bash
# Redeploy backend
railway redeploy

# Redeploy frontend
vercel --prod

# Check status
railway status
vercel inspect
```

---

## 🎉 Success!

Once deployed, your VideoCraft will be available at:

- **Frontend**: `https://videocraft.vercel.app`
- **Backend**: `https://videocraft-backend.railway.app`
- **API Docs**: `https://videocraft-backend.railway.app/docs`

**Total Setup Time**: ~30 minutes  
**Monthly Cost**: $0-25 (depending on usage)  
**Scalability**: Auto-scaling on both platforms

Your professional AI video editing platform is now live! 🌟
