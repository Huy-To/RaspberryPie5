# HTTP API Usage Guide

Complete guide on how to use the HTTP API for the Raspberry Pi 5 Face Detection & Recognition System.

**Base URL:** `http://raspberrypi.local:8000` (or your Pi's IP address, e.g., `http://192.168.1.50:8000`)

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [GET Endpoints (Read Operations)](#get-endpoints-read-operations)
3. [POST Endpoints (Write Operations)](#post-endpoints-write-operations)
4. [n8n Integration](#n8n-integration)
5. [Code Examples](#code-examples)
6. [Common Use Cases](#common-use-cases)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. Start the API Server

```bash
cd ~/RaspberryPie5
./run_api.sh
```

Or with webhook URL:
```bash
./run_api.sh --webhook-url "https://your-n8n-webhook-url"
```

### 2. Test the API

```bash
# Check if API is running
curl http://localhost:8000/health

# Get API information
curl http://localhost:8000/
```

### 3. Basic Usage

**Get system status:**
```bash
curl http://localhost:8000/status
```

**Get recent detections:**
```bash
curl "http://localhost:8000/detections?limit=10"
```

---

## GET Endpoints (Read Operations)

All GET endpoints are simple HTTP requests - perfect for n8n HTTP Request nodes!

### 1. GET / - API Information

**Description:** Get API information and list of all endpoints

**URL:** `http://raspberrypi.local:8000/`

**Method:** `GET`

**Example:**
```bash
curl http://raspberrypi.local:8000/
```

**Response:**
```json
{
  "name": "Raspberry Pi Face Detection API",
  "version": "1.0.0",
  "description": "RESTful API - All read operations use GET, write operations use POST",
  "endpoints": {
    "GET /": "API information",
    "GET /health": "Health check",
    "GET /status": "System status",
    "GET /detections": "Recent detections (?limit=10&event_type=verified_person)",
    "GET /enrolled-faces": "List enrolled faces",
    "GET /statistics": "Detection statistics",
    "GET /config": "Current configuration",
    "POST /unknown-person-alert": "Send unknown person alert (multipart/form-data)",
    "POST /verified-person-alert": "Send verified person alert (multipart/form-data)"
  }
}
```

---

### 2. GET /health - Health Check

**Description:** Check if API is running and webhook is configured

**URL:** `http://raspberrypi.local:8000/health`

**Method:** `GET`

**Example:**
```bash
curl http://raspberrypi.local:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "webhook_enabled": true,
  "webhook_url": "https://your-webhook-url"
}
```

**n8n Usage:**
```
HTTP Request Node:
Method: GET
URL: http://raspberrypi.local:8000/health
```

---

### 3. GET /status - System Status

**Description:** Get complete system status including face recognition, storage, and webhook info

**URL:** `http://raspberrypi.local:8000/status`

**Method:** `GET`

**Example:**
```bash
curl http://raspberrypi.local:8000/status
```

**Response:**
```json
{
  "status": "success",
  "system": {
    "running": true,
    "api_version": "1.0.0",
    "webhook_enabled": true
  },
  "face_recognition": {
    "enabled": true,
    "enrolled_faces": 5
  },
  "storage": {
    "frames_stored": 42
  },
  "timestamp": "2024-01-15T14:30:45.123456"
}
```

**n8n Usage:**
```
HTTP Request Node:
Method: GET
URL: http://raspberrypi.local:8000/status
```

---

### 4. GET /detections - Recent Detections

**Description:** Get recent detection events with optional filtering

**URL:** `http://raspberrypi.local:8000/detections`

**Query Parameters:**
- `limit` (optional, default: 10) - Number of detections to return
- `event_type` (optional) - Filter by type: `"verified_person"` or `"unknown_person"`

**Examples:**

```bash
# Get 10 recent detections
curl "http://raspberrypi.local:8000/detections?limit=10"

# Get 20 recent detections
curl "http://raspberrypi.local:8000/detections?limit=20"

# Get only verified person detections
curl "http://raspberrypi.local:8000/detections?limit=10&event_type=verified_person"

# Get only unknown person detections
curl "http://raspberrypi.local:8000/detections?event_type=unknown_person"
```

**Response:**
```json
{
  "status": "success",
  "detections": [
    {
      "type": "verified_person",
      "person_name": "John Doe",
      "frame_filename": "verified_John_Doe_20240115_143045.jpg",
      "frame_url": "http://raspberrypi.local:8000/frames/verified_John_Doe_20240115_143045.jpg",
      "timestamp": "2024-01-15T14:30:45.123456"
    }
  ],
  "count": 1,
  "limit": 10,
  "event_type_filter": null
}
```

**n8n Usage:**
```
HTTP Request Node:
Method: GET
URL: http://raspberrypi.local:8000/detections?limit=10&event_type=verified_person
```

---

### 5. GET /enrolled-faces - List Enrolled Faces

**Description:** Get list of all enrolled faces in the database

**URL:** `http://raspberrypi.local:8000/enrolled-faces`

**Method:** `GET`

**Example:**
```bash
curl http://raspberrypi.local:8000/enrolled-faces
```

**Response:**
```json
{
  "status": "success",
  "faces": [
    {
      "name": "John Doe",
      "encoding_count": 15
    },
    {
      "name": "Jane Smith",
      "encoding_count": 12
    }
  ],
  "total_count": 2
}
```

**n8n Usage:**
```
HTTP Request Node:
Method: GET
URL: http://raspberrypi.local:8000/enrolled-faces
```

---

### 6. GET /statistics - Detection Statistics

**Description:** Get detection statistics including totals and breakdown by person

**URL:** `http://raspberrypi.local:8000/statistics`

**Method:** `GET`

**Example:**
```bash
curl http://raspberrypi.local:8000/statistics
```

**Response:**
```json
{
  "status": "success",
  "statistics": {
    "total_detections": 150,
    "verified_persons": 100,
    "unknown_persons": 50,
    "by_person": {
      "John Doe": 45,
      "Jane Smith": 35,
      "Bob Wilson": 20
    }
  },
  "timestamp": "2024-01-15T14:30:45.123456"
}
```

**n8n Usage:**
```
HTTP Request Node:
Method: GET
URL: http://raspberrypi.local:8000/statistics
```

---

### 7. GET /config - Current Configuration

**Description:** Get current system configuration

**URL:** `http://raspberrypi.local:8000/config`

**Method:** `GET`

**Example:**
```bash
curl http://raspberrypi.local:8000/config
```

**Response:**
```json
{
  "status": "success",
  "config": {
    "webhook_enabled": true,
    "webhook_url": "https://your-webhook-url",
    "api_version": "1.0.0",
    "frame_storage": "/home/pi/RaspberryPie5/frames",
    "face_database": "/home/pi/RaspberryPie5/known_faces.json"
  }
}
```

**n8n Usage:**
```
HTTP Request Node:
Method: GET
URL: http://raspberrypi.local:8000/config
```

---

## POST Endpoints (Write Operations)

POST endpoints are used for sending data (alerts with images).

### 8. POST /unknown-person-alert - Send Unknown Person Alert

**Description:** Send an alert for an unknown person detection with captured image

**URL:** `http://raspberrypi.local:8000/unknown-person-alert`

**Method:** `POST`

**Content-Type:** `multipart/form-data`

**Form Fields:**
- `camera_id` (required) - Camera identifier (string)
- `bbox` (required) - Bounding box as JSON string: `"[x1, y1, x2, y2]"`
- `confidence` (required) - Detection confidence (float, 0.0-1.0)
- `frame` (required) - Image file (JPEG/PNG)
- `metadata` (optional) - Additional metadata as JSON string

**Example (curl):**
```bash
curl -X POST http://raspberrypi.local:8000/unknown-person-alert \
  -F "camera_id=front_door_camera" \
  -F "bbox=[100,150,300,400]" \
  -F "confidence=0.85" \
  -F "frame=@/path/to/image.jpg" \
  -F 'metadata={"location":"front_door","zone":"entrance"}'
```

**Response:**
```json
{
  "status": "success",
  "message": "Unknown person alert sent",
  "event_type": "unknown_person_detected",
  "frame_url": "http://raspberrypi.local:8000/frames/unknown_person_20240115_143045.jpg",
  "timestamp": "2024-01-15T14:30:45.123456"
}
```

**n8n Usage:**
```
HTTP Request Node:
Method: POST
URL: http://raspberrypi.local:8000/unknown-person-alert
Body Type: Form-Data
Parameters:
  - camera_id: front_door_camera
  - bbox: [100,150,300,400]
  - confidence: 0.85
  - frame: (File from previous node)
  - metadata: {"location":"front_door"}
```

---

### 9. POST /verified-person-alert - Send Verified Person Alert

**Description:** Send an alert for a verified person detection (95%+ confidence) with image and person info

**URL:** `http://raspberrypi.local:8000/verified-person-alert`

**Method:** `POST`

**Content-Type:** `multipart/form-data`

**Form Fields:**
- `camera_id` (required) - Camera identifier (string)
- `person_name` (required) - Name of verified person (string)
- `bbox` (required) - Bounding box as JSON string: `"[x1, y1, x2, y2]"`
- `confidence` (required) - Must be >= 0.95 (float)
- `frame` (required) - Image file (JPEG/PNG)
- `date` (optional) - Date string (YYYY-MM-DD format)
- `time_str` (optional) - Time string (HH:MM:SS format)
- `metadata` (optional) - Additional metadata as JSON string

**Example (curl):**
```bash
curl -X POST http://raspberrypi.local:8000/verified-person-alert \
  -F "camera_id=front_door_camera" \
  -F "person_name=John Doe" \
  -F "bbox=[100,150,300,400]" \
  -F "confidence=0.95" \
  -F "frame=@/path/to/image.jpg" \
  -F "date=2024-01-15" \
  -F "time_str=14:30:45"
```

**Response:**
```json
{
  "status": "success",
  "message": "Verified person alert sent",
  "event_type": "verified_person_detected",
  "person_name": "John Doe",
  "confidence": 0.95,
  "date": "2024-01-15",
  "time": "14:30:45",
  "frame_url": "http://raspberrypi.local:8000/frames/verified_John_Doe_20240115_143045.jpg",
  "timestamp": "2024-01-15T14:30:45.123456"
}
```

**n8n Usage:**
```
HTTP Request Node:
Method: POST
URL: http://raspberrypi.local:8000/verified-person-alert
Body Type: Form-Data
Parameters:
  - camera_id: front_door_camera
  - person_name: John Doe
  - bbox: [100,150,300,400]
  - confidence: 0.95
  - frame: (File from previous node)
  - date: 2024-01-15
  - time_str: 14:30:45
```

---

## n8n Integration

### Basic GET Request in n8n

**Step 1:** Add HTTP Request Node

**Step 2:** Configure:
- **Method:** `GET`
- **URL:** `http://raspberrypi.local:8000/status`
- **Authentication:** None (or configure if needed)

**Step 3:** Execute node - you'll get the JSON response

### GET Request with Query Parameters

**Example:** Get recent verified person detections

**Configuration:**
- **Method:** `GET`
- **URL:** `http://raspberrypi.local:8000/detections?limit=10&event_type=verified_person`

**Or use n8n expressions:**
```
http://raspberrypi.local:8000/detections?limit={{$json.limit}}&event_type={{$json.event_type}}
```

### POST Request with Form Data

**Example:** Send unknown person alert

**Configuration:**
- **Method:** `POST`
- **URL:** `http://raspberrypi.local:8000/unknown-person-alert`
- **Body Type:** `Form-Data` or `Multipart-Form-Data`
- **Parameters:**
  ```
  camera_id: front_door
  bbox: [100,150,300,400]
  confidence: 0.85
  frame: (Binary data from previous node)
  ```

### Complete n8n Workflow Example

**Workflow:** Monitor system and send alerts

```
1. Schedule Trigger (every 5 minutes)
   ↓
2. HTTP Request → GET /health
   ↓
3. IF Node → Check if status === "healthy"
   ↓
4. Branch A (Unhealthy):
   - Send Email → Alert admin
   ↓
5. Branch B (Healthy):
   - HTTP Request → GET /statistics
   - IF Node → Check if unknown_persons > threshold
   - Send Notification → Security alert
```

---

## Code Examples

### Python

#### GET Request Example

```python
import requests

# Get system status
response = requests.get('http://raspberrypi.local:8000/status')
data = response.json()
print(f"Enrolled faces: {data['face_recognition']['enrolled_faces']}")

# Get recent detections
response = requests.get(
    'http://raspberrypi.local:8000/detections',
    params={'limit': 10, 'event_type': 'verified_person'}
)
detections = response.json()['detections']
for detection in detections:
    print(f"{detection['person_name']} detected at {detection['timestamp']}")
```

#### POST Request Example

```python
import requests

# Send unknown person alert
with open('unknown_person.jpg', 'rb') as f:
    files = {'frame': ('unknown_person.jpg', f, 'image/jpeg')}
    data = {
        'camera_id': 'front_door',
        'bbox': '[100, 150, 300, 400]',
        'confidence': '0.85',
        'metadata': '{"location": "front_door"}'
    }
    response = requests.post(
        'http://raspberrypi.local:8000/unknown-person-alert',
        files=files,
        data=data
    )
    print(response.json())
```

### JavaScript/Node.js

#### GET Request Example

```javascript
const axios = require('axios');

// Get system status
async function getStatus() {
    try {
        const response = await axios.get('http://raspberrypi.local:8000/status');
        console.log('Enrolled faces:', response.data.face_recognition.enrolled_faces);
    } catch (error) {
        console.error('Error:', error.message);
    }
}

// Get recent detections
async function getDetections(limit = 10, eventType = null) {
    const params = { limit };
    if (eventType) params.event_type = eventType;
    
    const response = await axios.get(
        'http://raspberrypi.local:8000/detections',
        { params }
    );
    return response.data.detections;
}
```

#### POST Request Example

```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

// Send unknown person alert
async function sendUnknownPersonAlert(imagePath) {
    const form = new FormData();
    form.append('camera_id', 'front_door');
    form.append('bbox', '[100, 150, 300, 400]');
    form.append('confidence', '0.85');
    form.append('frame', fs.createReadStream(imagePath));
    
    const response = await axios.post(
        'http://raspberrypi.local:8000/unknown-person-alert',
        form,
        { headers: form.getHeaders() }
    );
    return response.data;
}
```

### cURL Examples

```bash
# Get health
curl http://raspberrypi.local:8000/health

# Get status
curl http://raspberrypi.local:8000/status

# Get detections
curl "http://raspberrypi.local:8000/detections?limit=10&event_type=verified_person"

# Get enrolled faces
curl http://raspberrypi.local:8000/enrolled-faces

# Get statistics
curl http://raspberrypi.local:8000/statistics

# Send unknown person alert
curl -X POST http://raspberrypi.local:8000/unknown-person-alert \
  -F "camera_id=front_door" \
  -F "bbox=[100,150,300,400]" \
  -F "confidence=0.85" \
  -F "frame=@image.jpg"

# Send verified person alert
curl -X POST http://raspberrypi.local:8000/verified-person-alert \
  -F "camera_id=front_door" \
  -F "person_name=John Doe" \
  -F "bbox=[100,150,300,400]" \
  -F "confidence=0.95" \
  -F "frame=@image.jpg"
```

---

## Common Use Cases

### Use Case 1: Monitor System Health

**Goal:** Check if system is running every 5 minutes

**n8n Workflow:**
```
Schedule Trigger (every 5 minutes)
  ↓
HTTP Request → GET /health
  ↓
IF Node → status !== "healthy"
  ↓
Send Email → Alert admin
```

**Python:**
```python
import requests
import time

while True:
    try:
        response = requests.get('http://raspberrypi.local:8000/health', timeout=5)
        if response.json()['status'] != 'healthy':
            send_alert('System unhealthy!')
    except:
        send_alert('Cannot reach API server!')
    time.sleep(300)  # 5 minutes
```

### Use Case 2: Dashboard - Get All Data

**Goal:** Display system status, statistics, and recent detections

**n8n Workflow:**
```
Manual Trigger (button)
  ↓
HTTP Request → GET /status
HTTP Request → GET /statistics
HTTP Request → GET /detections?limit=10
  ↓
Set Node → Combine all data
  ↓
Display → Dashboard
```

**Python:**
```python
import requests

def get_dashboard_data():
    base_url = 'http://raspberrypi.local:8000'
    
    status = requests.get(f'{base_url}/status').json()
    stats = requests.get(f'{base_url}/statistics').json()
    detections = requests.get(f'{base_url}/detections?limit=10').json()
    
    return {
        'status': status,
        'statistics': stats['statistics'],
        'recent_detections': detections['detections']
    }
```

### Use Case 3: Alert on Unknown Person

**Goal:** When unknown person detected, send alert with image

**n8n Workflow:**
```
Webhook (receives detection event)
  ↓
IF Node → event_type === "unknown_person_detected"
  ↓
HTTP Request → GET frame_url (download image)
  ↓
Send Email → Alert with image attachment
Send Slack → Notification
```

### Use Case 4: Daily Statistics Report

**Goal:** Send daily report of detection statistics

**n8n Workflow:**
```
Schedule Trigger (daily at 9 AM)
  ↓
HTTP Request → GET /statistics
  ↓
Code Node → Format report
  ↓
Send Email → Daily report
```

**Python:**
```python
import requests
from datetime import datetime

def send_daily_report():
    response = requests.get('http://raspberrypi.local:8000/statistics')
    stats = response.json()['statistics']
    
    report = f"""
    Daily Detection Report - {datetime.now().strftime('%Y-%m-%d')}
    
    Total Detections: {stats['total_detections']}
    Verified Persons: {stats['verified_persons']}
    Unknown Persons: {stats['unknown_persons']}
    
    By Person:
    """
    for name, count in stats['by_person'].items():
        report += f"  - {name}: {count}\n"
    
    send_email('Daily Report', report)
```

---

## Troubleshooting

### Problem: Cannot Connect to API

**Symptoms:** Connection refused, timeout errors

**Solutions:**
1. **Check if API server is running:**
   ```bash
   ps aux | grep api_server.py
   ```

2. **Start API server:**
   ```bash
   ./run_api.sh
   ```

3. **Check firewall:**
   ```bash
   sudo ufw status
   # Allow port 8000 if needed
   sudo ufw allow 8000
   ```

4. **Test locally first:**
   ```bash
   curl http://localhost:8000/health
   ```

### Problem: GET Request Returns Empty Data

**Check:**
1. **Verify endpoint exists:**
   ```bash
   curl http://raspberrypi.local:8000/
   ```

2. **Check query parameters:**
   ```bash
   # Wrong - missing quotes for query params
   curl http://raspberrypi.local:8000/detections?limit=10&event_type=verified_person
   
   # Correct - use quotes
   curl "http://raspberrypi.local:8000/detections?limit=10&event_type=verified_person"
   ```

### Problem: POST Request Fails

**Check:**
1. **Content-Type:** Must be `multipart/form-data` for file uploads
2. **Bbox format:** Must be JSON string: `"[100,150,300,400]"` not array
3. **File exists:** Verify image file path is correct
4. **Confidence:** For verified person, must be >= 0.95

**Example of correct format:**
```bash
curl -X POST http://raspberrypi.local:8000/unknown-person-alert \
  -F "camera_id=test" \
  -F "bbox=[0,0,100,100]" \
  -F "confidence=0.5" \
  -F "frame=@test.jpg"
```

### Problem: n8n Cannot Access API

**Solutions:**
1. **Use IP address instead of hostname:**
   ```
   http://192.168.1.50:8000/status
   ```

2. **Check network connectivity:**
   ```bash
   ping raspberrypi.local
   ```

3. **Verify API is accessible from n8n machine:**
   ```bash
   curl http://raspberrypi.local:8000/health
   ```

### Problem: Frame URLs Not Working

**Check:**
1. **API_FRAME_BASE_URL configured:** Check config in `raspberry_pi_face_detection.py`
2. **Frames directory exists:** `ls ~/RaspberryPie5/frames`
3. **File permissions:** Frames should be readable

---

## Quick Reference

| Endpoint | Method | Purpose | Example |
|----------|--------|---------|---------|
| `/` | GET | API info | `curl http://raspberrypi.local:8000/` |
| `/health` | GET | Health check | `curl http://raspberrypi.local:8000/health` |
| `/status` | GET | System status | `curl http://raspberrypi.local:8000/status` |
| `/detections` | GET | Recent detections | `curl "http://raspberrypi.local:8000/detections?limit=10"` |
| `/enrolled-faces` | GET | List faces | `curl http://raspberrypi.local:8000/enrolled-faces` |
| `/statistics` | GET | Statistics | `curl http://raspberrypi.local:8000/statistics` |
| `/config` | GET | Configuration | `curl http://raspberrypi.local:8000/config` |
| `/unknown-person-alert` | POST | Send alert | See POST examples above |
| `/verified-person-alert` | POST | Send alert | See POST examples above |

---

## Best Practices

1. **Always use GET for read operations** - Simple, cacheable, easy to use
2. **Use query parameters** - Keep URLs clean and readable
3. **Handle errors gracefully** - Check response status codes
4. **Use timeouts** - Prevent hanging requests
5. **Cache when appropriate** - Don't poll too frequently
6. **Use absolute paths** - For file uploads, use full paths
7. **Validate data** - Check response structure before using

---

## See Also

- [API Reference](API_REFERENCE.md) - Complete endpoint documentation
- [API Configuration Guide](API_CONFIGURATION.md) - Setup and configuration
- [API Endpoints Summary](API_ENDPOINTS_SUMMARY.md) - Quick reference
- [n8n Cloud vs Local Guide](N8N_CLOUD_VS_LOCAL.md) - Webhook setup

---

**Last Updated:** 2024

