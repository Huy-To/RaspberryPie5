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

If `face_recognition` fails, install dependencies first:

```bash
# 1. Install dlib dependencies
sudo apt install -y libdlib-dev cmake libopenblas-dev liblapack-dev

# 2. Install face_recognition
python3 -m pip install --break-system-packages face_recognition
```

**Note:** Building dlib can take 10-30 minutes on Raspberry Pi.

## Alternative: Use Setup Script

The easiest way is to use the setup script which handles everything:

```bash
cd RaspberryPie5
chmod +x scripts/setup.sh
./scripts/setup.sh
```

The setup script automatically uses the correct flags and handles dependencies.

