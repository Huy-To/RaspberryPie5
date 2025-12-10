# API Server Configuration Guide

This guide explains how to configure the API server, including n8n webhook integration.

## Current Status

Based on your output:
- ✅ API server is running successfully on `0.0.0.0:8000`
- ⚠️ n8n webhook URL is not configured
- ✅ Frame storage is configured: `/home/pi/RaspberryPie5/frames`

## Important: GET vs POST for n8n

### For n8n Webhook (Receiving Events from System)

**Use POST method** - The system sends events TO n8n using POST requests:
- ✅ **POST** - Required for receiving webhook events with JSON data
- ❌ **GET** - Not suitable for receiving webhook events

### For n8n HTTP Request (Querying System)

**Both GET and POST available** - n8n can query the system using either:
- **GET endpoints** - Simple queries (status, recent detections)
  - `GET /status` - Get system status
  - `GET /detections?limit=10&event_type=verified_person` - Get recent detections
  - `GET /health` - Health check
  
- **POST endpoints** - Complex commands with parameters
  - `POST /command` - Execute commands (get_status, get_statistics, etc.)

## Configuration Methods

There are two ways to configure the API server:

### Method 1: Command Line Arguments (Recommended for Testing)

When running the API server standalone, you can pass configuration via command line:

```bash
# Run with webhook URL
./run_api.sh

# Or with custom options
python3 src/api_server.py \
  --webhook-url "http://n8n.local:5678/webhook/your-webhook-id" \
  --host 0.0.0.0 \
  --port 8000 \
  --storage-dir "/home/pi/RaspberryPie5/frames" \
  --base-url "http://raspberrypi.local:8000/frames"
```

**Available command line options:**
- `--webhook-url`: n8n webhook URL (required for sending events)
- `--host`: Server host (default: `0.0.0.0`)
- `--port`: Server port (default: `8000`)
- `--storage-dir`: Frame storage directory (default: `frames/`)
- `--base-url`: Base URL for frame access (optional)

### Method 2: Configuration File (Recommended for Production)

Edit `src/raspberry_pi_face_detection.py` to configure the API server:

```python
class Config:
    # ... other settings ...
    
    # API/n8n integration settings
    ENABLE_N8N_INTEGRATION = True  # Set to True to enable
    N8N_WEBHOOK_URL = "http://n8n.local:5678/webhook/your-webhook-id"  # Your n8n webhook URL
    
    # API Server settings
    API_SERVER_ENABLED = True  # Set to True to start API server
    API_SERVER_HOST = "0.0.0.0"
    API_SERVER_PORT = 8000
    API_FRAME_STORAGE_DIR = "frames"  # Auto-configured to project root/frames
    API_FRAME_BASE_URL = "http://raspberrypi.local:8000/frames"  # Optional: for frame URLs
    CAMERA_ID = "raspberry_pi_camera"  # Camera identifier for events
```

## Step-by-Step Configuration

### Step 1: Get Your n8n Webhook URL

**n8n Cloud (Recommended for Quick Setup):**

1. **Open n8n Cloud** in your browser (https://app.n8n.cloud)
2. **Create a new workflow** or open existing one
3. **Add a Webhook node**
4. **Configure the webhook:**
   - Method: `POST` ⚠️ **Important: Use POST, not GET**
   - Path: `/webhook/your-unique-id` (or use auto-generated)
   - Authentication: None (or configure if needed)
   - Response Mode: "Last Node" (default) or "When Last Node Finishes"
5. **Click "Execute Node"** to activate the webhook
6. **Copy the webhook URL** (e.g., `https://[id].hooks.n8n.cloud/webhook/[webhook-id]`)

**Local n8n Instance:**

1. **Open n8n** in your browser (e.g., `http://localhost:5678` or `http://192.168.1.100:5678`)
2. **Create a new workflow** or open existing one
3. **Add a Webhook node**
4. **Configure the webhook:**
   - Method: `POST` ⚠️ **Important: Use POST, not GET**
   - Path: `/webhook/your-unique-id` (or use auto-generated)
   - Authentication: None (or configure if needed)
   - Response Mode: "Last Node" (default) or "When Last Node Finishes"
5. **Click "Execute Node"** to activate the webhook
6. **Copy the webhook URL** (e.g., `http://n8n.local:5678/webhook/abc123`)

**Why POST?**
- The system sends events **TO** n8n using POST requests with JSON payloads
- POST is required for sending complex data (detection events, images, metadata)
- GET is only for simple queries without request bodies
- n8n webhooks are designed to receive POST requests with data

**Note:** If you have an n8n cloud URL (like `https://*.hooks.n8n.cloud/webhook/*`), that's perfectly fine! See [n8n Cloud vs Local Guide](N8N_CLOUD_VS_LOCAL.md) for details.

### Step 2: Configure API Server

**Option A: Quick Test (Command Line)**

```bash
# Stop current API server (Ctrl+C)
# Then restart with webhook URL:
python3 src/api_server.py \
  --webhook-url "http://n8n.local:5678/webhook/your-webhook-id"
```

**Option B: Permanent Configuration (Config File)**

1. Edit the config file:
```bash
nano src/raspberry_pi_face_detection.py
```

2. Find the `Config` class and update:
```python
class Config:
    # ... existing settings ...
    
    # Enable n8n integration
    ENABLE_N8N_INTEGRATION = True
    N8N_WEBHOOK_URL = "http://n8n.local:5678/webhook/your-webhook-id"
    
    # Enable API server
    API_SERVER_ENABLED = True
    API_SERVER_HOST = "0.0.0.0"
    API_SERVER_PORT = 8000
    API_FRAME_BASE_URL = "http://raspberrypi.local:8000/frames"
```

3. Save and exit (Ctrl+X, Y, Enter)

### Step 3: Restart API Server

```bash
# Stop current server (Ctrl+C if running)
# Then restart:
./run_api.sh

# Or if using integrated mode (API starts with face detection):
./run.sh
```

### Step 4: Verify Configuration

```bash
# Check health endpoint
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "webhook_enabled": true,
#   "webhook_url": "http://n8n.local:5678/webhook/your-webhook-id"
# }
```

## Configuration Examples

### Example 1: Local n8n Instance

If n8n is running on the same network:

```python
N8N_WEBHOOK_URL = "http://192.168.1.100:5678/webhook/abc123"
API_FRAME_BASE_URL = "http://192.168.1.50:8000/frames"  # Pi's IP
```

### Example 2: Remote n8n Instance

If n8n is running on a different machine or cloud:

```python
N8N_WEBHOOK_URL = "https://n8n.example.com/webhook/abc123"
API_FRAME_BASE_URL = "http://raspberrypi.local:8000/frames"
```

### Example 3: Custom Port

If you want to use a different port:

```python
API_SERVER_PORT = 8080
```

Then access at: `http://raspberrypi.local:8080`

### Example 4: Frame Storage on Network Drive

If frames are stored on a network drive:

```python
API_FRAME_STORAGE_DIR = "/mnt/nas/frames"
API_FRAME_BASE_URL = "http://nas.local/frames"
```

## Testing Configuration

### Test 1: Health Check

```bash
curl http://localhost:8000/health
```

Should return:
```json
{
  "status": "healthy",
  "webhook_enabled": true,
  "webhook_url": "http://n8n.local:5678/webhook/your-id"
}
```

### Test 2: Test Connection Command

```bash
curl -X POST http://localhost:8000/command \
  -H "Content-Type: application/json" \
  -d '{"command": "test_connection", "parameters": {}}'
```

### Test 3: Send Test Event to n8n

```bash
curl -X POST http://localhost:8000/event \
  -H "Content-Type: application/json" \
  -d '{
    "camera_id": "test_camera",
    "event_type": "test_event",
    "timestamp": "2024-01-15T10:30:45.123456",
    "detections": [],
    "metadata": {"test": true}
  }'
```

Check your n8n workflow - you should see the event arrive!

## Troubleshooting

### Problem: Webhook URL Not Configured

**Symptom:** `⚠️ n8n webhook URL not configured - events will not be sent`

**Solution:**
1. Set `N8N_WEBHOOK_URL` in config file, OR
2. Pass `--webhook-url` when starting API server

### Problem: Cannot Connect to n8n

**Symptom:** Events not arriving in n8n

**Check:**
1. **Network connectivity:**
   ```bash
   ping n8n.local
   # Or
   curl http://n8n.local:5678/webhook/your-id
   ```

2. **Webhook URL is correct:**
   - Check for typos
   - Ensure webhook is activated in n8n
   - Verify port number (default: 5678)

3. **Firewall:**
   ```bash
   # Check if port is accessible
   curl http://n8n.local:5678/webhook/your-id
   ```

### Problem: Frame URLs Not Working

**Symptom:** `frame_url` in events is `null` or not accessible

**Solution:**
1. Set `API_FRAME_BASE_URL` in config:
   ```python
   API_FRAME_BASE_URL = "http://raspberrypi.local:8000/frames"
   ```

2. Ensure API server is accessible from n8n:
   - Use Pi's IP address if `raspberrypi.local` doesn't resolve
   - Check firewall allows port 8000

### Problem: API Server Won't Start

**Check:**
1. Port already in use:
   ```bash
   sudo netstat -tulpn | grep 8000
   # Kill process if needed
   sudo kill <PID>
   ```

2. Permission issues:
   ```bash
   chmod +x run_api.sh
   chmod +x src/api_server.py
   ```

## Complete Configuration Example

Here's a complete configuration for production use:

```python
class Config:
    # ... camera and detection settings ...
    
    # n8n Integration
    ENABLE_N8N_INTEGRATION = True
    N8N_WEBHOOK_URL = "http://192.168.1.100:5678/webhook/face-detection-abc123"
    
    # API Server
    API_SERVER_ENABLED = True
    API_SERVER_HOST = "0.0.0.0"  # Listen on all interfaces
    API_SERVER_PORT = 8000
    API_FRAME_STORAGE_DIR = "frames"  # Auto: project_root/frames
    API_FRAME_BASE_URL = "http://192.168.1.50:8000/frames"  # Pi's IP
    CAMERA_ID = "front_door_camera"
    
    # Alerts
    ENABLE_UNKNOWN_PERSON_ALERTS = True
    ENABLE_VERIFIED_PERSON_ALERTS = True
```

## Quick Reference

**Start API server with webhook:**
```bash
python3 src/api_server.py --webhook-url "http://n8n.local:5678/webhook/id"
```

**Check configuration:**
```bash
curl http://localhost:8000/health
```

**Test webhook:**
```bash
curl -X POST http://localhost:8000/command \
  -H "Content-Type: application/json" \
  -d '{"command": "test_connection"}'
```

**View API documentation:**
- Open in browser: `http://raspberrypi.local:8000/docs`

---

**See Also:**
- [API Guide](API_GUIDE.md) - General API usage
- [API Reference](API_REFERENCE.md) - Complete endpoint documentation
- [Command API](COMMAND_API.md) - Command endpoint guide

