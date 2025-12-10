# API Endpoints Summary

Complete list of all available HTTP Request endpoints for n8n integration.

## ✅ All Functionalities Available via GET

All read operations use **GET** endpoints with query parameters - perfect for n8n HTTP Request nodes!

---

## GET Endpoints (Read Operations)

### 1. `GET /` - API Information
**URL:** `http://raspberrypi.local:8000/`

**Description:** Returns API information and available endpoints

**Example:**
```
GET http://raspberrypi.local:8000/
```

---

### 2. `GET /health` - Health Check
**URL:** `http://raspberrypi.local:8000/health`

**Description:** Check if API is running and webhook is configured

**Response:**
```json
{
  "status": "healthy",
  "webhook_enabled": true,
  "webhook_url": "https://..."
}
```

**n8n Usage:**
```
HTTP Request Node:
Method: GET
URL: http://raspberrypi.local:8000/health
```

---

### 3. `GET /status` - System Status
**URL:** `http://raspberrypi.local:8000/status`

**Description:** Get complete system status

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

### 4. `GET /detections` - Recent Detections
**URL:** `http://raspberrypi.local:8000/detections`

**Query Parameters:**
- `limit` (optional, default: 10) - Number of detections to return
- `event_type` (optional) - Filter by type: `"verified_person"` or `"unknown_person"`

**Examples:**
```
GET /detections
GET /detections?limit=20
GET /detections?limit=10&event_type=verified_person
GET /detections?event_type=unknown_person
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

### 5. `GET /enrolled-faces` - List Enrolled Faces
**URL:** `http://raspberrypi.local:8000/enrolled-faces`

**Description:** Get list of all enrolled faces in the database

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

### 6. `GET /statistics` - Detection Statistics
**URL:** `http://raspberrypi.local:8000/statistics`

**Description:** Get detection statistics (total, verified, unknown, by person)

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

### 7. `GET /config` - Current Configuration
**URL:** `http://raspberrypi.local:8000/config`

**Description:** Get current system configuration

**Response:**
```json
{
  "status": "success",
  "config": {
    "webhook_enabled": true,
    "webhook_url": "https://...",
    "api_version": "1.0.0",
    "frame_storage": "/path/to/frames",
    "face_database": "/path/to/known_faces.json"
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

### 8. `POST /unknown-person-alert` - Send Unknown Person Alert
**URL:** `http://raspberrypi.local:8000/unknown-person-alert`

**Content-Type:** `multipart/form-data`

**Form Fields:**
- `camera_id` (required) - Camera identifier
- `bbox` (required) - JSON string: `"[x1, y1, x2, y2]"`
- `confidence` (required) - Detection confidence (0.0-1.0)
- `frame` (required) - Image file (JPEG/PNG)
- `metadata` (optional) - JSON string with additional metadata

**Example (curl):**
```bash
curl -X POST http://raspberrypi.local:8000/unknown-person-alert \
  -F "camera_id=front_door" \
  -F "bbox=[100,150,300,400]" \
  -F "confidence=0.85" \
  -F "frame=@image.jpg"
```

**n8n Usage:**
```
HTTP Request Node:
Method: POST
URL: http://raspberrypi.local:8000/unknown-person-alert
Body Type: Form-Data
Parameters:
  - camera_id: front_door
  - bbox: [100,150,300,400]
  - confidence: 0.85
  - frame: (File from previous node)
```

---

### 9. `POST /verified-person-alert` - Send Verified Person Alert
**URL:** `http://raspberrypi.local:8000/verified-person-alert`

**Content-Type:** `multipart/form-data`

**Form Fields:**
- `camera_id` (required) - Camera identifier
- `person_name` (required) - Name of verified person
- `bbox` (required) - JSON string: `"[x1, y1, x2, y2]"`
- `confidence` (required) - Must be >= 0.95
- `frame` (required) - Image file (JPEG/PNG)
- `date` (optional) - Date string (YYYY-MM-DD)
- `time_str` (optional) - Time string (HH:MM:SS)
- `metadata` (optional) - JSON string with additional metadata

**Example (curl):**
```bash
curl -X POST http://raspberrypi.local:8000/verified-person-alert \
  -F "camera_id=front_door" \
  -F "person_name=John Doe" \
  -F "bbox=[100,150,300,400]" \
  -F "confidence=0.95" \
  -F "frame=@image.jpg"
```

**n8n Usage:**
```
HTTP Request Node:
Method: POST
URL: http://raspberrypi.local:8000/verified-person-alert
Body Type: Form-Data
Parameters:
  - camera_id: front_door
  - person_name: John Doe
  - bbox: [100,150,300,400]
  - confidence: 0.95
  - frame: (File from previous node)
```

---

## Quick Reference

| Endpoint | Method | Purpose | n8n Use Case |
|----------|--------|---------|--------------|
| `/` | GET | API info | Discover endpoints |
| `/health` | GET | Health check | Monitor system health |
| `/status` | GET | System status | Dashboard, monitoring |
| `/detections` | GET | Recent detections | View recent events |
| `/enrolled-faces` | GET | List faces | Manage face database |
| `/statistics` | GET | Statistics | Analytics, reporting |
| `/config` | GET | Configuration | Check settings |
| `/unknown-person-alert` | POST | Send alert | External system integration |
| `/verified-person-alert` | POST | Send alert | External system integration |

---

## Removed Endpoints (No Longer Needed)

These endpoints were removed to simplify the API:

- ❌ `POST /command` - Replaced with GET endpoints
- ❌ `POST /event` - Internal use only (not needed for n8n)
- ❌ `POST /training-clip` - Not needed for core functionality

---

## n8n Workflow Examples

### Example 1: Monitor System Health
```
Schedule Trigger (every 5 minutes)
  ↓
HTTP Request → GET /health
  ↓
IF Node → Check if status === "healthy"
  ↓
Send Email → Alert if unhealthy
```

### Example 2: Get Recent Verified Person Detections
```
Schedule Trigger (every hour)
  ↓
HTTP Request → GET /detections?limit=10&event_type=verified_person
  ↓
Process Array → Loop through detections
  ↓
Send Notification → For each detection
```

### Example 3: Dashboard Data
```
Manual Trigger (button)
  ↓
HTTP Request → GET /status
HTTP Request → GET /statistics
HTTP Request → GET /enrolled-faces
  ↓
Set Node → Combine data
  ↓
Display → Dashboard
```

---

## Summary

✅ **All functionalities accessible via GET**  
✅ **Simple query parameters** - No complex POST bodies needed  
✅ **Perfect for n8n HTTP Request nodes**  
✅ **Removed unnecessary endpoints**  
✅ **Clean, RESTful API structure**

