# Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Install Dependencies
```bash
cd RaspberryPie5

# Fix permissions (especially after git pull)
./fix_permissions.sh

# Run setup
./scripts/setup.sh
```

**Note:** If you pulled from GitHub, run `./fix_permissions.sh` first to make scripts executable.

### Step 2: Run Face Detection
```bash
chmod +x run.sh
./run.sh
```

### Step 3: (Optional) Enroll Faces
```bash
chmod +x run_enroll.sh
./run_enroll.sh --name "Your Name" --video /path/to/video.mp4
```

## 📋 Common Commands

### Run Face Detection
```bash
./run.sh
```

### Run API Server
```bash
# Basic (no webhook)
./run_api.sh

# With n8n webhook URL
./run_api.sh --webhook-url "http://n8n.local:5678/webhook/your-id"
```

**See [API Configuration Guide](docs/API_CONFIGURATION.md) for setup details.**

### Enroll New Face
```bash
./run_enroll.sh --name "John Doe" --video video.mp4
```

### Test Camera
```bash
python3 src/test_camera.py
```

## 🔧 Configuration

Edit `src/raspberry_pi_face_detection.py` to configure:
- Camera resolution
- Detection thresholds
- n8n webhook URL
- Alert settings

## 📚 More Information

- **Complete Setup Guide:** See [docs/RASPBERRY_PI_SETUP_GUIDE.md](docs/RASPBERRY_PI_SETUP_GUIDE.md) ⭐
- Full documentation: See [README.md](README.md)
- API documentation: See [docs/API_REFERENCE.md](docs/API_REFERENCE.md)
- API guide: See [docs/API_GUIDE.md](docs/API_GUIDE.md)

