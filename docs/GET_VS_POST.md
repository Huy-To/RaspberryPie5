# GET vs POST: When to Use Each Method

This guide explains when to use GET vs POST methods for n8n integration.

## Quick Answer

### For n8n Webhook (Receiving Events FROM System)
**✅ Use POST** - The webhook node must be configured as POST to receive events.

### For n8n HTTP Request (Querying System)
**Both GET and POST available** - Choose based on your needs:
- **GET** - Simple queries (status, recent detections)
- **POST** - Complex commands with parameters

---

## Detailed Explanation

### 1. n8n Webhook Node (Receiving Events)

**Purpose:** Receive events FROM the Raspberry Pi system TO n8n

**Method:** **POST** (Required)

**Why POST?**
- The system sends events with JSON payloads containing detection data
- POST supports request bodies with complex data structures
- Webhooks are designed to receive POST requests

**Configuration:**
```
n8n Webhook Node:
Method: POST
Path: /webhook/your-unique-id
```

**What the system sends:**
```json
{
  "camera_id": "raspberry_pi_camera",
  "event_type": "verified_person_detected",
  "timestamp": "2024-01-15T14:30:45.123456",
  "detections": [...],
  "frame_url": "http://raspberrypi.local:8000/frames/verified_John_Doe.jpg",
  "metadata": {...}
}
```

---

### 2. n8n HTTP Request Node (Querying System)

**Purpose:** Query the Raspberry Pi system FROM n8n

**Methods Available:** Both GET and POST

#### Option A: GET Endpoints (Simple Queries)

**Use GET when:**
- You need simple status checks
- You want to retrieve recent detections
- You prefer URL query parameters
- You don't need complex request bodies

**Available GET Endpoints:**

1. **GET /health** - Health check
   ```
   http://raspberrypi.local:8000/health
   ```

2. **GET /status** - System status
   ```
   http://raspberrypi.local:8000/status
   ```

3. **GET /detections** - Recent detections
   ```
   http://raspberrypi.local:8000/detections?limit=10&event_type=verified_person
   ```

**n8n Configuration Example:**
```
HTTP Request Node:
Method: GET
URL: http://raspberrypi.local:8000/status
```

#### Option B: POST Endpoints (Complex Commands)

**Use POST when:**
- You need to send complex commands with parameters
- You want structured request bodies
- You need more control over the request

**Available POST Endpoints:**

1. **POST /command** - Execute commands
   ```json
   {
     "command": "get_status",
     "parameters": {}
   }
   ```

2. **POST /event** - Send detection events (internal use)

3. **POST /verified-person-alert** - Send verified person alert

4. **POST /unknown-person-alert** - Send unknown person alert

**n8n Configuration Example:**
```
HTTP Request Node:
Method: POST
URL: http://raspberrypi.local:8000/command
Body Type: JSON
Body:
{
  "command": "get_statistics",
  "parameters": {}
}
```

---

## Comparison Table

| Feature | GET | POST |
|---------|-----|------|
| **Request Body** | ❌ No | ✅ Yes |
| **URL Parameters** | ✅ Yes (query params) | ✅ Yes |
| **Complexity** | Simple | Complex |
| **Use Case** | Status checks, simple queries | Commands, complex operations |
| **n8n Setup** | Easier (just URL) | More setup (body required) |
| **Examples** | `/status`, `/detections?limit=10` | `/command` with JSON body |

---

## Practical Examples

### Example 1: Check System Health (GET)

**n8n Workflow:**
1. **Schedule Trigger** (every 5 minutes)
2. **HTTP Request** (GET)
   - URL: `http://raspberrypi.local:8000/health`
3. **IF** node → Check `status === "healthy"`
4. **Send Email** → Alert if unhealthy

**Why GET?** Simple status check, no parameters needed.

---

### Example 2: Get Recent Verified Person Detections (GET)

**n8n Workflow:**
1. **Schedule Trigger** (every hour)
2. **HTTP Request** (GET)
   - URL: `http://raspberrypi.local:8000/detections?limit=5&event_type=verified_person`
3. **Process** detections array
4. **Send Notification** for each detection

**Why GET?** Simple query with URL parameters.

---

### Example 3: Execute Complex Command (POST)

**n8n Workflow:**
1. **Manual Trigger** (button)
2. **HTTP Request** (POST)
   - URL: `http://raspberrypi.local:8000/command`
   - Body:
     ```json
     {
       "command": "update_config",
       "parameters": {
         "alert_cooldown": 120
       }
     }
     ```
3. **Display** response

**Why POST?** Complex command with structured parameters.

---

## Recommendation

### For Most Use Cases: Use GET

**GET endpoints are simpler and easier to use in n8n:**
- ✅ No need to configure request body
- ✅ Easy to test in browser
- ✅ Works well with n8n's HTTP Request node
- ✅ Sufficient for most queries

**Use GET for:**
- Health checks
- Status queries
- Recent detections
- Simple data retrieval

### Use POST When:

- You need complex commands with nested parameters
- You're sending large amounts of data
- You need to update system configuration
- GET query parameters become too long/complex

---

## Summary

| Scenario | Method | Endpoint |
|----------|--------|----------|
| **Receive events FROM system** | POST | n8n Webhook (configured in n8n) |
| **Check health** | GET | `/health` |
| **Get status** | GET | `/status` |
| **Get recent detections** | GET | `/detections?limit=10` |
| **Execute complex command** | POST | `/command` |
| **Send alerts** | POST | `/verified-person-alert` or `/unknown-person-alert` |

---

**See Also:**
- [API Configuration Guide](API_CONFIGURATION.md) - Complete setup guide
- [API Reference](API_REFERENCE.md) - Full endpoint documentation

