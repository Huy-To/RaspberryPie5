# Raspberry Pi 5 Face Detection & Recognition System

A real-time face detection and recognition system optimized for Raspberry Pi 5, featuring YOLOv12n-face detection, facial recognition, and n8n integration.

## 📁 Project Structure

```
RaspberryPie5/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── run.sh                    # Main run script (face detection)
├── run_api.sh               # API server run script
├── run_enroll.sh            # Face enrollment run script
│
├── docs/                     # Documentation
│   ├── API_GUIDE.md         # API usage guide
│   └── API_REFERENCE.md     # Complete API reference
│
├── scripts/                   # Setup and utility scripts
│   ├── setup.sh             # Installation script
│   ├── run.sh               # Face detection runner
│   ├── fix_libcap.sh        # Fix libcap installation
│   └── fix_numpy.sh         # Fix numpy compatibility
│
├── src/                       # Source code
│   ├── raspberry_pi_face_detection.py  # Main detection system
│   ├── api_server.py        # FastAPI server for n8n
│   ├── enroll_face.py       # Face enrollment tool
│   ├── test_camera.py       # Camera test utility
│   └── yolo.py              # YOLO utilities
│
├── models/                    # Model files
│   └── yolov12n-face.pt     # YOLOv12n-face detection model
│
├── logs/                      # Log files
│   └── (error logs)
│
└── frames/                    # Frame storage (created automatically)
    └── (captured frames)
```

## 🚀 Quick Start

### 1. Installation

Run the setup script to install all dependencies:

```bash
cd RaspberryPie5
chmod +x scripts/setup.sh
./scripts/setup.sh
```

Or run from project root:
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 2. Run Face Detection

**Option 1: Use main run script (recommended)**
```bash
chmod +x run.sh
./run.sh
```

**Option 2: Use scripts/run.sh directly**
```bash
chmod +x scripts/run.sh
./scripts/run.sh
```

**Option 3: Run Python script directly**
```bash
python3 src/raspberry_pi_face_detection.py
```

### 3. Run API Server

**Basic (no webhook):**
```bash
chmod +x run_api.sh
./run_api.sh
```

**With n8n webhook URL:**
```bash
# Option 1: Command line argument
./run_api.sh --webhook-url "http://n8n.local:5678/webhook/abc123"

# Option 2: Environment variable
N8N_WEBHOOK_URL="http://n8n.local:5678/webhook/abc123" ./run_api.sh

# Option 3: Direct Python call
python3 src/api_server.py --webhook-url "http://n8n.local:5678/webhook/abc123" --port 8000
```

**See [API Configuration Guide](docs/API_CONFIGURATION.md) for detailed setup instructions.**

### 4. Enroll Faces

```bash
chmod +x run_enroll.sh
./run_enroll.sh --name "John Doe" --video /path/to/video.mp4
```

Or directly:
```bash
python3 src/enroll_face.py --name "John Doe" --video /path/to/video.mp4
```

## 📋 Features

- ✅ Real-time face detection using YOLOv12n-face
- ✅ Facial recognition with known faces database
- ✅ Unknown person detection and alerts
- ✅ Verified person detection (95%+ confidence) with person info
- ✅ n8n integration via FastAPI webhooks
- ✅ Optimized for Raspberry Pi 5 performance
- ✅ Configurable detection parameters
- ✅ FPS monitoring and performance stats

## 🔧 Configuration

Edit `src/raspberry_pi_face_detection.py` to configure:

```python
class Config:
    # Model settings
    MODEL_PATH = "models/yolov12n-face.pt"  # Auto-configured
    
    # Camera settings
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480
    CAMERA_FPS = 30
    
    # Face recognition
    ENABLE_FACE_RECOGNITION = True
    FACE_DATABASE_PATH = "known_faces.json"  # Auto-configured
    
    # Alerts
    ENABLE_UNKNOWN_PERSON_ALERTS = True
    ENABLE_VERIFIED_PERSON_ALERTS = True
    VERIFIED_PERSON_CONFIDENCE_THRESHOLD = 0.95
    
    # n8n Integration
    ENABLE_N8N_INTEGRATION = True
    N8N_WEBHOOK_URL = "http://n8n.local:5678/webhook/abc123"
```

## 📚 Documentation

- **[Raspberry Pi Setup Guide](docs/RASPBERRY_PI_SETUP_GUIDE.md)** - ⭐ **Complete step-by-step setup guide**
- **[HTTP API Usage Guide](docs/HTTP_API_USAGE_GUIDE.md)** - ⭐ **Complete guide on using the HTTP API**
- **[API Guide](docs/API_GUIDE.md)** - Quick start guide for API usage
- **[API Reference](docs/API_REFERENCE.md)** - Complete API endpoint documentation
- **[Command API Guide](docs/COMMAND_API.md)** - Guide for sending commands from n8n to the system
- **[Automatic Unknown Person Alerts](docs/AUTO_UNKNOWN_PERSON_ALERTS.md)** - Auto-send alerts to n8n when unknown person detected ⭐
- **[Unknown Person API Guide](docs/UNKNOWN_PERSON_API_GUIDE.md)** - Manual API usage for unknown person alerts

## 🛠️ Troubleshooting

### Camera Issues
```bash
# Test camera
python3 src/test_camera.py

# Check camera permissions
sudo usermod -aG video $USER
```

### Installation Issues
```bash
# Fix script permissions (run after git pull)
./fix_permissions.sh

# Fix libcap installation
./scripts/fix_libcap.sh

# Fix numpy compatibility
./scripts/fix_numpy.sh
```

### Git Pull Issues (Permissions)
```bash
# After pulling from GitHub, fix permissions automatically:
./fix_permissions.sh

# Or set up git hooks for automatic fix (one-time):
chmod +x .git/hooks/post-merge .git/hooks/post-checkout
# Now permissions fix automatically after every git pull!
```

**See [Git Permissions Guide](docs/GIT_PERMISSIONS_GUIDE.md) for details.**

### API Server Issues
```bash
# Install missing python-multipart
python3 -m pip install --break-system-packages python-multipart

# Fix Pydantic warnings (update code)
# Code has been updated to use min_length/max_length
```

### Path Issues
All paths are automatically configured relative to the project root. The system will:
- Look for models in `models/` directory
- Store frames in `frames/` directory
- Store face database as `known_faces.json` in project root

## 📝 Scripts Overview

| Script | Purpose |
|--------|---------|
| `run.sh` | Main entry point for face detection |
| `run_api.sh` | Start API server for n8n integration |
| `run_enroll.sh` | Enroll new faces into database |
| `scripts/setup.sh` | Install all dependencies |
| `scripts/fix_libcap.sh` | Fix libcap installation issues |
| `scripts/fix_numpy.sh` | Fix numpy compatibility issues |

## 🔐 File Permissions

Make scripts executable:
```bash
chmod +x run.sh run_api.sh run_enroll.sh
chmod +x scripts/*.sh
```

## 📦 Dependencies

See `requirements.txt` for Python dependencies. System dependencies are installed via `scripts/setup.sh`.

## 🎯 Use Cases

- **Access Control**: Verify authorized personnel
- **Security Monitoring**: Detect unknown persons
- **Time Tracking**: Log employee check-ins
- **Visitor Management**: Track and log visitors
- **Home Automation**: Trigger actions based on recognized faces

## 📞 Support

For issues, check:
1. Error logs in `logs/` directory
2. Camera test: `python3 src/test_camera.py`
3. API health: `curl http://raspberrypi.local:8000/health`

---

**Last Updated:** 2024  
**Version:** 1.0.0
