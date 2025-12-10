# Project Structure

This document describes the organized folder structure of the Raspberry Pi 5 Face Detection System.

## 📁 Directory Layout

```
RaspberryPie5/
│
├── 📄 README.md                    # Main documentation
├── 📄 QUICKSTART.md                # Quick start guide
├── 📄 STRUCTURE.md                 # This file
├── 📄 requirements.txt              # Python dependencies
├── 📄 .gitignore                   # Git ignore rules
│
├── 🚀 run.sh                       # Main entry point (face detection)
├── 🚀 run_api.sh                   # API server entry point
├── 🚀 run_enroll.sh                # Face enrollment entry point
│
├── 📚 docs/                        # Documentation
│   ├── API_GUIDE.md               # API usage guide
│   └── API_REFERENCE.md           # Complete API reference
│
├── 🔧 scripts/                     # Setup and utility scripts
│   ├── setup.sh                   # Main installation script
│   ├── run.sh                     # Face detection runner (internal)
│   ├── fix_libcap.sh              # Fix libcap installation
│   └── fix_numpy.sh               # Fix numpy compatibility
│
├── 💻 src/                         # Source code
│   ├── raspberry_pi_face_detection.py  # Main detection system
│   ├── api_server.py              # FastAPI server for n8n
│   ├── enroll_face.py              # Face enrollment tool
│   ├── test_camera.py             # Camera test utility
│   └── yolo.py                    # YOLO utilities
│
├── 🤖 models/                      # Model files
│   └── yolov12n-face.pt          # YOLOv12n-face detection model
│
├── 📝 logs/                        # Log files
│   └── (error logs stored here)
│
└── 🖼️ frames/                       # Frame storage (auto-created)
    └── (captured frames stored here)
```

## 🔄 Path Configuration

All paths are automatically configured relative to the project root:

- **Models**: `models/yolov12n-face.pt`
- **Face Database**: `known_faces.json` (project root)
- **Frame Storage**: `frames/` (project root)
- **Source Code**: `src/` directory

The system uses `Path(__file__).parent.parent` to automatically detect the project root, so paths work regardless of where you run the scripts from.

## 🚀 Running the System

### From Project Root (Recommended)
```bash
cd RaspberryPie5
./run.sh              # Face detection
./run_api.sh          # API server
./run_enroll.sh       # Face enrollment
```

### From Any Directory
```bash
cd /path/to/RaspberryPie5
./run.sh              # Works from anywhere
```

### Direct Python Execution
```bash
cd RaspberryPie5
python3 src/raspberry_pi_face_detection.py
python3 src/api_server.py
python3 src/enroll_face.py --name "John" --video video.mp4
```

## 📋 File Descriptions

### Root Level Scripts
- **run.sh**: Main entry point, delegates to `scripts/run.sh`
- **run_api.sh**: Starts the FastAPI server
- **run_enroll.sh**: Runs face enrollment tool

### Documentation
- **README.md**: Complete system documentation
- **QUICKSTART.md**: Quick start guide
- **docs/API_GUIDE.md**: API usage guide
- **docs/API_REFERENCE.md**: Complete API documentation

### Source Code
- **src/raspberry_pi_face_detection.py**: Main detection system (1387 lines)
- **src/api_server.py**: FastAPI server for n8n integration (715 lines)
- **src/enroll_face.py**: Face enrollment tool (381 lines)
- **src/test_camera.py**: Camera testing utility
- **src/yolo.py**: YOLO helper utilities

### Scripts
- **scripts/setup.sh**: Installs all dependencies
- **scripts/run.sh**: Internal runner (called by root run.sh)
- **scripts/fix_libcap.sh**: Fixes libcap installation issues
- **scripts/fix_numpy.sh**: Fixes numpy compatibility issues

## 🔧 Configuration Files

- **requirements.txt**: Python package dependencies
- **.gitignore**: Git ignore rules (excludes frames/, logs/, known_faces.json)
- **known_faces.json**: Face recognition database (created automatically, excluded from git)

## 📦 Generated Directories

These directories are created automatically when needed:

- **frames/**: Stores captured frames (last 100 kept)
- **logs/**: Stores error logs
- **__pycache__/**: Python cache (excluded from git)

## 🎯 Benefits of This Structure

1. **Organized**: Clear separation of concerns
2. **Maintainable**: Easy to find and update files
3. **Scalable**: Easy to add new features
4. **Portable**: Works from any directory
5. **Clean**: Root directory isn't cluttered

## 📝 Notes

- All scripts use relative paths that work from any directory
- The system automatically creates necessary directories
- Paths are configured in `Config` class using `BASE_DIR`
- Model path: `Config.BASE_DIR / "models" / "yolov12n-face.pt"`
- Database path: `Config.BASE_DIR / "known_faces.json"`
- Frame storage: `Config.BASE_DIR / "frames"`

