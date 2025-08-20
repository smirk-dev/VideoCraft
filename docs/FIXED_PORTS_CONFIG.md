# 🎬 VideoCraft - FIXED PORT CONFIGURATION

## 🔒 **FIXED PORTS (Cannot be changed without user instruction)**

- **Backend**: http://localhost:8001 (FIXED)
- **Frontend**: http://localhost:3001 (FIXED)
- **API Docs**: http://localhost:8001/api/docs

## 🚀 **How to Start VideoCraft**

### Option 1: Double-Click Launcher (Easiest)
```
📁 VideoCraft/
└── start-videocraft.bat  ← Double-click this file
```

### Option 2: PowerShell Script
```powershell
powershell -ExecutionPolicy Bypass -File start-videocraft.ps1
```

### Option 3: Manual Start (Terminal Commands)
```bash
# Terminal 1 (Backend on 8001)
cd backend
python simple_main.py

# Terminal 2 (Frontend on 3001) 
cd frontend
npm start
```

## ⚙️ **Configuration Files Enforcing Fixed Ports**

### Backend Configuration:
- `backend/simple_main.py` - Defaults to port 8001
- `backend/main.py` - Defaults to port 8001
- `backend/.env` - PORT=8001

### Frontend Configuration:
- `frontend/.env` - PORT=3001
- `frontend/package.json` - Scripts use PORT=3001
- CORS configured for localhost:3001 only

## 🔧 **Port Enforcement Details**

1. **Backend CORS**: Only allows connections from localhost:3001
2. **Frontend .env**: Hardcoded to PORT=3001
3. **Package.json**: Scripts enforce PORT=3001
4. **Startup Scripts**: All use fixed 8001/3001 ports
5. **API URLs**: Frontend configured to call localhost:8001

## ⚠️ **Important Notes**

- **Port conflicts**: If ports are in use, you must manually stop the conflicting services
- **No auto-port changing**: Scripts will not automatically try different ports
- **Consistent behavior**: All startup methods use the same fixed ports
- **CORS security**: Backend only accepts connections from the designated frontend port

## 🎯 **Testing the Fixed Configuration**

1. Start backend: Should run on http://localhost:8001
2. Start frontend: Should run on http://localhost:3001
3. Test API: Frontend should successfully connect to backend
4. Check CORS: Only localhost:3001 allowed in backend

## 🛠️ **If Ports Are In Use**

To free up the ports:

### Windows:
```cmd
# Check what's using the ports
netstat -ano | findstr :8001
netstat -ano | findstr :3001

# Kill processes (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### Manual Override (Only if instructed):
If you specifically need different ports, you would need to:
1. Update `backend/.env` 
2. Update `frontend/.env`
3. Update CORS settings in backend files
4. Update startup scripts

---

**✅ VideoCraft is now configured to ALWAYS use ports 8001/3001 unless manually instructed otherwise.**
