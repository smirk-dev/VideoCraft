# 🚀 Vercel + Render Deployment Guide

## 🎯 **Why Vercel + Render?**

**Perfect combination for VideoCraft:**
- **Frontend (React)** → **Vercel**: Global CDN, automatic optimization
- **Backend (FastAPI)** → **Render**: Free tier, persistent storage, PostgreSQL
- **Total Cost**: $0/month to start (both have generous free tiers)
- **Setup Time**: 12 minutes total

---

## 📋 **Prerequisites**

- [ ] **GitHub Repository** with your VideoCraft code
- [ ] **Vercel Account** (free at vercel.com)
- [ ] **Render Account** (free at render.com)

---

## 🌐 **Part 1: Frontend Deployment (Vercel) - 5 minutes**

### Step 1: Create Vercel Account
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub account
3. Install Vercel GitHub app

### Step 2: Deploy Frontend
1. Click **"New Project"**
2. Import your **VideoCraft** repository
3. Configure build settings:

```bash
Framework Preset: Create React App
Root Directory: frontend/
Build Command: npm run build
Output Directory: build
Install Command: npm install
```

### Step 3: Set Environment Variables
In Vercel Dashboard → Settings → Environment Variables:

```env
REACT_APP_API_URL=https://videocraft-backend.onrender.com
REACT_APP_MAX_FILE_SIZE=104857600
NODE_ENV=production
```

### Step 4: Deploy
- Click **"Deploy"**
- Wait for build to complete (~2-3 minutes)
- Get your URL: `https://videocraft.vercel.app`

---

## 🖥️ **Part 2: Backend Deployment (Render) - 5 minutes**

### Step 1: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up with GitHub account
3. Connect your GitHub repository

### Step 2: Create Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your **VideoCraft** repository
3. Configure service:

```bash
Name: videocraft-backend
Region: Oregon (US West)
Branch: main
Root Directory: (leave blank)
Runtime: Python 3
Build Command: cd backend && pip install -r requirements.txt
Start Command: cd backend && python simple_main_backup.py --host 0.0.0.0 --port $PORT
```

### Step 3: Set Environment Variables
In Render Dashboard → Environment:

```env
PYTHON_VERSION=3.11.0
DEBUG=false
MAX_UPLOAD_SIZE=104857600
CORS_ORIGINS=["https://videocraft.vercel.app"]
PYTHONPATH=/opt/render/project/src/backend
```

### Step 4: Enable Persistent Disk (Optional)
For file uploads:
1. Go to **Environment** → **Disks**
2. Add disk: **Name**: `uploads`, **Mount Path**: `/opt/render/project/src/backend/uploads`, **Size**: 1GB

### Step 5: Deploy
- Click **"Create Web Service"**
- Wait for deployment (~3-5 minutes)
- Get your URL: `https://videocraft-backend.onrender.com`

---

## 🔗 **Part 3: Connect Services - 2 minutes**

### Step 1: Update Frontend API URL
Update your Vercel environment variables:

```env
REACT_APP_API_URL=https://your-actual-render-url.onrender.com
```

### Step 2: Update Backend CORS
Add to `backend/simple_main_backup.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://videocraft.vercel.app",  # Your actual Vercel URL
        "http://localhost:3001"  # Local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Step 3: Push Changes
```bash
git add .
git commit -m "Configure production deployment"
git push origin main
```

Both Vercel and Render will automatically redeploy!

---

## 🧪 **Testing Your Deployment**

### ✅ **Verify Backend**
1. Visit: `https://your-render-url.onrender.com/docs`
2. Test the `/health` endpoint
3. Check if Swagger UI loads correctly

### ✅ **Verify Frontend**
1. Visit: `https://your-vercel-url.vercel.app`
2. Test file upload (should connect to backend)
3. Check browser console for any CORS errors

### ✅ **Integration Test**
1. Upload a small video file
2. Wait for AI analysis to complete
3. Verify export functionality works

---

## 🌍 **Custom Domain Setup (Optional)**

### For Frontend (Vercel)
1. Vercel Dashboard → Settings → Domains
2. Add your domain: `videocraft.com`
3. Configure DNS as instructed by Vercel

### For Backend (Render)
1. Render Dashboard → Settings → Custom Domains
2. Add: `api.videocraft.com`
3. Configure DNS:
   ```dns
   Type: CNAME
   Name: api
   Value: your-service.onrender.com
   ```

---

## 📊 **Platform Benefits**

### **Vercel (Frontend)**
✅ Global CDN with edge caching  
✅ Automatic code splitting  
✅ Zero-config deployment  
✅ Built-in analytics  
✅ Custom domains included  

### **Render (Backend)**
✅ Free tier: 750 hours/month  
✅ Automatic SSL certificates  
✅ Zero-downtime deployments  
✅ Built-in monitoring  
✅ Persistent disk storage  
✅ Free PostgreSQL database  

---

## 💰 **Cost Breakdown**

### **Free Tier Limits**
**Vercel Free:**
- 100GB bandwidth/month
- 1000 serverless function invocations
- Custom domains included

**Render Free:**
- 750 hours/month runtime
- 512MB RAM, 0.1 CPU
- 1GB persistent disk
- Free PostgreSQL (90 days)

### **Paid Upgrades**
**Vercel Pro ($20/month):**
- Unlimited bandwidth
- Advanced analytics
- Team collaboration

**Render Starter ($7/month):**
- Always-on service
- 1GB RAM, 0.5 CPU
- More reliable performance

---

## 🔧 **Troubleshooting**

### **Common Issues**

**Backend doesn't start:**
```bash
# Check Render logs
- Go to Render Dashboard → Logs
- Look for Python/pip errors
- Verify requirements.txt is correct
```

**Frontend can't reach backend:**
```bash
# Check CORS configuration
- Verify CORS origins in backend
- Check API URL in frontend environment
- Test API endpoints directly
```

**File uploads fail:**
```bash
# Check file size limits
- Render free tier: 100MB max
- Adjust MAX_UPLOAD_SIZE accordingly
- Consider upgrading for larger files
```

---

## 🎉 **Success Verification**

Your deployment is successful when:

- [ ] **Frontend loads**: `https://videocraft.vercel.app`
- [ ] **Backend responds**: `https://videocraft-backend.onrender.com/docs`
- [ ] **API connection works**: No CORS errors in browser console
- [ ] **File upload works**: Can upload videos successfully
- [ ] **AI analysis runs**: Video processing completes
- [ ] **Export functions**: Can download results

---

## 📈 **Performance Optimization**

### **For Production Use:**

**Vercel Optimizations:**
- Enable analytics for performance monitoring
- Use custom domains for branding
- Implement caching strategies

**Render Optimizations:**
- Upgrade to paid plan for always-on service
- Use persistent disk for uploaded files
- Add PostgreSQL database for user data
- Set up health checks and monitoring

---

## 🚀 **Final URLs**

After successful deployment:

- 🌐 **Frontend**: `https://videocraft.vercel.app`
- 🔗 **Backend**: `https://videocraft-backend.onrender.com`
- 📚 **API Docs**: `https://videocraft-backend.onrender.com/docs`

**Total Setup Time**: ~12 minutes  
**Monthly Cost**: $0 to start, $27/month for full features  
**Performance**: Production-ready with global distribution

Your VideoCraft AI platform is now live on professional infrastructure! 🌟
