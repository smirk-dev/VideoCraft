# 📁 VideoCraft Project Structure

This document describes the organized structure of the VideoCraft project for better accessibility and readability.

## 🗂️ Root Directory Structure

```
VideoCraft/
├── 📁 backend/              # Backend API server
├── 📁 frontend/             # React frontend application
├── 📁 docs/                 # All documentation files
├── 📁 scripts/              # Development and utility scripts
├── 📁 deployment/           # Production deployment configurations
├── 📁 config/              # Configuration files and templates
├── 📄 .env                 # Environment variables (local)
├── 📄 .gitignore           # Git ignore rules
├── 📄 LICENSE              # Project license
└── 📄 README.md            # Main project documentation
```

## 📖 Directory Descriptions

### `/backend/` - Backend API Server
```
backend/
├── 📁 app/                  # Main application package
├── 📁 uploads/              # Uploaded video files
├── 📁 temp/                 # Temporary processing files
├── 📁 processed/            # Processed video outputs
├── 📄 simple_main_backup.py # Production backend server
├── 📄 requirements.txt      # Python dependencies
├── 📄 .env                  # Backend environment variables
└── 📄 .env.production       # Production environment config
```

### `/frontend/` - React Frontend Application
```
frontend/
├── 📁 public/               # Static public assets
├── 📁 src/                  # Source code
│   ├── 📁 components/       # React components
│   ├── 📁 pages/           # Page components
│   ├── 📁 services/        # API services
│   └── 📁 context/         # React context providers
├── 📁 build/               # Production build output
├── 📄 package.json         # Node.js dependencies
├── 📄 .env                 # Frontend environment variables
└── 📄 .env.production      # Production environment config
```

### `/docs/` - Documentation
```
docs/
├── 📄 DEPLOYMENT.md         # Deployment instructions
├── 📄 DEVELOPMENT.md        # Development setup guide
├── 📄 PRODUCTION_CHECKLIST.md # Pre-deployment checklist
├── 📄 READY_TO_DEPLOY.md    # Final deployment summary
├── 📄 FUNCTIONALITY_STATUS.md # Feature status tracking
├── 📄 PROJECT_STATUS.md     # Overall project status
├── 📄 ANALYSIS_FIXED.md     # Analysis fixes documentation
├── 📄 WORKING_STATUS.md     # Working features status
├── 📄 SETUP_COMPLETE.md     # Setup completion guide
├── 📄 PROJECT_RUNNING_STATUS.md # Runtime status
├── 📄 FIXED_PORTS_CONFIG.md # Port configuration fixes
└── 📄 PORT_CONFIG_SUCCESS.md # Port setup success guide
```

### `/scripts/` - Development Scripts
```
scripts/
├── 📄 start-custom-ports.bat    # Windows: Start with custom ports
├── 📄 start-custom-ports.ps1    # PowerShell: Start with custom ports
├── 📄 start-simple-backend.bat  # Windows: Start backend only
├── 📄 start-simple-backend.ps1  # PowerShell: Start backend only
├── 📄 start-videocraft.bat      # Windows: Start full application
├── 📄 start-videocraft.ps1      # PowerShell: Start full application
├── 📄 start.bat                 # Windows: Basic start script
├── 📄 start.sh                  # Linux/Mac: Basic start script
├── 📄 setup_real_implementation.ps1 # AI setup script (PowerShell)
└── 📄 setup_real_implementation.py  # AI setup script (Python)
```

### `/deployment/` - Production Deployment
```
deployment/
├── 📄 docker-compose.yml           # Development Docker setup
├── 📄 docker-compose.production.yml # Production Docker setup
├── 📄 Dockerfile.backend           # Backend Docker image
├── 📄 Dockerfile.frontend          # Frontend Docker image
├── 📄 start-production.bat         # Windows production deployment
└── 📄 start-production.sh          # Linux/Mac production deployment
```

### `/config/` - Configuration Files
```
config/
├── 📄 nginx.frontend.conf    # Nginx config for frontend
├── 📄 nginx.production.conf  # Production Nginx config
├── 📄 .env.example          # Environment variables template
├── 📄 requirements.txt      # Global Python requirements
└── 📄 setup.py             # Project setup configuration
```

## 🚀 Quick Start Commands

### Development
```bash
# Start development servers
scripts/start-videocraft.bat        # Windows
scripts/start-videocraft.ps1        # PowerShell
./scripts/start.sh                  # Linux/Mac
```

### Production Deployment
```bash
# Quick production deployment
deployment/start-production.bat     # Windows
./deployment/start-production.sh    # Linux/Mac

# Docker deployment
cd deployment/
docker-compose -f docker-compose.production.yml up -d
```

## 📚 Documentation Navigation

| File | Purpose |
|------|---------|
| `README.md` | Main project overview and quick start |
| `docs/DEPLOYMENT.md` | Complete deployment guide |
| `docs/DEVELOPMENT.md` | Development setup instructions |
| `docs/PRODUCTION_CHECKLIST.md` | Pre-deployment verification |
| `docs/READY_TO_DEPLOY.md` | Final deployment summary |
| `docs/FUNCTIONALITY_STATUS.md` | Feature implementation status |

## 🔧 Configuration Files

| File | Purpose |
|------|---------|
| `.env` | Local environment variables |
| `config/.env.example` | Environment template |
| `backend/.env.production` | Backend production config |
| `frontend/.env.production` | Frontend production config |
| `config/nginx.production.conf` | Production web server config |

## 📦 Dependencies

| File | Purpose |
|------|---------|
| `backend/requirements.txt` | Backend Python packages |
| `backend/requirements.production.txt` | Production Python packages |
| `frontend/package.json` | Frontend Node.js packages |
| `config/requirements.txt` | Global requirements template |

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   AI Services   │
│   (React)       │◄──►│   (FastAPI)     │◄──►│  (Simulation)   │
│   Port: 3000    │    │   Port: 8000    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Static Files  │    │   File Storage  │    │   ML Models     │
│   (Build/)      │    │   (uploads/)    │    │   (Cached)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🎯 Key Benefits of This Structure

1. **📁 Clear Separation**: Each directory has a specific purpose
2. **📖 Easy Navigation**: Logical grouping of related files
3. **🚀 Quick Deployment**: All deployment files in one place
4. **📚 Comprehensive Docs**: All documentation centralized
5. **🔧 Easy Maintenance**: Configuration files organized
6. **⚡ Fast Development**: Scripts readily available

This organized structure makes the VideoCraft project more maintainable, deployable, and easier to understand for new developers.
