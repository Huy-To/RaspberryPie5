# Quick Fix: CMake Error for face_recognition Installation

## The Error

```
CMake is not installed on your system!
ERROR: Failed building wheel for dlib
```

## The Solution

Install CMake and other required dependencies:

```bash
# 1. Update package list
sudo apt update

# 2. Install CMake and dlib dependencies
sudo apt install -y cmake libdlib-dev libopenblas-dev liblapack-dev

# 3. Verify CMake is installed
cmake --version

# 4. Install face_recognition
python3 -m pip install --break-system-packages face_recognition
```

## Complete Installation Steps

### Step 1: Install Dependencies

```bash
sudo apt update
sudo apt install -y cmake libdlib-dev libopenblas-dev liblapack-dev
```

### Step 2: Verify CMake

```bash
cmake --version
```

Should output something like:
```
cmake version 3.27.x
```

### Step 3: Install face_recognition

```bash
python3 -m pip install --break-system-packages face_recognition
```

**Note:** Building dlib can take 10-30 minutes on Raspberry Pi.

## Alternative: Use Setup Script

The easiest way is to use the setup script which handles everything:

```bash
cd ~/RaspberryPie5
chmod +x scripts/setup.sh
./scripts/setup.sh
```

The setup script will:
1. Install cmake and all dependencies
2. Verify cmake is installed
3. Install face_recognition automatically

## Troubleshooting

### Problem: "cmake: command not found" after installation

**Solution:**
```bash
# Check if cmake is installed
which cmake

# If not found, reinstall
sudo apt install --reinstall cmake

# Add to PATH if needed (usually not necessary)
export PATH=/usr/bin:$PATH
```

### Problem: Still getting CMake error

**Check:**
1. **Verify cmake works:**
   ```bash
   cmake --version
   ```

2. **Check for broken cmake in Python paths:**
   ```bash
   which cmake
   # Should show: /usr/bin/cmake
   # NOT something like: /usr/local/lib/python3.x/site-packages/cmake
   ```

3. **If broken cmake found, remove it:**
   ```bash
   # Find broken cmake
   find ~/.local -name cmake 2>/dev/null
   # Remove if found in Python paths
   ```

### Problem: dlib build takes too long

**This is normal!** Building dlib from source on Raspberry Pi can take:
- **10-30 minutes** depending on Pi model
- **Even longer** on older Pi models

**Tips:**
- Let it run - don't interrupt
- Use a stable power supply
- Ensure adequate cooling
- Consider running overnight

## Verification

After installation, verify it works:

```bash
python3 -c "import face_recognition; print('✅ face_recognition installed')"
```

## Summary

✅ **Install cmake:** `sudo apt install -y cmake`  
✅ **Install dependencies:** `sudo apt install -y libdlib-dev libopenblas-dev liblapack-dev`  
✅ **Install face_recognition:** `python3 -m pip install --break-system-packages face_recognition`  
✅ **Be patient:** Building dlib takes 10-30 minutes  

---

**See Also:**
- [FIX_ERRORS.md](FIX_ERRORS.md) - Complete error fixing guide
- [QUICK_FIX_FACE_RECOGNITION.md](QUICK_FIX_FACE_RECOGNITION.md) - face_recognition installation guide

