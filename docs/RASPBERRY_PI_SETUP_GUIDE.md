# Complete Raspberry Pi 5 Setup & Run Guide

This comprehensive guide will walk you through setting up and running the Face Detection & Recognition System on your Raspberry Pi 5 from start to finish.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Installation](#installation)
4. [Camera Setup](#camera-setup)
5. [Running the System](#running-the-system)
6. [Enrolling Faces](#enrolling-faces)
7. [API Server Setup](#api-server-setup)
8. [Configuration](#configuration)
9. [Running as a Service](#running-as-a-service)
10. [Troubleshooting](#troubleshooting)
11. [Common Workflows](#common-workflows)

---

## Prerequisites

### Hardware Requirements

- **Raspberry Pi 5** (4GB RAM minimum, 8GB recommended)
- **Raspberry Pi Camera Module** (v2 or v3) - USB webcams are NOT supported
- **MicroSD Card** (32GB minimum, Class 10 or better)
- **Power Supply** (Official Raspberry Pi 5 power supply recommended)
- **Network Connection** (Ethernet or WiFi)

### Software Requirements

- **Raspberry Pi OS** (64-bit, Bookworm or later)
- **Python 3.8+** (usually pre-installed)
- **Internet Connection** (for downloading packages)

### Verify Your System

```bash
# Check Raspberry Pi model
cat /proc/cpuinfo | grep Model

# Check OS version
cat /etc/os-release

# Check Python version
python3 --version

# Check available memory
free -h
```

---

## Initial Setup

### Step 1: Update Raspberry Pi OS

```bash
# Update package list
sudo apt update

# Upgrade system packages (optional but recommended)
sudo apt upgrade -y

# Reboot if kernel was updated
sudo reboot
```

### Step 2: Enable Camera Interface

```bash
# Enable camera interface
sudo raspi-config
```

Navigate to:
1. **Interface Options** → **Camera** → **Enable**
2. Select **Finish** and reboot

**Or use command line:**
```bash
sudo raspi-config nonint do_camera 0
sudo reboot
```

### Step 3: Verify Camera Connection

After reboot, test the camera:

```bash
# Test camera with rpicam-hello (should show camera preview)
rpicam-hello

# Or test with still capture
rpicam-jpeg -o test.jpg
```

If the camera works, you should see a preview window or a captured image.

### Step 4: Clone or Copy Project Files

If you have the project files on another computer:

```bash
# Option 1: Using SCP (from your computer)
scp -r RaspberryPie5 pi@raspberrypi.local:~/

# Option 2: Using Git (if repository exists)
git clone <repository-url>
cd RaspberryPie5

# Option 3: Copy via USB drive
# Mount USB drive, then copy files
```

### Step 5: Navigate to Project Directory

```bash
cd ~/RaspberryPie5

# Verify files are present
ls -la
```

You should see:
- `README.md`
- `requirements.txt`
- `run.sh`, `run_api.sh`, `run_enroll.sh`
- `src/` directory
- `models/` directory
- `scripts/` directory

---

## Installation

### Step 1: Make Scripts Executable

```bash
cd ~/RaspberryPie5

# Make all scripts executable
chmod +x run.sh run_api.sh run_enroll.sh
chmod +x scripts/*.sh
chmod +x src/*.py
```

### Step 2: Run Setup Script

The setup script will install all required dependencies:

```bash
# Run the setup script
./scripts/setup.sh
```

**What the setup script does:**
1. Checks Python version
2. Updates package list
3. Installs system dependencies (libcap-dev, build tools, etc.)
4. Installs Python packages (ultralytics, picamera2, face_recognition, etc.)
5. Verifies installations

**Expected time:** 10-30 minutes depending on internet speed

**Important:** If you see errors about `libcap-dev` or `python-prctl`, run:

```bash
./scripts/fix_libcap.sh
```

### Step 3: Verify Installation

```bash
# Test Python imports
python3 -c "from picamera2 import Picamera2; print('✅ picamera2 OK')"
python3 -c "from ultralytics import YOLO; print('✅ ultralytics OK')"
python3 -c "import face_recognition; print('✅ face_recognition OK')"

# Check if model file exists
ls -lh models/yolov12n-face.pt
```

### Step 4: Fix PATH (if needed)

If you see warnings about scripts not being on PATH:

```bash
# Add ~/.local/bin to PATH permanently
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

---

## Camera Setup

### Step 1: Test Camera with Python

```bash
cd ~/RaspberryPie5
python3 src/test_camera.py
```

You should see:
- Camera initialization message
- Frame capture confirmation
- "Camera test successful!" message

### Step 2: Fix Camera Permissions (if needed)

If you get permission errors:

```bash
# Add user to video group
sudo usermod -aG video $USER

# Log out and back in, or:
newgrp video

# Verify
groups
```

### Step 3: Test Camera Preview

```bash
# Test with rpicam-hello (should show preview)
rpicam-hello

# Press Ctrl+C to exit
```

---

## Running the System

### Method 1: Run Face Detection (Recommended)

**Basic run:**
```bash
cd ~/RaspberryPie5
./run.sh
```

**With custom options:**
```bash
python3 src/raspberry_pi_face_detection.py \
  --conf 0.6 \
  --width 640 \
  --height 480 \
  --resize 0.75
```

**What you'll see:**
- System initialization messages
- Camera feed window (if display available)
- Console output with detection info
- FPS counter
- Detection statistics

**Controls:**
- `q` or `ESC`: Quit
- `r`: Reset FPS counter
- `f`: Toggle FPS display
- `d`: Toggle detection info
- `s`: Toggle performance stats
- `c`: Toggle confidence threshold
- `SPACE`: Pause/Resume

### Method 2: Run Without Display (Headless)

If running via SSH or without display:

```bash
# The system will automatically detect if display is unavailable
# and run in console-only mode
./run.sh
```

You'll see detection info in the console output.

### Method 3: Run in Background

```bash
# Run in background
nohup ./run.sh > detection.log 2>&1 &

# Check if running
ps aux | grep raspberry_pi_face_detection

# View logs
tail -f detection.log

# Stop
pkill -f raspberry_pi_face_detection
```

---

## Enrolling Faces

### Step 1: Prepare Video

Create a video of the person rotating their face:
- **Duration:** 10-30 seconds
- **Format:** MP4, MOV, or AVI
- **Quality:** 720p or higher recommended
- **Content:** Person should rotate head slowly (left, right, up, down)

### Step 2: Transfer Video to Raspberry Pi

```bash
# Option 1: Using SCP (from your computer)
scp video.mp4 pi@raspberrypi.local:~/RaspberryPie5/

# Option 2: Using USB drive
# Copy video to USB, then on Pi:
cp /media/usb/video.mp4 ~/RaspberryPie5/
```

### Step 3: Enroll Face

```bash
cd ~/RaspberryPie5

# Basic enrollment
./run_enroll.sh --name "John Doe" --video video.mp4

# With options
python3 src/enroll_face.py \
  --name "John Doe" \
  --video video.mp4 \
  --max-frames 50 \
  --frame-skip 5
```

**Parameters:**
- `--name`: Person's name (required)
- `--video`: Path to video file (required)
- `--max-frames`: Maximum frames to process (default: 30)
- `--frame-skip`: Process every Nth frame (default: 5)

**What happens:**
1. Video is processed frame by frame
2. Faces are detected in each frame
3. Face encodings are extracted
4. Encodings are saved to `known_faces.json`

### Step 4: Verify Enrollment

```bash
# Check face database
cat known_faces.json | python3 -m json.tool

# Or use API command
curl -X POST http://localhost:8000/command \
  -H "Content-Type: application/json" \
  -d '{"command": "get_enrolled_faces", "parameters": {}}'
```

---

## API Server Setup

### Step 1: Configure n8n Integration (Optional)

Edit `src/raspberry_pi_face_detection.py`:

```python
class Config:
    # Enable n8n integration
    ENABLE_N8N_INTEGRATION = True
    N8N_WEBHOOK_URL = "http://n8n.local:5678/webhook/your-webhook-id"
    
    # Enable API server
    API_SERVER_ENABLED = True
    API_SERVER_HOST = "0.0.0.0"
    API_SERVER_PORT = 8000
```

### Step 2: Run API Server

**Option 1: Integrated (with face detection)**
```bash
# API server starts automatically when face detection runs
# if API_SERVER_ENABLED = True
./run.sh
```

**Option 2: Standalone**
```bash
# Run API server separately
./run_api.sh

# Or with custom options
python3 src/api_server.py \
  --webhook-url "http://n8n.local:5678/webhook/abc123" \
  --host 0.0.0.0 \
  --port 8000
```

### Step 3: Test API Server

```bash
# Health check
curl http://localhost:8000/health

# Test command endpoint
curl -X POST http://localhost:8000/command \
  -H "Content-Type: application/json" \
  -d '{"command": "test_connection", "parameters": {}}'

# Get status
curl -X POST http://localhost:8000/command \
  -H "Content-Type: application/json" \
  -d '{"command": "get_status", "parameters": {}}'
```

### Step 4: Access API Documentation

Open in browser (if accessible):
- **Swagger UI:** `http://raspberrypi.local:8000/docs`
- **ReDoc:** `http://raspberrypi.local:8000/redoc`

---

## Configuration

### Main Configuration File

Edit `src/raspberry_pi_face_detection.py`:

```python
class Config:
    # Model settings
    MODEL_PATH = "models/yolov12n-face.pt"  # Auto-configured
    CONFIDENCE_THRESHOLD = 0.5  # Detection confidence (0.0-1.0)
    IOU_THRESHOLD = 0.45
    
    # Camera settings
    CAMERA_WIDTH = 640   # Camera resolution width
    CAMERA_HEIGHT = 480  # Camera resolution height
    CAMERA_FPS = 30      # Frames per second
    
    # Performance settings
    RESIZE_FACTOR = 0.75  # Resize input for faster processing (0.1-1.0)
    SKIP_FRAMES = 2       # Process every 3rd frame
    ENABLE_PARALLEL_PROCESSING = True
    
    # Face recognition
    ENABLE_FACE_RECOGNITION = True
    FACE_DATABASE_PATH = "known_faces.json"  # Auto-configured
    RECOGNITION_TOLERANCE = 0.6  # Lower = more strict (0.4-0.6 recommended)
    
    # Alerts
    ENABLE_UNKNOWN_PERSON_ALERTS = True
    UNKNOWN_PERSON_ALERT_COOLDOWN = 30  # Seconds
    
    ENABLE_VERIFIED_PERSON_ALERTS = True
    VERIFIED_PERSON_CONFIDENCE_THRESHOLD = 0.95  # 95% confidence required
    VERIFIED_PERSON_ALERT_COOLDOWN = 60  # Seconds
    
    # n8n Integration
    ENABLE_N8N_INTEGRATION = True
    N8N_WEBHOOK_URL = "http://n8n.local:5678/webhook/abc123"
    API_SERVER_ENABLED = True
    API_SERVER_HOST = "0.0.0.0"
    API_SERVER_PORT = 8000
    API_FRAME_STORAGE_DIR = "frames"  # Auto-configured
    API_FRAME_BASE_URL = "http://raspberrypi.local:8000/frames"
    CAMERA_ID = "raspberry_pi_camera"
```

### Performance Tuning

**For Better FPS:**
```python
RESIZE_FACTOR = 0.5  # Smaller = faster
SKIP_FRAMES = 3      # Process every 4th frame
CAMERA_WIDTH = 320   # Lower resolution
CAMERA_HEIGHT = 240
```

**For Better Accuracy:**
```python
RESIZE_FACTOR = 1.0  # No resizing
SKIP_FRAMES = 0      # Process every frame
CAMERA_WIDTH = 1280  # Higher resolution
CAMERA_HEIGHT = 720
CONFIDENCE_THRESHOLD = 0.6  # Higher threshold
```

---

## Running as a Service

### Create Systemd Service

Create service file:

```bash
sudo nano /etc/systemd/system/face-detection.service
```

Add content:

```ini
[Unit]
Description=Raspberry Pi Face Detection System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/RaspberryPie5
ExecStart=/usr/bin/python3 /home/pi/RaspberryPie5/src/raspberry_pi_face_detection.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable face-detection.service

# Start service
sudo systemctl start face-detection.service

# Check status
sudo systemctl status face-detection.service

# View logs
sudo journalctl -u face-detection.service -f

# Stop service
sudo systemctl stop face-detection.service

# Disable service
sudo systemctl disable face-detection.service
```

### Create API Server Service (Optional)

```bash
sudo nano /etc/systemd/system/face-detection-api.service
```

```ini
[Unit]
Description=Raspberry Pi Face Detection API Server
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/RaspberryPie5
ExecStart=/usr/bin/python3 /home/pi/RaspberryPie5/src/api_server.py --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable face-detection-api.service
sudo systemctl start face-detection-api.service
```

---

## Troubleshooting

### Camera Issues

**Problem: Camera not detected**
```bash
# Check camera is enabled
sudo raspi-config nonint do_camera 0

# Check camera connection
vcgencmd get_camera

# Should show: supported=1 detected=1

# Test with rpicam-hello
rpicam-hello
```

**Problem: Permission denied**
```bash
# Add user to video group
sudo usermod -aG video $USER
newgrp video

# Check permissions
ls -l /dev/video*
```

**Problem: Camera preview not showing**
- The system works without display
- Check console output for detection info
- Display requires X11 and tkinter

### Installation Issues

**Problem: libcap-dev not found**
```bash
./scripts/fix_libcap.sh
```

**Problem: numpy compatibility**
```bash
./scripts/fix_numpy.sh
```

**Problem: pip externally-managed-environment error**
```bash
# Use --break-system-packages flag (already in setup.sh)
python3 -m pip install --break-system-packages <package>
```

**Problem: picamera2 import fails**
```bash
# Install via apt
sudo apt install -y python3-picamera2

# Or via pip
python3 -m pip install --break-system-packages picamera2
```

### Runtime Issues

**Problem: Low FPS**
```bash
# Reduce resolution
# Edit Config: CAMERA_WIDTH = 320, CAMERA_HEIGHT = 240

# Increase frame skipping
# Edit Config: SKIP_FRAMES = 3

# Reduce resize factor
# Edit Config: RESIZE_FACTOR = 0.5
```

**Problem: High CPU usage**
```bash
# Disable parallel processing
# Edit Config: ENABLE_PARALLEL_PROCESSING = False

# Increase frame skipping
# Edit Config: SKIP_FRAMES = 5
```

**Problem: Out of memory**
```bash
# Check memory usage
free -h

# Reduce resolution
# Edit Config: CAMERA_WIDTH = 320, CAMERA_HEIGHT = 240

# Increase swap (if needed)
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

**Problem: Model file not found**
```bash
# Check model exists
ls -lh models/yolov12n-face.pt

# Download if missing (if you have the file)
# Place in models/ directory
```

### API Issues

**Problem: API not accessible**
```bash
# Check if API server is running
ps aux | grep api_server

# Check firewall
sudo ufw status
sudo ufw allow 8000

# Check if port is in use
sudo netstat -tulpn | grep 8000
```

**Problem: Webhook not receiving events**
```bash
# Test webhook URL
curl -X POST http://n8n.local:5678/webhook/abc123 \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'

# Check n8n webhook is active
# Verify N8N_WEBHOOK_URL in config
```

### Face Recognition Issues

**Problem: Faces not recognized**
```bash
# Check face database
cat known_faces.json | python3 -m json.tool

# Re-enroll with better video
# Use video with good lighting and clear face

# Adjust tolerance
# Edit Config: RECOGNITION_TOLERANCE = 0.5 (lower = more strict)
```

**Problem: Too many false positives**
```bash
# Increase tolerance
# Edit Config: RECOGNITION_TOLERANCE = 0.7

# Increase confidence threshold
# Edit Config: CONFIDENCE_THRESHOLD = 0.6
```

---

## Common Workflows

### Workflow 1: First-Time Setup

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Enable camera
sudo raspi-config nonint do_camera 0
sudo reboot

# 3. After reboot, navigate to project
cd ~/RaspberryPie5

# 4. Make scripts executable
chmod +x run.sh run_api.sh run_enroll.sh scripts/*.sh

# 5. Run setup
./scripts/setup.sh

# 6. Test camera
python3 src/test_camera.py

# 7. Run face detection
./run.sh
```

### Workflow 2: Enroll New Person

```bash
# 1. Record video of person rotating face
# (on phone/computer, then transfer)

# 2. Transfer video to Pi
scp video.mp4 pi@raspberrypi.local:~/RaspberryPie5/

# 3. Enroll face
cd ~/RaspberryPie5
./run_enroll.sh --name "John Doe" --video video.mp4

# 4. Verify enrollment
cat known_faces.json | python3 -m json.tool
```

### Workflow 3: Start System on Boot

```bash
# 1. Create systemd service (see "Running as a Service" section)

# 2. Enable service
sudo systemctl enable face-detection.service

# 3. Start service
sudo systemctl start face-detection.service

# 4. Check status
sudo systemctl status face-detection.service
```

### Workflow 4: Monitor System Remotely

```bash
# 1. Start API server
./run_api.sh

# 2. From another computer, check status
curl -X POST http://raspberrypi.local:8000/command \
  -H "Content-Type: application/json" \
  -d '{"command": "get_status", "parameters": {}}'

# 3. Get recent detections
curl -X POST http://raspberrypi.local:8000/command \
  -H "Content-Type: application/json" \
  -d '{"command": "get_recent_detections", "parameters": {"limit": 10}}'
```

### Workflow 5: Debug Issues

```bash
# 1. Check camera
rpicam-hello

# 2. Test Python imports
python3 -c "from picamera2 import Picamera2; print('OK')"
python3 -c "from ultralytics import YOLO; print('OK')"

# 3. Run with verbose output
python3 src/raspberry_pi_face_detection.py --no-parallel

# 4. Check logs
tail -f detection.log  # If running in background
# Or check systemd logs
sudo journalctl -u face-detection.service -f
```

---

## Quick Reference

### Essential Commands

```bash
# Setup
./scripts/setup.sh

# Run face detection
./run.sh

# Run API server
./run_api.sh

# Enroll face
./run_enroll.sh --name "Name" --video video.mp4

# Test camera
python3 src/test_camera.py

# Check status (if API running)
curl http://localhost:8000/health
```

### File Locations

- **Config:** `src/raspberry_pi_face_detection.py` (Config class)
- **Face Database:** `known_faces.json` (project root)
- **Frames:** `frames/` directory
- **Logs:** `logs/` directory
- **Model:** `models/yolov12n-face.pt`

### Important Paths

- **Project Root:** `~/RaspberryPie5`
- **Source Code:** `~/RaspberryPie5/src/`
- **Scripts:** `~/RaspberryPie5/scripts/`
- **Models:** `~/RaspberryPie5/models/`

---

## Next Steps

1. **Enroll faces** - Add people to the recognition database
2. **Configure alerts** - Set up n8n webhooks for notifications
3. **Tune performance** - Adjust settings for your use case
4. **Set up monitoring** - Use API commands to monitor system
5. **Automate** - Create systemd services for auto-start

---

## Additional Resources

- **[API Guide](API_GUIDE.md)** - API usage guide
- **[API Reference](API_REFERENCE.md)** - Complete API documentation
- **[Command API](COMMAND_API.md)** - Command endpoint guide
- **[README](../README.md)** - Project overview

---

**Last Updated:** 2024  
**Version:** 1.0.0

