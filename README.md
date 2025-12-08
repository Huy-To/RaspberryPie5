# Raspberry Pi 5 Face Detection System

A real-time face detection system optimized for Raspberry Pi 5 using YOLOv12n-face.pt model.

## ⚡ Quick Start (3 Steps)

1. **Navigate to directory:**
   ```bash
   cd RaspberryPie5
   ```

2. **Run setup (one command):**
   ```bash
   chmod +x setup.sh && ./setup.sh
   ```

3. **Run the system:**
   ```bash
   ./run.sh
   ```

**That's it!** The setup script handles everything automatically.

---

## 🚀 Features

- **Real-time face detection** with live camera feed
- **Optimized for Raspberry Pi 5** performance
- **Configurable detection parameters** (confidence threshold, resize factor, etc.)
- **Performance monitoring** with FPS tracking and processing statistics
- **Interactive controls** for runtime configuration
- **Parallel processing** support for better performance
- **Frame skipping** to reduce CPU load
- **Comprehensive error handling** and logging

## 📋 Requirements

### Hardware
- Raspberry Pi 5 (recommended) or Pi 4
- Camera module or USB webcam
- At least 4GB RAM (8GB recommended for best performance)
- MicroSD card with at least 16GB storage

### Software
- Raspberry Pi OS (64-bit recommended)
- Python 3.8 or higher
- Camera access permissions

## 🛠️ Installation

### Quick Setup (Recommended)

**One-command installation:**

```bash
cd RaspberryPie5
chmod +x setup.sh
./setup.sh
```

The setup script will:
- ✅ Install all required system packages
- ✅ Create a Python virtual environment
- ✅ Install all Python dependencies
- ✅ Verify the YOLO model file exists
- ✅ Test camera access (if connected)

**That's it!** The setup takes about 5-10 minutes on Raspberry Pi 5.

### Manual Setup

If you prefer manual installation or the script fails:

1. **Install essential system dependencies**:
   ```bash
   sudo apt update
   sudo apt install -y python3-pip python3-venv python3-dev libcap-dev
   ```
   
   **Note:** 
   - OpenCV will be installed via pip (included in requirements.txt)
   - `libcap-dev` is required for picamera2 (Raspberry Pi Camera Module support)

2. **Create virtual environment**:
   ```bash
   python3 -m venv face_detection_env
   source face_detection_env/bin/activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```
   
   This will install OpenCV via pip, which is more reliable on Raspberry Pi.

4. **Verify YOLO model**:
   - The `yolov12n-face.pt` model should be in the same directory
   - If missing, download from [Ultralytics releases](https://github.com/ultralytics/assets/releases)

## 🎬 Usage

### Quick Start

**After installation, simply run:**

```bash
./run.sh
```

The run script automatically:
- ✅ Activates the virtual environment
- ✅ Checks for required files
- ✅ Launches the face detection system

**Or run directly:**

```bash
source face_detection_env/bin/activate
python3 raspberry_pi_face_detection.py
```

**First time running?** Make sure:
- Camera is connected (USB webcam or Pi Camera Module)
- Camera is enabled (for Pi Camera: `sudo raspi-config` → Interface Options → Camera)
- You have a display connected (or use SSH with X11 forwarding)

### Camera Support

The system supports **two camera types**:

1. **Raspberry Pi Camera Module** (recommended)
   - Uses `picamera2` library (installed automatically)
   - Better performance and native support
   - Automatically detected in `auto` mode
   - Test with: `rpicam-hello`

2. **USB Webcam**
   - Uses OpenCV
   - Works with most USB cameras
   - Specify with: `--camera-type opencv --camera 0`

**Auto Mode** (default): System tries picamera2 first, then falls back to OpenCV if needed.

### Command Line Options

```bash
python3 raspberry_pi_face_detection.py [OPTIONS]
```

**Available options:**
- `--model PATH`: Path to YOLO model file (default: yolov12n-face.pt)
- `--conf FLOAT`: Confidence threshold 0.0-1.0 (default: 0.5)
- `--camera-type TYPE`: Camera type: `auto` (default, tries picamera2 first), `picamera2`, or `opencv`
- `--camera INT`: Camera index for OpenCV/USB webcams (default: 0)
- `--width INT`: Camera width (default: 640)
- `--height INT`: Camera height (default: 480)
- `--resize FLOAT`: Resize factor for processing 0.1-1.0 (default: 0.75)
- `--skip-frames INT`: Frames to skip between processing (default: 2)
- `--no-parallel`: Disable parallel processing

**Example usage:**
```bash
# Use Raspberry Pi Camera Module (automatic detection)
python3 raspberry_pi_face_detection.py

# Force use of picamera2 (Raspberry Pi Camera Module)
python3 raspberry_pi_face_detection.py --camera-type picamera2

# Force use of OpenCV (USB webcam)
python3 raspberry_pi_face_detection.py --camera-type opencv --camera 0

# Lower resolution for better performance
python3 raspberry_pi_face_detection.py --width 480 --height 360 --resize 0.5

# Higher confidence threshold for fewer false positives
python3 raspberry_pi_face_detection.py --conf 0.7

# Disable parallel processing if having issues
python3 raspberry_pi_face_detection.py --no-parallel
```

## 🎮 Controls

During runtime, you can use these keyboard controls:

| Key | Action |
|-----|--------|
| `q` or `ESC` | Quit the application |
| `r` | Reset FPS counter |
| `f` | Toggle FPS display |
| `d` | Toggle detection information |
| `s` | Toggle performance statistics |
| `c` | Cycle confidence threshold (0.3 → 0.5 → 0.7) |
| `SPACE` | Pause/Resume detection |

## ⚡ Performance Optimization

### For Better FPS

1. **Reduce camera resolution**:
   ```bash
   python3 raspberry_pi_face_detection.py --width 480 --height 360
   ```

2. **Increase frame skipping**:
   ```bash
   python3 raspberry_pi_face_detection.py --skip-frames 3
   ```

3. **Lower resize factor**:
   ```bash
   python3 raspberry_pi_face_detection.py --resize 0.5
   ```

### For Better Accuracy

1. **Increase confidence threshold**:
   ```bash
   python3 raspberry_pi_face_detection.py --conf 0.7
   ```

2. **Higher resolution**:
   ```bash
   python3 raspberry_pi_face_detection.py --width 800 --height 600
   ```

3. **No resize**:
   ```bash
   python3 raspberry_pi_face_detection.py --resize 1.0
   ```

### System-Level Optimizations

1. **Enable GPU memory split** (if using Pi GPU):
   ```bash
   sudo raspi-config
   # Advanced Options → Memory Split → 128 or 256
   ```

2. **Increase swap size** (if having memory issues):
   ```bash
   sudo nano /etc/dphys-swapfile
   # Change CONF_SWAPSIZE=100 to CONF_SWAPSIZE=2048
   sudo systemctl restart dphys-swapfile
   ```

3. **Overclock** (advanced users):
   ```bash
   sudo nano /boot/config.txt
   # Add: arm_freq=2000, gpu_freq=750
   ```

## 🔧 Configuration

You can modify the `Config` class in `raspberry_pi_face_detection.py` to adjust default settings:

```python
class Config:
    # Model settings
    MODEL_PATH = "yolov12n-face.pt"
    CONFIDENCE_THRESHOLD = 0.5
    IOU_THRESHOLD = 0.45
    
    # Camera settings
    CAMERA_INDEX = 0
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480
    CAMERA_FPS = 30
    
    # Performance settings
    RESIZE_FACTOR = 0.75
    SKIP_FRAMES = 2
    ENABLE_PARALLEL_PROCESSING = True
    
    # Display settings
    SHOW_FPS = True
    SHOW_DETECTION_INFO = True
    SHOW_PERFORMANCE_STATS = True
```

## 🐛 Troubleshooting

### Common Issues

1. **Camera not detected**:
   ```bash
   # Test Raspberry Pi Camera Module
   rpicam-hello
   
   # Test USB webcam
   python3 -c "import cv2; cap = cv2.VideoCapture(0); print('Camera OK' if cap.isOpened() else 'Camera Error'); cap.release()"
   ```
   - **Raspberry Pi Camera Module**: 
     - Enable in `sudo raspi-config` → Interface Options → Camera
     - Test with: `rpicam-hello`
     - Use: `--camera-type picamera2` or `--camera-type auto`
   - **USB webcam**: 
     - Try `--camera-type opencv --camera 0`, `--camera 1`, or `--camera 2`
     - Check connection: `lsusb`
   - **Auto mode**: System tries picamera2 first, then falls back to OpenCV

2. **"Model file not found" error**:
   - Verify model exists: `ls -la yolov12n-face.pt`
   - Make sure you're in the correct directory
   - Download model if missing from [Ultralytics releases](https://github.com/ultralytics/assets/releases)

3. **Low FPS performance**:
   - Reduce camera resolution: `--width 480 --height 360`
   - Increase frame skipping: `--skip-frames 3`
   - Lower resize factor: `--resize 0.5`
   - Check CPU temperature: `vcgencmd measure_temp`
   - Close other applications to free up resources

4. **Memory issues**:
   - Close other applications
   - Increase swap size (see System-Level Optimizations in README)
   - Use lower resolution or reduce resize factor

5. **Import errors (ultralytics, cv2, etc.)**:
   - Make sure virtual environment is activated: `source face_detection_env/bin/activate`
   - Reinstall dependencies: `pip install --upgrade -r requirements.txt`
   - Check if OpenCV is installed: `python3 -c "import cv2; print(cv2.__version__)"`
   - If OpenCV fails, try: `pip install --upgrade opencv-python`
   - **Note:** We use pip-installed OpenCV, not system OpenCV, so missing apt packages are OK

6. **python-prctl build error** ("You need to install libcap development headers"):
   ```bash
   sudo apt install -y libcap-dev
   pip install --upgrade picamera2
   ```
   This error occurs when installing picamera2. Installing `libcap-dev` fixes it.

6. **Display/GUI errors**:
   - If running headless (no display), the system will still process frames
   - For SSH: Use X11 forwarding: `ssh -X pi@your-pi-ip`
   - Or use VNC for remote desktop access

### Performance Monitoring

The system displays real-time performance information:
- **FPS**: Current frames per second
- **Faces**: Number of detected faces
- **Avg Time**: Average processing time per frame
- **Frame**: Current frame number
- **Queue**: Processing queue size

## 📊 Expected Performance

On Raspberry Pi 5 with default settings:
- **Resolution**: 640x480
- **Expected FPS**: 15-25 FPS
- **CPU Usage**: 60-80%
- **Memory Usage**: 200-400 MB

Performance varies based on:
- Number of faces in frame
- Lighting conditions
- Background complexity
- System temperature

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests to improve the system.

## 📄 License

This project is open source. Please check the main project license for details.

## 🙏 Acknowledgments

- [Ultralytics](https://ultralytics.com/) for YOLO models
- [OpenCV](https://opencv.org/) for computer vision capabilities
- Raspberry Pi Foundation for the amazing hardware platform

