# How to Send Unknown Person Alerts to n8n

Complete guide on using the API to send unknown person detection alerts to n8n.

---

## Two Ways to Send Unknown Person Alerts

### Method 1: Automatic (Recommended)
The detection system automatically sends alerts when unknown persons are detected.

### Method 2: Manual API Call
Manually send alerts via the API endpoint from external systems or n8n workflows.

---

## Method 1: Automatic Unknown Person Alerts

### How It Works

When the face detection system runs, it automatically:
1. Detects faces in the camera feed
2. Attempts to recognize them against enrolled faces
3. If a face is detected but NOT recognized (unknown person):
   - Crops the frame to focus on the unknown person
   - Sends an alert to n8n with the captured image
   - Applies cooldown to prevent spam (default: 30 seconds)

### Setup Steps

**Step 1: Enable Unknown Person Alerts**

Edit `src/raspberry_pi_face_detection.py`:

```python
class Config:
    # ... other settings ...
    
    # Unknown person alert settings
    ENABLE_UNKNOWN_PERSON_ALERTS = True  # ✅ Set to True
    
    # n8n Integration
    ENABLE_N8N_INTEGRATION = True
    N8N_WEBHOOK_URL = "https://6ggkissei8ctfmonsox9d8tz.hooks.n8n.cloud/webhook/b666a94f-f3be-4f52-83c1-2cf687be6e73"
```

**Step 2: Configure Cooldown (Optional)**

```python
UNKNOWN_PERSON_ALERT_COOLDOWN = 30  # Seconds between alerts (prevents spam)
```

**Step 3: Run the Detection System**

```bash
./run.sh
```

**Step 4: Set Up n8n Webhook**

1. Open your n8n workflow
2. Add a **Webhook** node (POST method)
3. Copy the webhook URL
4. Configure it in Step 1 above

**That's it!** Unknown persons will automatically trigger alerts to n8n.

---

## Method 2: Manual API Call

Use the `/unknown-person-alert` endpoint to manually send alerts.

### Endpoint Details

**URL:** `POST http://raspberrypi.local:8000/unknown-person-alert`

**Content-Type:** `multipart/form-data`

**Required Fields:**
- `camera_id` (string) - Camera identifier
- `bbox` (string, JSON) - Bounding box `[x1, y1, x2, y2]`
- `confidence` (float) - Detection confidence (0.0-1.0)
- `frame` (file) - Image file (JPEG/PNG)

**Optional Fields:**
- `metadata` (string, JSON) - Additional metadata

### Example 1: Using curl

```bash
curl -X POST http://raspberrypi.local:8000/unknown-person-alert \
  -F "camera_id=front_door_camera" \
  -F "bbox=[100,150,300,400]" \
  -F "confidence=0.85" \
  -F "frame=@/path/to/image.jpg" \
  -F 'metadata={"location":"front_door","zone":"entrance"}'
```

### Example 2: Using Python

```python
import requests

# Prepare the image
with open('unknown_person.jpg', 'rb') as f:
    image_data = f.read()

# Prepare form data
data = {
    'camera_id': 'front_door_camera',
    'bbox': '[100, 150, 300, 400]',  # JSON string
    'confidence': 0.85,
    'metadata': '{"location": "front_door", "zone": "entrance"}'  # Optional JSON string
}

files = {
    'frame': ('unknown_person.jpg', image_data, 'image/jpeg')
}

# Send request
response = requests.post(
    'http://raspberrypi.local:8000/unknown-person-alert',
    data=data,
    files=files
)

print(response.json())
```

### Example 3: Using n8n HTTP Request Node

**In n8n:**

1. **Add HTTP Request Node**
2. **Configure:**
   - Method: `POST`
   - URL: `http://raspberrypi.local:8000/unknown-person-alert`
   - Body Type: `Form-Data` or `Multipart-Form-Data`
   - Parameters:
     ```
     camera_id: front_door_camera
     bbox: [100,150,300,400]
     confidence: 0.85
     frame: (File from previous node or binary data)
     metadata: {"location":"front_door"} (optional)
     ```

3. **Connect to previous node** that provides the image

### Example 4: Using JavaScript/Node.js

```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const form = new FormData();
form.append('camera_id', 'front_door_camera');
form.append('bbox', '[100, 150, 300, 400]');
form.append('confidence', '0.85');
form.append('frame', fs.createReadStream('unknown_person.jpg'));
form.append('metadata', JSON.stringify({ location: 'front_door' }));

axios.post('http://raspberrypi.local:8000/unknown-person-alert', form, {
  headers: form.getHeaders()
})
.then(response => {
  console.log('Alert sent:', response.data);
})
.catch(error => {
  console.error('Error:', error);
});
```

---

## Response Format

**Success Response (200 OK):**

```json
{
  "status": "success",
  "message": "Unknown person alert sent",
  "event_type": "unknown_person_detected",
  "frame_url": "http://raspberrypi.local:8000/frames/unknown_person_20240115_143045.jpg",
  "timestamp": "2024-01-15T14:30:45.123456"
}
```

**Error Response (400/500):**

```json
{
  "detail": "Error message here"
}
```

---

## Event Sent to n8n

When an alert is sent (automatically or manually), n8n receives:

```json
{
  "camera_id": "front_door_camera",
  "event_type": "unknown_person_detected",
  "timestamp": "2024-01-15T14:30:45.123456",
  "detections": [
    {
      "label": "unknown_person",
      "confidence": 0.85,
      "bbox": [100, 150, 300, 400],
      "name": null
    }
  ],
  "frame_url": "http://raspberrypi.local:8000/frames/unknown_person_20240115_143045.jpg",
  "frame_base64": null,
  "clip_url": null,
  "metadata": {
    "alert_source": "api_endpoint",
    "alert_type": "unknown_person",
    "location": "front_door",
    "zone": "entrance"
  }
}
```

---

## n8n Workflow Example

### Workflow: Unknown Person Alert Handler

**Nodes:**

1. **Webhook** (POST)
   - Receives unknown person alerts
   - Path: `/webhook/unknown-person`

2. **IF** Node
   - Condition: `{{ $json.event_type }} === "unknown_person_detected"`

3. **HTTP Request** Node
   - Method: `GET`
   - URL: `{{ $json.frame_url }}`
   - Downloads the image

4. **Send Email** Node
   - Subject: `🚨 Unknown Person Detected`
   - Body: 
     ```
     Unknown person detected at {{ $json.timestamp }}
     
     Location: {{ $json.metadata.location }}
     Confidence: {{ $json.detections[0].confidence }}
     
     Image: {{ $json.frame_url }}
     ```

5. **Slack/Telegram/Discord** Node (Optional)
   - Send notification to team

---

## Bounding Box Format

The `bbox` parameter must be a JSON string with 4 numbers:

```json
[x1, y1, x2, y2]
```

Where:
- `x1, y1` = Top-left corner coordinates
- `x2, y2` = Bottom-right corner coordinates

**Example:**
```json
[100, 150, 300, 400]
```

This represents a box:
- Starting at pixel (100, 150)
- Ending at pixel (300, 400)
- Width: 200 pixels
- Height: 250 pixels

---

## Complete Example: Full Workflow

### Scenario: External Camera System Detects Unknown Person

```python
import requests
from PIL import Image
import io

# 1. Capture image from external camera
# (Your camera capture code here)
image = capture_image()

# 2. Detect face and get bounding box
# (Your face detection code here)
bbox = [100, 150, 300, 400]  # Example coordinates
confidence = 0.85

# 3. Convert image to bytes
img_bytes = io.BytesIO()
image.save(img_bytes, format='JPEG')
img_bytes.seek(0)

# 4. Send alert to API
data = {
    'camera_id': 'external_camera_1',
    'bbox': str(bbox),  # Convert list to JSON string
    'confidence': confidence,
    'metadata': '{"source": "external_camera", "zone": "parking_lot"}'
}

files = {
    'frame': ('unknown_person.jpg', img_bytes, 'image/jpeg')
}

response = requests.post(
    'http://raspberrypi.local:8000/unknown-person-alert',
    data=data,
    files=files
)

if response.status_code == 200:
    result = response.json()
    print(f"✅ Alert sent! Frame URL: {result['frame_url']}")
else:
    print(f"❌ Error: {response.json()}")
```

---

## Troubleshooting

### Problem: Alert Not Received in n8n

**Check:**
1. ✅ Webhook URL is configured correctly
2. ✅ API server is running (`./run_api.sh`)
3. ✅ n8n webhook node is executed/active
4. ✅ Internet connectivity (for n8n cloud)

**Test:**
```bash
# Test API endpoint directly
curl -X POST http://localhost:8000/unknown-person-alert \
  -F "camera_id=test" \
  -F "bbox=[0,0,100,100]" \
  -F "confidence=0.5" \
  -F "frame=@test_image.jpg"
```

### Problem: "Invalid bbox format" Error

**Solution:** Ensure bbox is a JSON string:
```python
# ✅ Correct
bbox = "[100, 150, 300, 400]"

# ❌ Wrong
bbox = [100, 150, 300, 400]  # Must be string
```

### Problem: Image Not Uploading

**Check:**
- File exists and is readable
- File format is JPEG or PNG
- File size is reasonable (< 10MB recommended)

---

## Configuration Reference

### Automatic Alerts Configuration

```python
# src/raspberry_pi_face_detection.py

class Config:
    # Enable/disable unknown person alerts
    ENABLE_UNKNOWN_PERSON_ALERTS = True
    
    # Cooldown between alerts (seconds)
    UNKNOWN_PERSON_ALERT_COOLDOWN = 30
    
    # n8n webhook URL
    N8N_WEBHOOK_URL = "https://your-webhook-url"
    ENABLE_N8N_INTEGRATION = True
```

### API Server Configuration

```python
# src/api_server.py (configured automatically)

API_SERVER_HOST = "0.0.0.0"
API_SERVER_PORT = 8000
API_FRAME_STORAGE_DIR = "frames"
```

---

## Summary

✅ **Automatic:** Enable `ENABLE_UNKNOWN_PERSON_ALERTS = True` and run `./run.sh`

✅ **Manual API:** Use `POST /unknown-person-alert` endpoint with form data

✅ **n8n Integration:** Webhook receives `unknown_person_detected` events automatically

---

**See Also:**
- [API Reference](API_REFERENCE.md) - Complete endpoint documentation
- [API Configuration Guide](API_CONFIGURATION.md) - Setup instructions
- [Verified Person API Guide](VERIFIED_PERSON_API_GUIDE.md) - For verified person alerts

