# Automatic Unknown Person Alerts to n8n

## Overview

The system now **automatically sends unknown person alerts to n8n** as soon as an unknown person is detected. No manual API calls needed!

---

## How It Works

1. **Detection**: When the system detects a face that is not recognized (marked as "Unknown")
2. **Auto-Initialization**: The system automatically initializes the n8n client if needed
3. **Alert**: Sends an alert to n8n with the captured image and detection details
4. **Cooldown**: Prevents spam by respecting the cooldown period (default: 30 seconds)

---

## Configuration

### Step 1: Set n8n Webhook URL

Edit `src/raspberry_pi_face_detection.py` and set your n8n webhook URL:

```python
class Config:
    # ... other settings ...
    
    # API/n8n integration settings
    N8N_WEBHOOK_URL = "https://your-n8n-webhook-url/webhook/your-id"
    
    # Unknown person alert settings
    ENABLE_UNKNOWN_PERSON_ALERTS = True  # Already enabled by default
    UNKNOWN_PERSON_ALERT_COOLDOWN = 30  # Seconds between alerts (prevents spam)
```

### Step 2: Ensure Face Recognition is Enabled

Unknown person detection requires face recognition to be enabled:

```python
ENABLE_FACE_RECOGNITION = True  # Must be True
```

**Note**: If face recognition is disabled, all faces will be considered "unknown" and alerts will be sent for every detection.

---

## What Gets Sent to n8n

When an unknown person is detected, the following event is automatically sent to your n8n webhook:

```json
{
  "camera_id": "raspberry_pi_camera",
  "event_type": "unknown_person_detected",
  "timestamp": "2024-01-15T10:30:45.123456",
  "detections": [
    {
      "label": "unknown_person",
      "confidence": 0.85,
      "bbox": [100, 150, 200, 250],
      "name": null
    }
  ],
  "frame_url": "http://raspberrypi.local:8000/frames/unknown_person_20240115_103045_123456.jpg",
  "frame_base64": "base64_encoded_image_data",
  "metadata": {
    "frame_count": 1234,
    "fps": 15.5,
    "alert_type": "unknown_person",
    "count": 1,
    "cooldown_seconds": 30,
    "message": "Alien Detected"
  }
}
```

---

## Automatic Features

### ✅ Auto-Initialization

If `N8N_WEBHOOK_URL` is configured but the n8n client isn't initialized, the system will automatically:
- Import required API modules
- Initialize the n8n webhook client
- Initialize frame storage
- Set up the detection event creator

**You'll see this message:**
```
ℹ️  Auto-initializing n8n client for unknown person alert...
✅ n8n client auto-initialized: https://your-webhook-url
```

### ✅ Independent Operation

Unknown person alerts work **independently** of general n8n integration:
- You don't need to enable `ENABLE_N8N_INTEGRATION` for alerts to work
- Alerts will work as long as `ENABLE_UNKNOWN_PERSON_ALERTS = True` and `N8N_WEBHOOK_URL` is set
- The system auto-enables n8n integration when alerts are enabled

### ✅ Cooldown Protection

Prevents spam by tracking alerts per unknown person:
- Default cooldown: 30 seconds
- Each unknown person (identified by bounding box position) has its own cooldown timer
- Only sends one alert per unknown person every 30 seconds (configurable)

---

## Testing

### Test 1: Check Configuration

```bash
# Run the system and check startup messages
./run.sh

# You should see:
# ✅ n8n webhook client initialized: https://your-webhook-url
# OR
# ℹ️  Auto-enabling n8n integration for unknown/verified person alerts
```

### Test 2: Trigger Unknown Person Detection

1. **Make sure no faces are enrolled** (or use a face that's not enrolled)
2. **Stand in front of the camera**
3. **Check console output** - you should see:
   ```
   🚨 Alien Detected! Alert sent: 1 unknown face(s) detected
   ```
4. **Check n8n** - you should receive the webhook with the alert data

### Test 3: Verify Cooldown

1. Trigger an unknown person alert
2. Stay in front of the camera
3. Wait less than 30 seconds - no new alert should be sent
4. Wait more than 30 seconds - a new alert should be sent

---

## Troubleshooting

### Problem: Alerts not being sent

**Check 1: Webhook URL configured?**
```python
# In src/raspberry_pi_face_detection.py
N8N_WEBHOOK_URL = "https://your-webhook-url"  # Must be set!
```

**Check 2: Alerts enabled?**
```python
ENABLE_UNKNOWN_PERSON_ALERTS = True  # Must be True
```

**Check 3: Face recognition enabled?**
```python
ENABLE_FACE_RECOGNITION = True  # Must be True for unknown detection
```

**Check 4: API packages installed?**
```bash
python3 -m pip install --break-system-packages fastapi uvicorn httpx pydantic python-multipart
```

### Problem: "n8n client not initialized" error

**Solution**: The system will auto-initialize. If it fails, check:
1. Webhook URL is correct
2. API packages are installed
3. Check console for error messages

### Problem: Too many alerts (spam)

**Solution**: Increase cooldown period:
```python
UNKNOWN_PERSON_ALERT_COOLDOWN = 60  # Increase to 60 seconds
```

### Problem: No alerts for unknown persons

**Possible causes:**
1. Face recognition is disabled - all faces will be "Unknown"
2. All faces are recognized - no unknown persons detected
3. Cooldown period hasn't expired yet
4. Webhook URL not configured

---

## Console Output Examples

### Successful Alert
```
🚨 Alien Detected! Alert sent: 1 unknown face(s) detected
```

### Auto-Initialization
```
ℹ️  Auto-initializing n8n client for unknown person alert...
✅ n8n client auto-initialized: https://your-webhook-url
🚨 Alien Detected! Alert sent: 1 unknown face(s) detected
```

### Cooldown Active
```
# No message - alert skipped due to cooldown
```

### Error
```
⚠️  Unknown person detected but N8N_WEBHOOK_URL not configured
   Set N8N_WEBHOOK_URL in config to enable automatic alerts
```

---

## Summary

✅ **Automatic**: Unknown person alerts are sent automatically when detected  
✅ **Auto-Initialize**: n8n client initializes automatically if needed  
✅ **Independent**: Works independently of general n8n integration  
✅ **Cooldown**: Built-in spam protection  
✅ **Easy Setup**: Just set `N8N_WEBHOOK_URL` and enable alerts  

---

**See Also:**
- [API Configuration Guide](API_CONFIGURATION.md) - How to configure n8n webhook
- [Unknown Person API Guide](UNKNOWN_PERSON_API_GUIDE.md) - Manual API usage
- [README.md](../README.md) - Main documentation

