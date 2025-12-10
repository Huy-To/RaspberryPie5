# API Reference for n8n Integration

Complete list of all available API endpoints for the Raspberry Pi 5 Face Detection & Recognition System.

**Base URL:** `http://raspberrypi.local:8000` (or your Pi's IP address)

---

## 📋 Table of Contents

1. [GET / - API Information](#get---api-information)
2. [GET /health - Health Check](#get-health---health-check)
3. [POST /event - Detection Event](#post-event---detection-event)
4. [POST /training-clip - Training Clip Metadata](#post-training-clip---training-clip-metadata)
5. [POST /unknown-person-alert - Unknown Person Alert](#post-unknown-person-alert---unknown-person-alert)

---

## GET / - API Information

**Description:** Returns API information and available endpoints.

**Method:** `GET`

**URL:** `http://raspberrypi.local:8000/`

**Headers:** None required

**Query Parameters:** None

**Request Body:** None

**Response:** `200 OK`

```json
{
  "name": "Raspberry Pi Face Detection API",
  "version": "1.0.0",
  "endpoints": {
    "POST /event": "Receive detection events",
    "POST /training-clip": "Receive training clip metadata",
    "GET /health": "Health check",
    "GET /": "API information"
  }
}
```

**n8n Usage:**
- Use **HTTP Request** node with method `GET`
- Use to verify API is running and discover available endpoints
- No authentication required

**Example n8n HTTP Request Node:**
```
Method: GET
URL: http://raspberrypi.local:8000/
```

---

## GET /health - Health Check

**Description:** Returns API health status and webhook configuration.

**Method:** `GET`

**URL:** `http://raspberrypi.local:8000/health`

**Headers:** None required

**Query Parameters:** None

**Request Body:** None

**Response:** `200 OK`

```json
{
  "status": "healthy",
  "webhook_enabled": true,
  "webhook_url": "http://n8n.local:5678/webhook/abc123"
}
```

**Response Fields:**
- `status` (string): Always `"healthy"` if API is running
- `webhook_enabled` (boolean): Whether n8n webhook is configured
- `webhook_url` (string|null): Configured n8n webhook URL, or `null` if not set

**n8n Usage:**
- Use **HTTP Request** node with method `GET`
- Use in monitoring workflows to check API availability
- Can be used as a trigger for health monitoring workflows
- No authentication required

**Example n8n HTTP Request Node:**
```
Method: GET
URL: http://raspberrypi.local:8000/health
```

**Example n8n Workflow:**
1. **Schedule Trigger** (every 5 minutes)
2. **HTTP Request** → GET `/health`
3. **IF** node → Check if `status === "healthy"`
4. **Send Email** → Alert if unhealthy

---

## GET /status - System Status

**Description:** Simple GET endpoint to retrieve system status. Alternative to `POST /command` with `get_status` command. Useful for n8n HTTP Request nodes using GET method.

**Method:** `GET`

**URL:** `http://raspberrypi.local:8000/status`

**Headers:** None required

**Query Parameters:** None

**Request Body:** None

**Response:** `200 OK`

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

## GET /detections - Recent Detections

**Description:** Simple GET endpoint to retrieve recent detection events. Alternative to `POST /command` with `get_recent_detections` command. Useful for n8n HTTP Request nodes using GET method.

**Method:** `GET`

**URL:** `http://raspberrypi.local:8000/detections`

**Headers:** None required

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | No | Number of detections to return (default: 10) |
| `event_type` | string | No | Filter by type: `"verified_person"` or `"unknown_person"` |

**Request Body:** None

**Response:** `200 OK`

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

**Example Requests:**

```bash
# Get 10 recent detections
curl "http://raspberrypi.local:8000/detections?limit=10"

# Get 5 verified person detections only
curl "http://raspberrypi.local:8000/detections?limit=5&event_type=verified_person"

# Get unknown person detections
curl "http://raspberrypi.local:8000/detections?event_type=unknown_person"
```

**n8n Usage:**

```
HTTP Request Node:
Method: GET
URL: http://raspberrypi.local:8000/detections?limit=10&event_type=verified_person
```

---

## POST /command - n8n Command Handler

**Description:** Handle commands from n8n. This endpoint allows n8n to send commands to the system and receive responses. Use this for bidirectional communication between n8n and the detection system.

**Method:** `POST`

**URL:** `http://raspberrypi.local:8000/command`

**Headers:**
```
Content-Type: application/json
```

**Query Parameters:** None

**Request Body:** JSON object

```json
{
  "command": "get_status",
  "parameters": {}
}
```

**Request Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `command` | string | Yes | Command to execute (see supported commands below) |
| `parameters` | object | No | Command-specific parameters (default: `{}`) |

**Supported Commands:**

### 1. `get_status`
Get system status and information.

**Request:**
```json
{
  "command": "get_status",
  "parameters": {}
}
```

**Response:**
```json
{
  "status": "success",
  "command": "get_status",
  "data": {
    "system": {
      "running": true,
      "api_version": "1.0.0",
      "webhook_enabled": true,
      "webhook_url": "http://n8n.local:5678/webhook/abc123"
    },
    "face_recognition": {
      "enabled": true,
      "enrolled_faces": 5,
      "database_path": "/path/to/known_faces.json"
    },
    "storage": {
      "frames_stored": 42,
      "frames_directory": "/path/to/frames"
    },
    "timestamp": "2024-01-15T14:30:45.123456"
  }
}
```

### 2. `get_recent_detections`
Get recent detection events.

**Request:**
```json
{
  "command": "get_recent_detections",
  "parameters": {
    "limit": 10,
    "event_type": "verified_person"
  }
}
```

**Parameters:**
- `limit` (integer, optional): Number of detections to return (default: 10)
- `event_type` (string, optional): Filter by event type (`"verified_person"`, `"unknown_person"`, or `null` for all)

**Response:**
```json
{
  "status": "success",
  "command": "get_recent_detections",
  "data": {
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
    "event_type_filter": "verified_person"
  }
}
```

### 3. `get_enrolled_faces`
Get list of all enrolled faces.

**Request:**
```json
{
  "command": "get_enrolled_faces",
  "parameters": {}
}
```

**Response:**
```json
{
  "status": "success",
  "command": "get_enrolled_faces",
  "data": {
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
}
```

### 4. `get_statistics`
Get detection statistics.

**Request:**
```json
{
  "command": "get_statistics",
  "parameters": {}
}
```

**Response:**
```json
{
  "status": "success",
  "command": "get_statistics",
  "data": {
    "statistics": {
      "total_detections": 150,
      "verified_persons": 120,
      "unknown_persons": 30,
      "by_person": {
        "John Doe": 45,
        "Jane Smith": 35,
        "Bob Johnson": 40
      }
    },
    "timestamp": "2024-01-15T14:30:45.123456"
  }
}
```

### 5. `update_config`
Update system configuration (limited parameters).

**Request:**
```json
{
  "command": "update_config",
  "parameters": {
    "camera_id": "front_door_camera",
    "alert_cooldown": 60
  }
}
```

**Allowed Parameters:**
- `camera_id` (string): Camera identifier
- `alert_cooldown` (integer): Alert cooldown in seconds

**Response:**
```json
{
  "status": "success",
  "command": "update_config",
  "message": "Configuration update received",
  "updates": {
    "camera_id": "front_door_camera",
    "alert_cooldown": 60
  },
  "note": "Configuration changes require system restart to take effect"
}
```

### 6. `test_connection`
Test API connection.

**Request:**
```json
{
  "command": "test_connection",
  "parameters": {}
}
```

**Response:**
```json
{
  "status": "success",
  "command": "test_connection",
  "message": "API is responding",
  "timestamp": "2024-01-15T14:30:45.123456",
  "api_version": "1.0.0"
}
```

**Error Response:** `400 Bad Request` (invalid command)

```json
{
  "status": "error",
  "message": "Unknown command: invalid_command",
  "available_commands": [
    "get_status",
    "get_recent_detections",
    "get_enrolled_faces",
    "get_statistics",
    "update_config",
    "test_connection"
  ]
}
```

**n8n Usage:**

### Use Case 1: Check System Status
```
HTTP Request Node:
Method: POST
URL: http://raspberrypi.local:8000/command
Body (JSON):
{
  "command": "get_status",
  "parameters": {}
}
```

### Use Case 2: Get Recent Verified Person Detections
```
HTTP Request Node:
Method: POST
URL: http://raspberrypi.local:8000/command
Body (JSON):
{
  "command": "get_recent_detections",
  "parameters": {
    "limit": 5,
    "event_type": "verified_person"
  }
}
```

### Use Case 3: Monitor Detection Statistics
```
Schedule Trigger (every hour)
  ↓
HTTP Request → POST /command (get_statistics)
  ↓
IF Node → Check if unknown_persons > threshold
  ↓
Send Alert → Security team
```

### Use Case 4: Dashboard Workflow
```
Webhook (receives detection event)
  ↓
HTTP Request → POST /command (get_status)
  ↓
HTTP Request → POST /command (get_statistics)
  ↓
Set Node → Combine data
  ↓
Send to Dashboard → Display status
```

**Example n8n Workflow:**
```
Schedule Trigger (every 5 minutes)
  ↓
HTTP Request → POST /command
  Body: {"command": "get_status"}
  ↓
IF Node → Check if system.running === false
  ↓
Branch A (Not Running):
  - Send Email → "System is not running!"
  - HTTP Request → Restart system (if API supports it)
  ↓
Branch B (Running):
  - HTTP Request → POST /command
    Body: {"command": "get_statistics"}
  - Log to Database → Store statistics
```

---

## POST /event - Detection Event

**Description:** Receives detection events and forwards them to n8n webhook (if configured). This endpoint is called internally by the detection system, but can also be called directly from n8n or other systems.

**Method:** `POST`

**URL:** `http://raspberrypi.local:8000/event`

**Headers:**
```
Content-Type: application/json
```

**Query Parameters:** None

**Request Body:** JSON object following `DetectionEvent` schema

```json
{
  "camera_id": "raspberry_pi_camera",
  "event_type": "face_detected",
  "timestamp": "2024-01-15T10:30:45.123456",
  "detections": [
    {
      "label": "face",
      "confidence": 0.95,
      "bbox": [100, 150, 200, 250],
      "name": "John Doe"
    }
  ],
  "frame_url": "http://raspberrypi.local:8000/frames/frame_20240115_103045.jpg",
  "frame_base64": null,
  "clip_url": null,
  "metadata": {
    "frame_count": 1234,
    "fps": 15.5
  }
}
```

**Request Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `camera_id` | string | Yes | Camera identifier (e.g., "frontdoor", "raspberry_pi_camera") |
| `event_type` | string | Yes | Event type: `"face_detected"`, `"person_detected"`, `"training_clip_ready"`, etc. |
| `timestamp` | string | Yes | ISO 8601 timestamp (e.g., "2024-01-15T10:30:45.123456") |
| `detections` | array | No | List of detection objects (default: `[]`) |
| `detections[].label` | string | Yes | Detection label (e.g., "face", "person") |
| `detections[].confidence` | float | Yes | Confidence score (0.0-1.0) |
| `detections[].bbox` | array[4] | Yes | Bounding box `[x1, y1, x2, y2]` |
| `detections[].name` | string\|null | No | Recognized name if face recognition enabled |
| `frame_url` | string\|null | No | URL to frame image |
| `frame_base64` | string\|null | No | Base64 encoded frame (alternative to frame_url) |
| `clip_url` | string\|null | No | URL to video clip (for training clips) |
| `metadata` | object | No | Additional metadata (default: `{}`) |

**Response:** `200 OK`

```json
{
  "status": "success",
  "message": "Event received and queued for n8n",
  "event_type": "face_detected",
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

**Error Response:** `500 Internal Server Error`

```json
{
  "detail": "Error processing event: <error message>"
}
```

**n8n Usage:**

### Use Case 1: Receive Events from Detection System (Automatic)
The detection system automatically sends events to this endpoint, which forwards them to your n8n webhook. No n8n action needed - events arrive at your webhook automatically.

### Use Case 2: Send Custom Events from n8n
Use **HTTP Request** node to send custom events:

**n8n HTTP Request Node Configuration:**
```
Method: POST
URL: http://raspberrypi.local:8000/event
Headers:
  Content-Type: application/json
Body (JSON):
{
  "camera_id": "raspberry_pi_camera",
  "event_type": "custom_event",
  "timestamp": "{{ $now.toISO() }}",
  "detections": [],
  "metadata": {
    "source": "n8n",
    "custom_field": "custom_value"
  }
}
```

### Use Case 3: Forward Events to Multiple Destinations
1. **Webhook** node receives event from detection system
2. **HTTP Request** node → POST to `/event` (forwards to another n8n instance)
3. **HTTP Request** node → POST to external API
4. **Send Email** node → Send notification

**Example n8n Workflow:**
```
Webhook (receives from detection system)
  ↓
Set node (add metadata)
  ↓
HTTP Request → POST /event (forward to another system)
  ↓
IF node → Check if recognized person
  ↓
Send Email → Alert for known person
```

---

## POST /training-clip - Training Clip Metadata

**Description:** Accepts training clip metadata and optionally a preview frame. Forwards a `training_clip_ready` event to n8n webhook.

**Method:** `POST`

**URL:** `http://raspberrypi.local:8000/training-clip`

**Headers:**
```
Content-Type: multipart/form-data
```

**Query Parameters:** None

**Request Body:** Form data (multipart/form-data)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `clip_path` | string | Yes | Path to saved clip file |
| `camera_id` | string | Yes | Camera identifier |
| `clip_url` | string | No | URL to access clip (if hosted elsewhere) |
| `duration` | float | No | Clip duration in seconds |
| `frame_count` | integer | No | Number of frames in clip |
| `metadata` | string | No | JSON string with additional metadata |
| `frame_preview` | file | No | Preview frame image (JPEG/PNG) |

**Example Request (curl):**
```bash
curl -X POST http://raspberrypi.local:8000/training-clip \
  -F "clip_path=/path/to/clip.mp4" \
  -F "camera_id=raspberry_pi_camera" \
  -F "clip_url=http://nas.local/clips/clip.mp4" \
  -F "duration=10.5" \
  -F "frame_count=300" \
  -F "metadata={\"quality\":\"high\",\"source\":\"manual\"}" \
  -F "frame_preview=@preview.jpg"
```

**Response:** `200 OK`

```json
{
  "status": "success",
  "message": "Training clip event received",
  "clip_path": "/path/to/clip.mp4",
  "frame_url": "http://raspberrypi.local:8000/frames/frame_20240115_103045.jpg"
}
```

**Response Fields:**
- `status` (string): Always `"success"`
- `message` (string): Confirmation message
- `clip_path` (string): Path to clip file
- `frame_url` (string|null): URL to preview frame if provided

**Error Response:** `500 Internal Server Error`

```json
{
  "detail": "Error processing training clip: <error message>"
}
```

**Event Sent to n8n Webhook:**
When this endpoint is called, it automatically sends a `training_clip_ready` event to the configured n8n webhook:

```json
{
  "camera_id": "raspberry_pi_camera",
  "event_type": "training_clip_ready",
  "clip_path": "/path/to/clip.mp4",
  "clip_url": "http://nas.local/clips/clip.mp4",
  "timestamp": "2024-01-15T10:30:45.123456",
  "duration": 10.5,
  "frame_count": 300,
  "metadata": {
    "quality": "high",
    "source": "manual"
  }
}
```

**n8n Usage:**

### Use Case 1: Notify When Training Clips Are Ready
1. External system calls `/training-clip` endpoint
2. Event automatically forwarded to n8n webhook
3. n8n workflow processes the event

**Example n8n Workflow:**
```
Webhook (receives training_clip_ready event)
  ↓
IF node → Check clip quality
  ↓
HTTP Request → Download clip from clip_url
  ↓
Code node → Process clip metadata
  ↓
Send Email → Notify about new training clip
```

### Use Case 2: Upload Training Clip from n8n
Use **HTTP Request** node to upload training clip metadata:

**n8n HTTP Request Node Configuration:**
```
Method: POST
URL: http://raspberrypi.local:8000/training-clip
Body Type: Form-Data
Form Fields:
  clip_path: /path/to/clip.mp4
  camera_id: raspberry_pi_camera
  clip_url: http://nas.local/clips/clip.mp4
  duration: 10.5
  frame_count: 300
  metadata: {"quality":"high","source":"n8n"}
  frame_preview: (file from previous node)
```

**Example n8n Workflow:**
```
Schedule Trigger (daily)
  ↓
HTTP Request → Download clip from storage
  ↓
Code node → Extract preview frame
  ↓
HTTP Request → POST /training-clip (upload metadata)
  ↓
Webhook → Receive training_clip_ready event
  ↓
Process training clip
```

---

## 📊 Event Types Reference

### Standard Event Types

| Event Type | Description | When Sent |
|------------|-------------|-----------|
| `face_detected` | Face detected in frame | Automatically when faces are detected |
| `verified_person_detected` | Verified person detected (95%+ confidence) | Automatically when verified persons are detected (if enabled) |
| `unknown_person_detected` | Unknown person detected | Automatically when unknown faces are detected (if enabled) |
| `person_detected` | Person detected (if person detection enabled) | When persons are detected |
| `training_clip_ready` | Training clip is ready for processing | When `/training-clip` endpoint is called |

### Custom Event Types

You can use any custom event type string. Examples:
- `motion_detected`
- `intrusion_alert`
- `face_recognized`
- `unknown_face_detected`
- `low_confidence_detection`

---

## 🔐 Authentication

Currently, the API does not require authentication. For production use, consider:

1. **Network-level security:** Use firewall rules to restrict access
2. **VPN:** Access API only through VPN
3. **API keys:** Add API key authentication (requires code modification)
4. **HTTPS:** Use reverse proxy (nginx) with SSL certificates

---

## 📝 Complete n8n Workflow Examples

### Example 1: Verified Person Access Control

```
1. Webhook Node (receives verified_person_detected events)
   ↓
2. HTTP Request → Download frame from frame_url
   ↓
3. Set Node → Extract person information
   - Name: {{ $json.metadata.person.name }}
   - Date: {{ $json.metadata.person.date }}
   - Time: {{ $json.metadata.person.time }}
   - Confidence: {{ $json.detections[0].confidence }}
   ↓
4. Database Node → Log access entry
   ↓
5. IF Node → Check if person is authorized
   ↓
6. Branch A (Authorized):
   - HTTP Request → Unlock door/gate
   - Send Email → "Access granted: {{ $json.metadata.person.name }}"
   - Send SMS → Notification to person
   ↓
7. Branch B (Not Authorized):
   - Send Alert → Security team
   - HTTP Request → Trigger alarm
   ↓
8. Save File → Store frame for records
```

### Example 2: Face Detection Alert System

```
1. Webhook Node (receives face_detected events)
   ↓
2. IF Node → Check if detections.length > 0
   ↓
3. IF Node → Check if recognized person (detections[].name !== null)
   ↓
4. Branch A (Known Person):
   - Set Node → Format message
   - Send Email → "Known person detected: {{ $json.detections[0].name }}"
   ↓
5. Branch B (Unknown Person):
   - Set Node → Format alert message
   - Send Email → "Unknown person detected!"
   - HTTP Request → POST to security system API
   ↓
6. HTTP Request → Download frame from frame_url
   ↓
7. Save File → Store frame locally
```

### Example 2: Training Clip Processing Pipeline

```
1. Webhook Node (receives training_clip_ready events)
   ↓
2. HTTP Request → Download clip from clip_url
   ↓
3. Code Node → Extract metadata
   ↓
4. IF Node → Check clip quality (duration > 5 seconds)
   ↓
5. HTTP Request → POST to ML training service
   ↓
6. Database Node → Store clip metadata
   ↓
7. Send Email → Notify training team
```

### Example 3: Multi-Camera Monitoring

```
1. Webhook Node (receives all events)
   ↓
2. Switch Node → Route by camera_id
   ↓
3. Branch "frontdoor":
   - IF Node → Check event_type === "face_detected"
   - Send SMS → Alert security
   ↓
4. Branch "backyard":
   - IF Node → Check event_type === "motion_detected"
   - HTTP Request → Trigger lights
   ↓
5. Branch "indoor":
   - Log to database
   - Generate daily report
```

---

## 🧪 Testing Endpoints

### Test Health Endpoint
```bash
curl http://raspberrypi.local:8000/health
```

### Test Event Endpoint
```bash
curl -X POST http://raspberrypi.local:8000/event \
  -H "Content-Type: application/json" \
  -d '{
    "camera_id": "test_camera",
    "event_type": "face_detected",
    "timestamp": "2024-01-15T10:30:45.123456",
    "detections": [
      {
        "label": "face",
        "confidence": 0.95,
        "bbox": [100, 150, 200, 250],
        "name": "Test Person"
      }
    ],
    "metadata": {
      "test": true
    }
  }'
```

### Test Training Clip Endpoint
```bash
curl -X POST http://raspberrypi.local:8000/training-clip \
  -F "clip_path=/tmp/test_clip.mp4" \
  -F "camera_id=test_camera" \
  -F "duration=10.0" \
  -F "frame_count=300" \
  -F "metadata={\"test\":true}"
```

### Test Verified Person Alert Endpoint
```bash
curl -X POST http://raspberrypi.local:8000/verified-person-alert \
  -F "camera_id=test_camera" \
  -F "person_name=John Doe" \
  -F "bbox=[100,150,200,250]" \
  -F "confidence=0.97" \
  -F "frame=@verified_person.jpg" \
  -F "date=2024-01-15" \
  -F "time_str=14:30:45" \
  -F "metadata={\"location\":\"front_door\",\"test\":true}"
```

### Test Unknown Person Alert Endpoint
```bash
curl -X POST http://raspberrypi.local:8000/unknown-person-alert \
  -F "camera_id=test_camera" \
  -F "bbox=[100,150,200,250]" \
  -F "confidence=0.95" \
  -F "frame=@unknown_person.jpg" \
  -F "metadata={\"location\":\"front_door\",\"test\":true}"
```

---

## 📚 Additional Resources

- **API Guide:** See `API_GUIDE.md` for setup instructions
- **README:** See `README.md` for system overview
- **FastAPI Docs:** Visit `http://raspberrypi.local:8000/docs` for interactive API documentation (Swagger UI)
- **ReDoc:** Visit `http://raspberrypi.local:8000/redoc` for alternative API documentation

---

## ⚠️ Important Notes

1. **Frame Storage:** Frames are stored in `frames/` directory (keeps last 100). Ensure sufficient disk space.

2. **Webhook Timeout:** Default timeout is 5 seconds. Adjust in `api_server.py` if needed.

3. **Event Queue:** Events are queued asynchronously. If n8n is unreachable, events may be lost (consider implementing persistent queue).

4. **Rate Limiting:** No rate limiting implemented. Consider adding if needed for production.

5. **Frame URLs:** Frame URLs only work if `API_FRAME_BASE_URL` is configured and API server is accessible.

6. **Large Payloads:** Avoid sending large base64-encoded frames. Use `frame_url` instead.

---

## 🐛 Troubleshooting

**Problem:** Endpoint returns 404
- **Solution:** Ensure API server is running (`API_SERVER_ENABLED = True`)

**Problem:** Events not reaching n8n
- **Solution:** Check `N8N_WEBHOOK_URL` configuration and network connectivity

**Problem:** Frame URLs not accessible
- **Solution:** Configure `API_FRAME_BASE_URL` with correct hostname/IP and port

**Problem:** Training clip endpoint fails
- **Solution:** Ensure `clip_path` exists and is accessible, check file permissions

---

**Last Updated:** 2024
**API Version:** 1.0.0

