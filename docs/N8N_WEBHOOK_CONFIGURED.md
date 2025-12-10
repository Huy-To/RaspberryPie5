# n8n Webhook Configuration

## ✅ Configuration Status

Your n8n webhook URL has been **permanently configured** in the system:

```
https://huyto002.app.n8n.cloud/webhook/5314c1d4-5ffc-4d3d-8e07-c05b9e8140a5
```

---

## 📍 Where It's Configured

The webhook URL is set in `src/raspberry_pi_face_detection.py`:

```python
class Config:
    # API/n8n integration settings
    N8N_WEBHOOK_URL = "https://huyto002.app.n8n.cloud/webhook/5314c1d4-5ffc-4d3d-8e07-c05b9e8140a5"
    
    # Unknown person alert settings
    ENABLE_UNKNOWN_PERSON_ALERTS = True  # Already enabled
    
    # Verified person alert settings
    ENABLE_VERIFIED_PERSON_ALERTS = True  # Already enabled
```

---

## 🚀 What Happens Now

### Automatic Unknown Person Alerts

When an unknown person is detected:
1. ✅ System automatically sends alert to your n8n webhook
2. ✅ Includes captured image and detection details
3. ✅ Respects cooldown period (30 seconds default)

### Automatic Verified Person Alerts

When a verified person is detected (95%+ confidence):
1. ✅ System automatically sends alert to your n8n webhook
2. ✅ Includes person name, date, time, and captured image
3. ✅ Respects cooldown period (60 seconds default)

---

## 🧪 Testing

### Test Unknown Person Alert

1. **Run the system:**
   ```bash
   ./run.sh
   ```

2. **Stand in front of camera** (with a face that's not enrolled)

3. **Check console output:**
   ```
   🚨 Alien Detected! Alert sent: 1 unknown face(s) detected
   ```

4. **Check n8n** - You should receive the webhook automatically!

### Test Verified Person Alert

1. **Enroll a face first:**
   ```bash
   ./run_enroll.sh --name "Test Person" --video /path/to/video.mp4
   ```

2. **Run the system:**
   ```bash
   ./run.sh
   ```

3. **Stand in front of camera** (with enrolled face)

4. **Check console output:**
   ```
   ✅ Verified person alert sent: 1 verified face(s) detected
   ```

5. **Check n8n** - You should receive the webhook with person information!

---

## 📋 What Gets Sent to n8n

### Unknown Person Alert

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

### Verified Person Alert

```json
{
  "camera_id": "raspberry_pi_camera",
  "event_type": "verified_person_detected",
  "timestamp": "2024-01-15T10:30:45.123456",
  "detections": [
    {
      "label": "verified_person",
      "confidence": 0.96,
      "bbox": [100, 150, 200, 250],
      "name": "John Doe"
    }
  ],
  "frame_url": "http://raspberrypi.local:8000/frames/verified_John_Doe_20240115_103045_123456.jpg",
  "frame_base64": "base64_encoded_image_data",
  "metadata": {
    "frame_count": 1234,
    "fps": 15.5,
    "alert_type": "verified_person",
    "count": 1,
    "cooldown_seconds": 60,
    "person": {
      "name": "John Doe",
      "confidence": 0.96,
      "date": "2024-01-15",
      "time": "10:30:45",
      "datetime": "2024-01-15 10:30:45",
      "timestamp": "2024-01-15T10:30:45.123456"
    }
  }
}
```

---

## ⚙️ Configuration Options

You can adjust these settings in `src/raspberry_pi_face_detection.py`:

```python
# Unknown person alert settings
ENABLE_UNKNOWN_PERSON_ALERTS = True  # Enable/disable unknown alerts
UNKNOWN_PERSON_ALERT_COOLDOWN = 30  # Seconds between alerts (prevents spam)

# Verified person alert settings
ENABLE_VERIFIED_PERSON_ALERTS = True  # Enable/disable verified alerts
VERIFIED_PERSON_CONFIDENCE_THRESHOLD = 0.95  # Minimum confidence (0.0-1.0)
VERIFIED_PERSON_ALERT_COOLDOWN = 60  # Seconds between alerts (prevents spam)
```

---

## 🔧 Troubleshooting

### Problem: Alerts not being sent

**Check 1: System is running**
```bash
# Make sure the system is running
./run.sh
```

**Check 2: Webhook URL is correct**
```python
# In src/raspberry_pi_face_detection.py
N8N_WEBHOOK_URL = "https://huyto002.app.n8n.cloud/webhook/5314c1d4-5ffc-4d3d-8e07-c05b9e8140a5"
```

**Check 3: Alerts are enabled**
```python
ENABLE_UNKNOWN_PERSON_ALERTS = True
ENABLE_VERIFIED_PERSON_ALERTS = True
```

**Check 4: Check console for errors**
Look for messages like:
- `✅ n8n webhook client initialized`
- `🚨 Alien Detected! Alert sent`
- `✅ Verified person alert sent`

### Problem: Too many alerts

**Solution**: Increase cooldown period:
```python
UNKNOWN_PERSON_ALERT_COOLDOWN = 60  # Increase to 60 seconds
VERIFIED_PERSON_ALERT_COOLDOWN = 120  # Increase to 2 minutes
```

---

## 📝 Summary

✅ **Webhook URL**: Permanently configured  
✅ **Unknown Person Alerts**: Enabled and automatic  
✅ **Verified Person Alerts**: Enabled and automatic  
✅ **Auto-Initialization**: System auto-initializes n8n client  
✅ **Ready to Use**: Just run `./run.sh` and alerts will be sent automatically!  

---

**See Also:**
- [Automatic Unknown Person Alerts](AUTO_UNKNOWN_PERSON_ALERTS.md) - Detailed guide
- [API Configuration Guide](API_CONFIGURATION.md) - General API setup
- [README.md](../README.md) - Main documentation

