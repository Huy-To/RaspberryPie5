# n8n Cloud vs Local: Webhook URL Guide

## Your URL Analysis

**Your URL:** `https://6ggkissei8ctfmonsox9d8tz.hooks.n8n.cloud/webhook/b666a94f-f3be-4f52-83c1-2cf687be6e73`

**Type:** ✅ **n8n Cloud** (not local)

**Can you use it?** ✅ **Yes!** This will work perfectly fine.

---

## n8n Cloud vs Local: What's the Difference?

### n8n Cloud (Your URL)

**Domain:** `hooks.n8n.cloud`

**Characteristics:**
- ✅ Hosted by n8n (cloud service)
- ✅ Accessible from anywhere on the internet
- ✅ No need to manage server/hosting
- ✅ Works from Raspberry Pi if it has internet access
- ✅ URL format: `https://[random-id].hooks.n8n.cloud/webhook/[webhook-id]`

**Your URL Breakdown:**
```
https://6ggkissei8ctfmonsox9d8tz.hooks.n8n.cloud/webhook/b666a94f-f3be-4f52-83c1-2cf687be6e73
│     │                              │              │      │
│     │                              │              │      └─ Webhook ID
│     │                              │              └─ Path
│     │                              └─ n8n Cloud Domain
│     └─ Instance ID
└─ HTTPS Protocol
```

### Local n8n Instance

**Domain:** Your local network (e.g., `localhost`, `192.168.x.x`, `n8n.local`)

**Characteristics:**
- ✅ Runs on your own server/computer
- ✅ Only accessible on your local network
- ✅ Full control over data and hosting
- ✅ No internet required (after initial setup)
- ✅ URL format: `http://[your-ip-or-hostname]:5678/webhook/[webhook-id]`

**Example Local URLs:**
```
http://localhost:5678/webhook/abc123
http://192.168.1.100:5678/webhook/abc123
http://n8n.local:5678/webhook/abc123
http://raspberrypi.local:5678/webhook/abc123
```

---

## How to Use Your n8n Cloud Webhook

### Step 1: Verify Internet Connectivity

Your Raspberry Pi needs internet access to reach n8n cloud:

```bash
# Test internet connectivity
ping -c 3 google.com

# Test n8n cloud connectivity
curl -I https://hooks.n8n.cloud
```

### Step 2: Configure API Server

**Option A: Command Line (Quick Test)**

```bash
./run_api.sh --webhook-url "https://6ggkissei8ctfmonsox9d8tz.hooks.n8n.cloud/webhook/b666a94f-f3be-4f52-83c1-2cf687be6e73"
```

**Option B: Configuration File (Permanent)**

Edit `src/raspberry_pi_face_detection.py`:

```python
class Config:
    # ... other settings ...
    
    # n8n Integration (Cloud)
    ENABLE_N8N_INTEGRATION = True
    N8N_WEBHOOK_URL = "https://6ggkissei8ctfmonsox9d8tz.hooks.n8n.cloud/webhook/b666a94f-f3be-4f52-83c1-2cf687be6e73"
    
    # API Server
    API_SERVER_ENABLED = True
    API_SERVER_HOST = "0.0.0.0"
    API_SERVER_PORT = 8000
```

### Step 3: Test the Connection

```bash
# Test health endpoint
curl http://localhost:8000/health

# Should show:
# {
#   "status": "healthy",
#   "webhook_enabled": true,
#   "webhook_url": "https://6ggkissei8ctfmonsox9d8tz.hooks.n8n.cloud/webhook/..."
# }

# Send a test event
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

Check your n8n cloud workflow - you should see the event arrive!

---

## Comparison: Cloud vs Local

| Feature | n8n Cloud | Local n8n |
|---------|-----------|-----------|
| **URL Format** | `https://*.hooks.n8n.cloud/webhook/*` | `http://[ip]:5678/webhook/*` |
| **Internet Required** | ✅ Yes | ❌ No (after setup) |
| **Accessibility** | Anywhere | Local network only |
| **Setup Complexity** | Easy (just sign up) | Medium (install & configure) |
| **Cost** | Free tier available | Free (self-hosted) |
| **Data Location** | n8n servers | Your server |
| **Performance** | Depends on internet | Depends on local network |
| **Best For** | Quick setup, remote access | Privacy, offline use |

---

## Which Should You Use?

### Use n8n Cloud If:
- ✅ You want quick setup
- ✅ Your Raspberry Pi has reliable internet
- ✅ You don't mind data going through n8n's servers
- ✅ You want to access workflows from anywhere
- ✅ You're okay with free tier limitations (if applicable)

### Use Local n8n If:
- ✅ You want complete data privacy
- ✅ You want offline operation (no internet required)
- ✅ You have a server/computer to run n8n
- ✅ You want full control over hosting
- ✅ You're on a local network only

---

## Troubleshooting n8n Cloud Connection

### Problem: Cannot Connect to n8n Cloud

**Symptoms:**
- Events not arriving in n8n
- Timeout errors
- Connection refused

**Solutions:**

1. **Check Internet Connection:**
   ```bash
   ping -c 3 google.com
   curl -I https://hooks.n8n.cloud
   ```

2. **Check Firewall:**
   ```bash
   # Raspberry Pi should allow outbound HTTPS (port 443)
   # Usually enabled by default
   ```

3. **Test Webhook Directly:**
   ```bash
   curl -X POST https://6ggkissei8ctfmonsox9d8tz.hooks.n8n.cloud/webhook/b666a94f-f3be-4f52-83c1-2cf687be6e73 \
     -H "Content-Type: application/json" \
     -d '{"test": true}'
   ```

4. **Verify Webhook is Active:**
   - Go to your n8n cloud workflow
   - Check that the webhook node is executed/active
   - Make sure the webhook URL matches exactly

5. **Check SSL/TLS:**
   ```bash
   # Test SSL connection
   openssl s_client -connect hooks.n8n.cloud:443 -showcerts
   ```

### Problem: Events Not Arriving

**Check:**
1. Webhook URL is correct (copy-paste to avoid typos)
2. Webhook node is executed/active in n8n
3. Workflow is saved and active
4. Check n8n execution logs for errors

---

## Switching Between Cloud and Local

### From Cloud to Local

If you want to switch to a local n8n instance:

1. **Install n8n locally** (on another machine or Docker)
2. **Create webhook** in local n8n
3. **Get local webhook URL** (e.g., `http://192.168.1.100:5678/webhook/abc123`)
4. **Update configuration** in `raspberry_pi_face_detection.py`
5. **Restart API server**

### From Local to Cloud

If you want to switch to n8n cloud:

1. **Sign up for n8n cloud** (if not already)
2. **Create webhook** in cloud workflow
3. **Get cloud webhook URL** (like yours)
4. **Update configuration** in `raspberry_pi_face_detection.py`
5. **Restart API server**

---

## Your Specific Configuration

**Your Webhook URL:**
```
https://6ggkissei8ctfmonsox9d8tz.hooks.n8n.cloud/webhook/b666a94f-f3be-4f52-83c1-2cf687be6e73
```

**To Use It:**

1. **Quick Test:**
   ```bash
   ./run_api.sh --webhook-url "https://6ggkissei8ctfmonsox9d8tz.hooks.n8n.cloud/webhook/b666a94f-f3be-4f52-83c1-2cf687be6e73"
   ```

2. **Permanent Setup:**
   Edit `src/raspberry_pi_face_detection.py`:
   ```python
   N8N_WEBHOOK_URL = "https://6ggkissei8ctfmonsox9d8tz.hooks.n8n.cloud/webhook/b666a94f-f3be-4f52-83c1-2cf687be6e73"
   ```

3. **Verify:**
   ```bash
   curl http://localhost:8000/health
   ```

---

## Summary

✅ **Your URL is valid** - It's an n8n cloud webhook URL  
✅ **It will work** - As long as your Raspberry Pi has internet access  
✅ **Use it as-is** - No changes needed to the URL format  

The system will send events to your n8n cloud workflow automatically when configured!

---

**See Also:**
- [API Configuration Guide](API_CONFIGURATION.md) - Complete setup instructions
- [API Reference](API_REFERENCE.md) - Endpoint documentation

