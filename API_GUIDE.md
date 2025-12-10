# n8n Integration API Guide (FastAPI)

This guide explains how to send detection/training events from the Raspberry Pi 5 face detection system to n8n using the built‑in FastAPI server and webhook client.

## Prerequisites
- Raspberry Pi 5 with this project installed (`setup.sh` installs FastAPI/httpx).
- n8n instance with a Webhook node (publicly reachable or reachable from the Pi).
- Optional: `ffmpeg` if you plan to push frames/clips through the API.

## Quick Start (Push Model - recommended)
1) Set your n8n webhook URL in `raspberry_pi_face_detection.py`:
```python
class Config:
    ENABLE_N8N_INTEGRATION = True
    N8N_WEBHOOK_URL = "http://n8n.local:5678/webhook/your-id"
    API_SERVER_ENABLED = True          # start FastAPI server
    API_SERVER_HOST = "0.0.0.0"
    API_SERVER_PORT = 8000
    API_FRAME_STORAGE_DIR = "frames"
    API_FRAME_BASE_URL = "http://raspberrypi.local:8000/frames"  # optional for frame URLs
    CAMERA_ID = "raspberry_pi_camera"
```
2) Run detection as usual:
```bash
./run.sh
# or
python3 raspberry_pi_face_detection.py
```
Events will be sent automatically to your n8n webhook when faces are detected.

## Standalone API Server (optional)
If you only want the API server (e.g., pull model or custom posts):
```bash
python3 api_server.py --webhook-url "http://n8n.local:5678/webhook/your-id" --host 0.0.0.0 --port 8000
```

## Endpoints
- **POST /event**  
  Receives detection events. Payload matches the schema below. Forwards to n8n if webhook configured.

- **POST /training-clip**  
  Form fields: `clip_path`, `camera_id`, optional `clip_url`, `duration`, `frame_count`, `metadata` (JSON), optional `frame_preview` (UploadFile). Forwards as `training_clip_ready`.

- **GET /health**  
  Returns status and webhook configuration.

- **GET /**  
  API info and endpoint listing.

## Event Schema (sent to n8n)
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
  "clip_url": null,
  "metadata": {
    "frame_count": 1234,
    "fps": 15.5
  }
}
```

## Push vs Pull
- **Push (default):** The detector posts to your n8n webhook in real time (best for alerts).
- **Pull:** You can call `GET /event` is not provided; instead you can have n8n poll your own store. Recommended: stick with push for simplicity.

## Frame & Clip Handling
- Frames are saved in `frames/` (keeps last 100). If `API_FRAME_BASE_URL` is set, events include `frame_url`.
- For large media, prefer hosting clips/frames on local NAS/HTTP server and send only URLs in the event (`clip_url`, `frame_url`).
- `frame_base64` exists in the model but is not sent by default to keep payloads small.

## Testing with curl
Health check:
```bash
curl http://raspberrypi.local:8000/health
```

Send a test event to the API (which will forward to n8n if configured):
```bash
curl -X POST http://raspberrypi.local:8000/event \
  -H "Content-Type: application/json" \
  -d '{
    "camera_id": "raspberry_pi_camera",
    "event_type": "face_detected",
    "timestamp": "2024-01-15T10:30:45.123456",
    "detections": [{"label":"face","confidence":0.9,"bbox":[10,10,100,120],"name":"Test"}]
  }'
```

## n8n Setup Steps
1) Add a **Webhook** node in n8n, copy its URL.
2) Set that URL in `N8N_WEBHOOK_URL` (Config) or pass `--webhook-url` to `api_server.py`.
3) Deploy the workflow; ensure the webhook is reachable from the Pi.
4) Run detection; verify events appear in n8n execution logs.

## Notes for Raspberry Pi 5
- Use `API_FRAME_BASE_URL` pointing to the Pi’s reachable hostname/IP and port if you want n8n to fetch frames.
- Keep `event_type` values short and stable (`face_detected`, `training_clip_ready`, etc.).
- If bandwidth is limited, avoid sending base64 frames; use URLs.

## Troubleshooting
- No events in n8n: check `N8N_WEBHOOK_URL` and network reachability; check API logs for HTTP errors.
- Frame URLs not working: ensure `API_FRAME_BASE_URL` matches your Pi host/port and that the API server is running.
- FastAPI missing: `python3 -m pip install --break-system-packages fastapi uvicorn httpx pydantic`.

