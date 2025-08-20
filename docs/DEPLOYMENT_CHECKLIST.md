# 🚀 VideoCraft Deployment Checklist

## 📋 Pre-Deployment Setup

### ✅ Repository Preparation
- [ ] **Code pushed to GitHub**: Ensure latest code is in your GitHub repository
- [ ] **Clean commit history**: All changes committed and pushed
- [ ] **No sensitive data**: Check no API keys or secrets in code
- [ ] **Dependencies updated**: All package.json and requirements.txt up to date

### ✅ Configuration Files Created
- [ ] **vercel.json**: ✅ Created in project root
- [ ] **railway.toml**: ✅ Created in project root  
- [ ] **Procfile**: ✅ Created in project root
- [ ] **backend/.env.production**: Production backend config
- [ ] **frontend/.env.production**: Production frontend config

---

## 🛤️ Railway Backend Deployment

### Step 1: Create Railway Account
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub account
3. Verify email address

### Step 2: Deploy Backend
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose **VideoCraft** repository
4. Select **"Deploy Now"**

### Step 3: Configure Environment Variables
Go to Railway Dashboard → Variables and add:

```env
PORT=8000
PYTHONPATH=/app/backend
DEBUG=false
MAX_UPLOAD_SIZE=104857600
CORS_ORIGINS=["https://videocraft.vercel.app"]
```

### Step 4: Set Custom Start Command
Railway Dashboard → Settings → Deploy → Start Command:
```bash
cd backend && python simple_main_backup.py --host 0.0.0.0 --port $PORT
```

### Step 5: Get Railway URL
- Copy your Railway deployment URL: `https://your-app.railway.app`
- You'll need this for frontend configuration

---

## 🌐 Vercel Frontend Deployment

### Step 1: Create Vercel Account
1. Go to [vercel.com](https://vercel.com)
2. Sign up with GitHub account
3. Install Vercel GitHub app

### Step 2: Import Project
1. Click **"New Project"**
2. Import **VideoCraft** from GitHub
3. Configure build settings:

```bash
Framework Preset: Create React App
Root Directory: frontend/
Build Command: npm run build
Output Directory: build
Install Command: npm install
```

### Step 3: Configure Environment Variables
Vercel Dashboard → Settings → Environment Variables:

```env
REACT_APP_API_URL=https://your-railway-url.railway.app
REACT_APP_MAX_FILE_SIZE=104857600
NODE_ENV=production
```

### Step 4: Deploy
- Click **"Deploy"**
- Wait for build to complete
- Get your Vercel URL: `https://videocraft.vercel.app`

---

## 🔗 Connect Frontend & Backend

### Step 1: Update CORS in Backend
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

### Step 2: Update Frontend API URL
Update `frontend/.env.production`:

```env
REACT_APP_API_URL=https://your-actual-railway-url.railway.app
```

### Step 3: Redeploy
- **Railway**: Automatic redeploy after pushing to GitHub
- **Vercel**: Automatic redeploy after pushing to GitHub

---

## 🧪 Testing Your Deployment

### ✅ Backend Tests
1. Visit: `https://your-railway-url.railway.app/docs`
2. Test API endpoints in Swagger UI
3. Check health endpoint: `/health`
4. Verify CORS headers in browser dev tools

### ✅ Frontend Tests  
1. Visit: `https://your-vercel-url.vercel.app`
2. Test file upload functionality
3. Verify API connections in Network tab
4. Test video analysis features
5. Check export functionality

### ✅ Integration Tests
1. Upload a small video file
2. Wait for AI analysis to complete
3. Test video editing features
4. Export in different formats
5. Verify all features work end-to-end

---

## 🌍 Custom Domain Setup (Optional)

### For Frontend (Vercel)
1. Vercel Dashboard → Settings → Domains
2. Add your domain: `videocraft.com`
3. Configure DNS:
   ```dns
   Type: CNAME
   Name: www
   Value: cname.vercel-dns.com
   ```

### For Backend (Railway)
1. Railway Dashboard → Settings → Domains  
2. Add: `api.videocraft.com`
3. Configure DNS:
   ```dns
   Type: CNAME
   Name: api
   Value: your-project.railway.app
   ```

---

## 🎉 Success Verification

Your deployment is successful when:

- [ ] **Frontend loads**: `https://videocraft.vercel.app` shows your app
- [ ] **Backend responds**: `https://your-app.railway.app/docs` shows API docs
- [ ] **File upload works**: Can upload videos up to 100MB
- [ ] **AI analysis runs**: Video processing completes successfully
- [ ] **Export functions**: Can download processed videos and reports
- [ ] **No CORS errors**: Frontend can communicate with backend
- [ ] **SSL certificates**: Both URLs show secure (🔒) in browser

---

## 📊 Final Setup

**Your Live URLs:**
- 🌐 **Frontend**: `https://videocraft.vercel.app`
- 🔗 **Backend**: `https://videocraft-backend.railway.app`  
- 📚 **API Docs**: `https://videocraft-backend.railway.app/docs`

**Monthly Costs:**
- 💰 **Free Tier**: $0/month (Railway $5 credit + Vercel free)
- 📈 **Paid Tier**: $5-25/month (depending on usage)

**Performance:**
- ⚡ **Frontend**: Global CDN via Vercel
- 🚀 **Backend**: Railway cloud infrastructure
- 📱 **Mobile**: Responsive design works on all devices

Your professional AI video editing platform is now live and ready for users! 🌟
