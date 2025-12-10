# Fix Common Errors

This guide helps you fix common errors encountered when running the system.

## Error 1: Pydantic Deprecation Warnings

**Error:**
```
PydanticDeprecatedSince20: `min_items` is deprecated and will be removed, use `min_length` instead.
```

**Status:** ✅ **FIXED** - Code has been updated to use `min_length`/`max_length`

**Solution:** Update to the latest code. The issue has been fixed in `src/api_server.py`.

## Error 2: python-multipart Missing

**Error:**
```
Form data requires "python-multipart" to be installed.
RuntimeError: Form data requires "python-multipart" to be installed.
```

**Status:** ✅ **FIXED** - Added to requirements.txt and setup.sh

**Solution:**

```bash
# Install python-multipart
python3 -m pip install --break-system-packages python-multipart

# Or re-run setup script (it will install it automatically)
./scripts/setup.sh
```

**Verification:**
```bash
python3 -c "import multipart; print('✅ python-multipart installed')"
```

## Error 3: Permission Denied

**Error:**
```
./run.sh: line 11: /home/pi/RaspberryPie5/scripts/run.sh: Permission denied
exec: /home/pi/RaspberryPie5/scripts/run.sh: cannot execute: Permission denied
```

**Status:** ✅ **FIXED** - Setup script now makes all scripts executable

**Solution:**

```bash
# Option 1: Use fix_permissions.sh (recommended)
chmod +x fix_permissions.sh
./fix_permissions.sh

# Option 2: Manual fix
chmod +x run.sh run_api.sh run_enroll.sh
chmod +x scripts/*.sh
chmod +x src/*.py

# Option 3: Re-run setup script
./scripts/setup.sh
```

**Verification:**
```bash
ls -l run.sh scripts/run.sh
# Should show: -rwxr-xr-x (executable)
```

## Error 4: externally-managed-environment

**Error:**
```
error: externally-managed-environment
× This environment is externally managed
```

**Status:** ✅ **FIXED** - All pip commands use --break-system-packages

**Solution:**

Always use `--break-system-packages` flag:

```bash
# Correct way
python3 -m pip install --break-system-packages <package>

# Wrong way (will fail)
pip install <package>
```

**Examples:**
```bash
# Install face_recognition
python3 -m pip install --break-system-packages face_recognition

# Install python-multipart
python3 -m pip install --break-system-packages python-multipart

# Install with all recommended flags
python3 -m pip install --no-cache-dir --break-system-packages --no-warn-script-location face_recognition
```

**If face_recognition fails, install dependencies first:**
```bash
# Install dlib dependencies
sudo apt install -y libdlib-dev cmake libopenblas-dev liblapack-dev

# Then install face_recognition
python3 -m pip install --break-system-packages face_recognition
```

**Note:** Building dlib can take 10-30 minutes on Raspberry Pi.

**Verification:**
```bash
python3 -c "import face_recognition; print('✅ face_recognition installed')"
```

## Quick Fix All Errors

Run these commands to fix all common errors:

```bash
cd ~/RaspberryPie5

# 1. Fix permissions
chmod +x fix_permissions.sh
./fix_permissions.sh

# 2. Install missing python-multipart
python3 -m pip install --break-system-packages python-multipart

# 3. Verify installations
python3 -c "import multipart; print('✅ python-multipart OK')"
python3 -c "from picamera2 import Picamera2; print('✅ picamera2 OK')"

# 4. Test API server
./run_api.sh
```

## Verification Checklist

After fixing errors, verify everything works:

```bash
# 1. Check script permissions
ls -l run.sh run_api.sh run_enroll.sh
# Should all show: -rwxr-xr-x

# 2. Test Python imports
python3 -c "from picamera2 import Picamera2; print('✅ picamera2')"
python3 -c "from ultralytics import YOLO; print('✅ ultralytics')"
python3 -c "import multipart; print('✅ python-multipart')"

# 3. Test API server starts
./run_api.sh
# Should start without errors

# 4. Test face detection
./run.sh
# Should start without permission errors
```

## Still Having Issues?

1. **Check logs:** Look in `logs/` directory for error logs
2. **Re-run setup:** `./scripts/setup.sh` (it's safe to run multiple times)
3. **Check documentation:** See [RASPBERRY_PI_SETUP_GUIDE.md](docs/RASPBERRY_PI_SETUP_GUIDE.md)

---

**Last Updated:** 2024

