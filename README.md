# Raspberry Pi 5 Face Detection & Recognition System (Picamera2 Only)

A real-time face detection and recognition system optimized for Raspberry Pi 5 using YOLOv12n-face.pt model.
**This version uses picamera2 ONLY - no OpenCV required. Designed specifically for Raspberry Pi Camera Module.**

## 🆕 New: Facial Recognition!

The system now includes **facial recognition** capabilities! You can:
- Enroll faces of known people
- Recognize faces in real-time
- See names displayed on detected faces
- Manage a database of known faces

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
   
   Or directly:
   ```bash
   python3 raspberry_pi_face_detection.py
   ```

**That's it!** The setup script installs everything system-wide (no virtual environment needed).

---

## 🚀 Features

- **Real-time face detection** with live camera feed
- **Facial recognition** - recognize known faces and display names
- **Face enrollment** - easily add new faces to the recognition database
- **Display window** showing video feed with detections and names (tkinter-based)
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
- **Raspberry Pi Camera Module** (required - USB webcams not supported)
- At least 4GB RAM (8GB recommended for best performance)
- MicroSD card with at least 16GB storage

### Software
- Raspberry Pi OS (64-bit recommended)
- Python 3.8 or higher
- Camera enabled in raspi-config
- **picamera2 library** (installed automatically)
- **tkinter** and **python3-pil.imagetk** (installed automatically by setup script, required for display window)
- **face_recognition library** (installed automatically, optional for facial recognition features)
  - Requires dlib (can take 10-30 minutes to build on Raspberry Pi)
  - System packages recommended: `libdlib-dev cmake libopenblas-dev liblapack-dev`
- **imageio and imageio-ffmpeg** (installed automatically, for video-based enrollment)
  - Requires ffmpeg: `sudo apt install -y ffmpeg`

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
- ✅ Install all Python dependencies (system-wide)
- ✅ Verify the YOLO model file exists
- ✅ Test camera access (if connected)

**That's it!** The setup takes about 5-10 minutes on Raspberry Pi 5.

### Manual Setup

If you prefer manual installation or the script fails:

1. **Install essential system dependencies**:
   ```bash
   sudo apt update
   sudo apt install -y python3-pip python3-dev
   ```
   
   **Optional (for picamera2/Pi Camera Module):**
   ```bash
   # Try to install libcap-dev (may not be available on all OS versions)
   sudo apt install -y libcap-dev || sudo apt install -y libcap2-dev || echo "libcap-dev not available"
   ```
   
   **Note:** 
   - `libcap-dev` is required for picamera2

2. **Install Python dependencies**:
   ```bash
   # Add ~/.local/bin to PATH (if not already there)
   export PATH="$HOME/.local/bin:$PATH"
   
   # Install packages
   python3 -m pip install --upgrade pip setuptools wheel --break-system-packages --no-warn-script-location
   python3 -m pip install --break-system-packages --no-warn-script-location -r requirements.txt
   ```
   
   **Note:** 
   - `--break-system-packages` flag is required on newer Raspberry Pi OS versions (PEP 668)
   - `--no-warn-script-location` suppresses PATH warnings
   - The setup script automatically adds `~/.local/bin` to your PATH
   
   This will install picamera2, ultralytics, Pillow, and numpy system-wide.

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
python3 raspberry_pi_face_detection.py
```

**First time running?** Make sure:
- Camera is connected (Raspberry Pi Camera Module)
- Camera is enabled: `sudo raspi-config` → Interface Options → Camera
- Test camera works: `rpicam-hello` (should show camera feed for 5 seconds)
- Test Python access: `python3 test_camera.py` (after setup)

### Camera Support

**This system ONLY supports Raspberry Pi Camera Module via picamera2.**

- Uses `picamera2` library (installed automatically)
- Native Raspberry Pi Camera Module support
- No OpenCV required
- Test camera with: `rpicam-hello`

**Note:** USB webcams are not supported in this version. This system is designed specifically for Raspberry Pi Camera Module.

### Command Line Options

```bash
python3 raspberry_pi_face_detection.py [OPTIONS]
```

**Available options:**
- `--model PATH`: Path to YOLO model file (default: yolov12n-face.pt)
- `--conf FLOAT`: Confidence threshold 0.0-1.0 (default: 0.5)
- `--width INT`: Camera width (default: 640)
- `--height INT`: Camera height (default: 480)
- `--resize FLOAT`: Resize factor for processing 0.1-1.0 (default: 0.75)
- `--skip-frames INT`: Frames to skip between processing (default: 2)
- `--no-parallel`: Disable parallel processing
- `--no-console`: Disable console output

**Example usage:**
```bash
# Basic usage (Raspberry Pi Camera Module)
python3 raspberry_pi_face_detection.py

# Lower resolution for better performance
python3 raspberry_pi_face_detection.py --width 480 --height 360 --resize 0.5

# Higher confidence threshold for fewer false positives
python3 raspberry_pi_face_detection.py --conf 0.7

# Disable parallel processing if having issues
python3 raspberry_pi_face_detection.py --no-parallel

# Disable console output (for headless operation)
python3 raspberry_pi_face_detection.py --no-console
```

## 👤 Facial Recognition

### Enrolling Faces from Video

Before the system can recognize faces, you need to enroll them into the database using a video file:

```bash
# Basic enrollment (processes up to 30 frames from video)
python3 enroll_face.py --name "John Doe" --video "face_video.mp4"

# Process more frames for better accuracy
python3 enroll_face.py --name "Jane Smith" --video "video.mp4" --max-frames 50

# Process every frame (slower but more thorough)
python3 enroll_face.py --name "Bob" --video "video.mp4" --frame-skip 1
```

**Video Requirements:**
- **Supported formats**: MP4, AVI, MOV, MKV, etc. (any format supported by ffmpeg)
- **Content**: Video of face rotating slowly (10-30 seconds recommended)
- **Lighting**: Face should be clearly visible and well-lit
- **Position**: Face should be centered and clearly visible throughout the video
- **Rotation**: Slowly rotate your head left/right and up/down to capture multiple angles

**Tips for best results:**
- Record in good lighting conditions
- Keep face centered in frame
- Rotate slowly (about 2-3 seconds per rotation)
- Avoid rapid movements
- Ensure face is not partially obscured

### Managing the Face Database

```bash
# List all enrolled faces
python3 enroll_face.py --list

# Delete a face from the database
python3 enroll_face.py --delete "John Doe"
```

### How Recognition Works

1. **Face Detection**: YOLO detects faces in the frame
2. **Face Encoding**: Each detected face is encoded into a 128-dimensional vector
3. **Face Matching**: Encodings are compared with known faces in the database
4. **Display**: Recognized faces show names in green, unknown faces show "Unknown" in orange

### Recognition Settings

You can adjust recognition sensitivity in `raspberry_pi_face_detection.py`:

```python
class Config:
    RECOGNITION_TOLERANCE = 0.6  # Lower = more strict (0.4-0.6 recommended)
    ENABLE_FACE_RECOGNITION = True  # Set to False to disable recognition
```

**Tolerance values:**
- `0.4`: Very strict (fewer false positives, may miss some matches)
- `0.6`: Balanced (recommended)
- `0.7`: More lenient (more matches, but may have false positives)

### Face Database

- Stored in `known_faces.json` (JSON format)
- Each person can have multiple encodings (captured from different angles/lighting)
- More encodings per person = better recognition accuracy
- Database is automatically loaded when the system starts

### Troubleshooting Recognition

**Problem: Faces not being recognized**
- Make sure faces are enrolled: `python3 enroll_face.py --list`
- Check lighting conditions (good lighting improves accuracy)
- Try processing more frames: `python3 enroll_face.py --name "Name" --video "video.mp4" --max-frames 50`
- Ensure video has good face coverage (multiple angles)
- Adjust tolerance: Lower values = more strict matching

**Problem: Video processing fails**
- Check video format is supported (MP4, AVI, MOV, etc.)
- Install ffmpeg: `sudo apt install -y ffmpeg`
- Install imageio: `python3 -m pip install --break-system-packages imageio imageio-ffmpeg`
- Try a different video format or re-encode the video

**Problem: Wrong person recognized**
- Lower the tolerance value in Config
- Re-enroll faces with better lighting/angles
- Ensure face is clearly visible and not partially obscured

**Problem: face_recognition library not installed**
- Install dependencies: `sudo apt install -y libdlib-dev cmake libopenblas-dev liblapack-dev`
- Install library: `python3 -m pip install --break-system-packages face_recognition`
- Note: Building dlib can take 10-30 minutes on Raspberry Pi

## 🔌 n8n Integration API

For complete API documentation, see **[API_REFERENCE.md](API_REFERENCE.md)** - comprehensive list of all available endpoints for n8n.

The system includes a FastAPI server for sending detection events to n8n workflows.

### Configuration

Enable n8n integration in `raspberry_pi_face_detection.py`:

```python
class Config:
    # Enable n8n webhook integration
    ENABLE_N8N_INTEGRATION = True
    N8N_WEBHOOK_URL = "http://n8n.local:5678/webhook/abc123"  # Your n8n webhook URL
    
    # Unknown person alert settings
    ENABLE_UNKNOWN_PERSON_ALERTS = True  # Enable automatic unknown person alerts
    UNKNOWN_PERSON_ALERT_COOLDOWN = 30  # Seconds between alerts (prevents spam)
    
    # Optional: Start FastAPI server
    API_SERVER_ENABLED = True
    API_SERVER_HOST = "0.0.0.0"
    API_SERVER_PORT = 8000
    API_FRAME_STORAGE_DIR = "frames"
    API_FRAME_BASE_URL = "http://raspberrypi.local:8000/frames"  # Optional
    CAMERA_ID = "raspberry_pi_camera"
```

### Unknown Person Detection & Alerts

The system can automatically detect unknown persons and send alerts with captured images to n8n:

**Features:**
- ✅ Automatic detection of unknown faces (not in recognition database)
- ✅ Captures and sends image of unknown person
- ✅ Cooldown period to prevent alert spam
- ✅ Crops image to focus on unknown person
- ✅ Sends `unknown_person_detected` event to n8n webhook

**How it works:**
1. System detects faces using YOLO
2. Attempts to recognize faces using face recognition database
3. If face is not recognized (name = "Unknown"), triggers alert
4. Captures frame with unknown person
5. Sends alert event to n8n with image URL

**Alert Event Schema:**
```json
{
  "camera_id": "raspberry_pi_camera",
  "event_type": "unknown_person_detected",
  "timestamp": "2024-01-15T10:30:45.123456",
  "detections": [
    {
      "label": "unknown_person",
      "confidence": 0.95,
      "bbox": [100, 150, 200, 250],
      "name": null
    }
  ],
  "frame_url": "http://raspberrypi.local:8000/frames/unknown_person_20240115_103045.jpg",
  "metadata": {
    "frame_count": 1234,
    "fps": 15.5,
    "alert_type": "unknown_person",
    "count": 1,
    "cooldown_seconds": 30
  }
}
```

### Event Schema

Events sent to n8n follow this JSON schema:

```json
{
  "camera_id": "raspberry_pi_camera",
  "event_type": "face_detected",
  "timestamp": "2024-01-15T10:30:45.123456",
  "detections": [
    {
      "label": "face",
      "confidence": 0.95,
      "bbox": [100, 150, 200, 250],
      "name": "John Doe"
    }
  ],
  "frame_url": "http://raspberrypi.local:8000/frames/frame_20240115_103045.jpg",
  "metadata": {
    "frame_count": 1234,
    "fps": 15.5
  }
}
```

### API Endpoints

**POST /event** - Receive detection events (called internally)
- Accepts detection event JSON
- Forwards to n8n webhook

**POST /training-clip** - Accept training clip metadata
- Accepts clip path, metadata, optional preview frame
- Forwards to n8n webhook

**GET /health** - Health check endpoint
- Returns API status and webhook configuration

**GET /** - API information
- Returns available endpoints

### Standalone API Server

You can also run the API server standalone:

```bash
python3 api_server.py --webhook-url "http://n8n.local:5678/webhook/abc123" --port 8000
```

### n8n Webhook Setup

1. Create a webhook node in your n8n workflow
2. Copy the webhook URL
3. Configure it in `raspberry_pi_face_detection.py`:
   ```python
   N8N_WEBHOOK_URL = "http://your-n8n-instance:5678/webhook/your-webhook-id"
   ```

### Event Types

- `face_detected` - Sent when faces are detected
- `training_clip_ready` - Sent when training clips are ready (via `/training-clip` endpoint)

### Frame Storage

- Frames are saved to `frames/` directory by default
- Old frames are automatically cleaned up (keeps last 100)
- Frame URLs are included in events if `API_FRAME_BASE_URL` is configured

## 🎮 Controls

**Display Window:**
- A tkinter window displays the live camera feed with face detection overlays
- Close the window or press **Ctrl+C** to quit
- If tkinter is not available, the system runs in console-only mode

**Console Output:**
- Detection results are printed to console
- Performance stats (FPS, face count, processing time) are displayed in console output

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
   # Test Raspberry Pi Camera Module (system level)
   rpicam-hello
   
   # Test Python picamera2 access
   python3 test_camera.py
   ```
   - **If `rpicam-hello` works but Python test fails**:
     - Camera hardware is fine ✅
     - Issue is with picamera2 installation
     - Make sure picamera2 is installed: `pip install picamera2`
     - Check virtual environment is activated
   - **If `rpicam-hello` fails**:
     - Enable camera: `sudo raspi-config` → Interface Options → Camera
     - Check camera connection (Pi 5 uses 15-pin connector)
     - Verify camera is properly seated
   - **Note**: USB webcams are NOT supported in this version

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

5. **Import errors (ultralytics, picamera2, etc.)**:
   - Reinstall dependencies: `python3 -m pip install --break-system-packages --no-warn-script-location -r requirements.txt`
   - Check if picamera2 is installed: `python3 -c "from picamera2 import Picamera2; print('OK')"`
   - Check if ultralytics is installed: `python3 -c "from ultralytics import YOLO; print('OK')"`
   - If packages fail, try: `python3 -m pip install --upgrade --break-system-packages --no-warn-script-location package_name`

6. **"No module named picamera2" error**:
   ```bash
   python3 -m pip install --break-system-packages picamera2
   ```
   This usually means:
   - picamera2 didn't install during setup: Re-run `./setup.sh`
   - Or install manually: `python3 -m pip install --break-system-packages picamera2`

7. **"externally-managed-environment" error**:
   This error occurs on newer Raspberry Pi OS versions that protect system Python.
   The setup script uses `--break-system-packages` flag to work around this.
   If you see this error manually, add the flag:
   ```bash
   python3 -m pip install --break-system-packages --no-warn-script-location package_name
   ```

8. **numpy version incompatibility error** ("numpy.dtype size changed"):
   ```bash
   # Quick fix - run this script
   chmod +x fix_numpy.sh
   ./fix_numpy.sh
   
   # Or manually:
   # Uninstall pip numpy and use system version
   python3 -m pip uninstall -y numpy
   # Or install compatible version
   python3 -m pip install --break-system-packages "numpy<2.0"
   ```
   This happens when system picamera2 (compiled against older numpy) conflicts with 
   newer pip-installed numpy. The fix script resolves this automatically.

9. **PATH warnings** ("script is installed in '/home/pi/.local/bin' which is not on PATH"):
   The setup script automatically adds `~/.local/bin` to your PATH.
   If you still see warnings:
   ```bash
   # Add to current session
   export PATH="$HOME/.local/bin:$PATH"
   
   # Add permanently to ~/.bashrc
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```
   Or restart your terminal session.

7. **python-prctl build error** ("You need to install libcap development headers"):
   ```bash
   # Quick fix - run this script
   chmod +x fix_libcap.sh
   ./fix_libcap.sh
   
   # Or manually:
   sudo apt update
   sudo apt install -y libcap-dev
   # If that fails, try:
   sudo apt install -y libcap2-dev
   # Or:
   sudo apt install -y libcap2
   
   # Then install picamera2
   source face_detection_env/bin/activate
   pip install picamera2
   ```
   This error occurs when installing picamera2. The `python-prctl` dependency requires libcap development headers.
   
   **Solutions:**
   - **Option 1**: Run the fix script: `./fix_libcap.sh`
   - **Option 2**: Install manually: `sudo apt install -y libcap-dev`
   - **Option 3**: Try alternative package: `sudo apt install -y libcap2-dev` or `libcap2`
   - **Option 4**: Update your system: `sudo apt update && sudo apt upgrade`
   - **Option 5**: Install build-essential first: `sudo apt install -y build-essential`
   - **After fixing libcap-dev**: `python3 -m pip install --break-system-packages picamera2`

6. **Display window not showing**:
   - **tkinter not available**: Install with `sudo apt install -y python3-tk`
   - **ImageTk not available**: Install with `sudo apt install -y python3-pil.imagetk`
   - **Both required**: You need both `python3-tk` and `python3-pil.imagetk` for the display window
   - **Running headless**: The system will run in console-only mode if display dependencies are not available
   - **SSH without display**: Use X11 forwarding: `ssh -X pi@your-pi-ip`
   - **Remote desktop**: Use VNC for remote desktop access
   - **Note**: The system will still process frames and output to console even without the display window

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

