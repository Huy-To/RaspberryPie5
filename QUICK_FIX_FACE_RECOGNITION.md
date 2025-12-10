# Quick Fix: face_recognition Installation Error

## The Error

```
error: externally-managed-environment
× This environment is externally managed
```

## The Solution

Use the `--break-system-packages` flag when installing:

```bash
python3 -m pip install --break-system-packages face_recognition
```

Or use the full command with all recommended flags:

```bash
python3 -m pip install --no-cache-dir --break-system-packages --no-warn-script-location face_recognition
```

## Why This Happens

Raspberry Pi OS (Debian-based) uses PEP 668 to prevent breaking system Python packages. The `--break-system-packages` flag is required to install packages system-wide.

## Complete Installation Steps

**IMPORTANT:** Install CMake and dependencies FIRST before installing face_recognition:

```bash
# 1. Update package list
sudo apt update

# 2. Install CMake and dlib dependencies (REQUIRED)
sudo apt install -y cmake libdlib-dev libopenblas-dev liblapack-dev

# 3. Verify CMake is installed
cmake --version

# 4. Install face_recognition
python3 -m pip install --break-system-packages face_recognition
```

**Note:** Building dlib can take 10-30 minutes on Raspberry Pi.

**If you get CMake error:** See [QUICK_FIX_CMAKE.md](QUICK_FIX_CMAKE.md) for detailed CMake troubleshooting.

## Alternative: Use Setup Script

The easiest way is to use the setup script which handles everything:

```bash
cd RaspberryPie5
chmod +x scripts/setup.sh
./scripts/setup.sh
```

The setup script automatically uses the correct flags and handles dependencies.

