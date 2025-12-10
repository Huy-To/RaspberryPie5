#!/usr/bin/env python3
"""
Quick test script to verify picamera2 is working
=================================================
Run this after installing picamera2 to test your camera.
"""

import sys

print("🔍 Testing picamera2 installation...")
print("=" * 50)

# Test 1: Check if picamera2 is installed
try:
    from picamera2 import Picamera2
    print("✅ picamera2 is installed")
except ImportError as e:
    print(f"❌ picamera2 is NOT installed: {e}")
    print("\nTo install:")
    print("  source face_detection_env/bin/activate")
    print("  pip install picamera2")
    sys.exit(1)

# Test 2: Try to initialize camera
print("\n📹 Testing camera initialization...")
try:
    picam2 = Picamera2()
    print("✅ Picamera2 object created")
    
    # Configure camera
    config = picam2.create_preview_configuration(
        main={"size": (640, 480), "format": "RGB888"}
    )
    picam2.configure(config)
    print("✅ Camera configured")
    
    # Start camera
    picam2.start()
    print("✅ Camera started")
    
    # Test capture
    import time
    time.sleep(0.5)  # Give camera time to start
    frame = picam2.capture_array()
    
    if frame is not None and frame.size > 0:
        height, width = frame.shape[:2]
        print(f"✅ Camera capture successful: {width}x{height}")
        print(f"   Frame shape: {frame.shape}")
        print(f"   Frame dtype: {frame.dtype}")
    else:
        print("❌ Camera capture returned empty frame")
        picam2.stop()
        sys.exit(1)
    
    # Stop camera
    picam2.stop()
    print("✅ Camera stopped successfully")
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! Your camera is ready to use.")
    print("   You can now run: ./run.sh")
    
except Exception as e:
    print(f"❌ Camera test failed: {e}")
    print("\nTroubleshooting:")
    print("  1. Make sure camera is connected")
    print("  2. Test with: rpicam-hello")
    print("  3. Enable camera: sudo raspi-config → Interface Options → Camera")
    try:
        picam2.stop()
    except:
        pass
    sys.exit(1)

