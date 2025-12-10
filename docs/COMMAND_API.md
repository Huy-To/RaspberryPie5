# Command API Guide

This guide explains how to use the `/command` endpoint to send commands from n8n to the Raspberry Pi Face Detection System.

## Overview

The `/command` endpoint enables bidirectional communication between n8n and the detection system. n8n can send commands to query system status, retrieve data, or update configuration.

## Endpoint

**URL:** `POST http://raspberrypi.local:8000/command`

**Content-Type:** `application/json`

## Request Format

```json
{
  "command": "command_name",
  "parameters": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

## Available Commands

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
- `event_type` (string, optional): Filter by type (`"verified_person"`, `"unknown_person"`, or `null` for all)

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

## n8n Usage Examples

### Example 1: Check System Status

**HTTP Request Node Configuration:**
```
Method: POST
URL: http://raspberrypi.local:8000/command
Body Type: JSON
Body:
{
  "command": "get_status",
  "parameters": {}
}
```

### Example 2: Get Recent Verified Person Detections

**HTTP Request Node Configuration:**
```
Method: POST
URL: http://raspberrypi.local:8000/command
Body Type: JSON
Body:
{
  "command": "get_recent_detections",
  "parameters": {
    "limit": 5,
    "event_type": "verified_person"
  }
}
```

### Example 3: Monitor System Health

**Workflow:**
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
  - Send SMS → Alert admin
  ↓
Branch B (Running):
  - HTTP Request → POST /command
    Body: {"command": "get_statistics"}
  - Log to Database → Store statistics
```

### Example 4: Dashboard Data Collection

**Workflow:**
```
Schedule Trigger (every minute)
  ↓
HTTP Request → POST /command (get_status)
  ↓
HTTP Request → POST /command (get_statistics)
  ↓
HTTP Request → POST /command (get_recent_detections)
  ↓
Set Node → Combine all data
  ↓
HTTP Request → POST to dashboard API
```

### Example 5: User Command Handler

**Workflow:**
```
Webhook (receives user command)
  ↓
Switch Node → Route by command
  ↓
Branch "status":
  - HTTP Request → POST /command
    Body: {"command": "get_status"}
  - Send Response → Return status
  ↓
Branch "recent":
  - HTTP Request → POST /command
    Body: {"command": "get_recent_detections", "parameters": {"limit": 10}}
  - Send Response → Return detections
  ↓
Branch "stats":
  - HTTP Request → POST /command
    Body: {"command": "get_statistics"}
  - Send Response → Return statistics
```

## Error Handling

**Unknown Command:**
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

**Server Error:**
```json
{
  "detail": "Error processing command: <error message>"
}
```

## Testing with curl

```bash
# Test connection
curl -X POST http://raspberrypi.local:8000/command \
  -H "Content-Type: application/json" \
  -d '{"command": "test_connection", "parameters": {}}'

# Get status
curl -X POST http://raspberrypi.local:8000/command \
  -H "Content-Type: application/json" \
  -d '{"command": "get_status", "parameters": {}}'

# Get recent detections
curl -X POST http://raspberrypi.local:8000/command \
  -H "Content-Type: application/json" \
  -d '{"command": "get_recent_detections", "parameters": {"limit": 5}}'
```

## Best Practices

1. **Use `test_connection` first** to verify API is accessible
2. **Cache status responses** to avoid excessive API calls
3. **Handle errors gracefully** - check `status` field in response
4. **Use appropriate limits** for `get_recent_detections` to avoid large responses
5. **Filter by event_type** when you only need specific detection types

## Integration Tips

- The command API works alongside the webhook system (events flow: System → n8n)
- Use commands for querying data, webhooks for receiving events
- Commands are synchronous - you get immediate responses
- Webhooks are asynchronous - events are queued and sent in background

---

**See Also:**
- [API Reference](API_REFERENCE.md) - Complete API documentation
- [API Guide](API_GUIDE.md) - General API usage guide

