# VideoCraft Backend

Clean, organized backend for the VideoCraft video analysis platform.

## Structure

```
backend_clean/
├── main.py              # Main Flask application
├── start.py             # Startup script with dependency installation
├── requirements.txt     # Python dependencies
├── .env                # Configuration file
└── README.md           # This file
```

## Quick Start

### Option 1: Auto-setup (Recommended)
```bash
cd backend_clean
python start.py
```

### Option 2: Manual setup
```bash
cd backend_clean
pip install -r requirements.txt
python main.py
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/analyze` | Analyze video |
| POST | `/api/analyze/<filename>` | Analyze specific video |
| GET | `/api/recommendations` | Get recommendations |
| POST | `/api/upload` | Upload video |

## Features

- ✅ Flask-based REST API
- ✅ CORS enabled for frontend
- ✅ Structured JSON responses
- ✅ Error handling
- ✅ Logging
- ✅ Mock data for testing
- ✅ Simple dependency management

## Development

The backend currently returns mock data to test frontend integration. 
Real AI/ML processing can be added later by implementing the analysis functions.

## Configuration

Edit `.env` file to customize:
- Port (default: 8002)
- CORS origins
- Upload settings
- Processing timeouts
