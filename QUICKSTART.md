# Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Install Dependencies
```bash
cd RaspberryPie5
chmod +x scripts/setup.sh
./scripts/setup.sh

# If you see permission errors after setup:
chmod +x fix_permissions.sh
./fix_permissions.sh
```

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
./run_api.sh
```

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

