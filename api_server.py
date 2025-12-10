#!/usr/bin/env python3
"""
FastAPI Server for n8n Integration
===================================

This module provides HTTP API endpoints for sending detection events to n8n.
It follows the push model: when detections occur, events are sent to n8n webhook URLs.

Endpoints:
- POST /event - Receive detection events and forward to n8n
- POST /training-clip - Accept training clip metadata

Author: AI Assistant
Date: 2024
"""

import json
import base64
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
import threading
import queue

# Try to import FastAPI
try:
    from fastapi import FastAPI, HTTPException, UploadFile, File, Form
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field
    import uvicorn
    import httpx
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    FastAPI = None
    print("⚠️  Warning: FastAPI not available. API features will be disabled.")
    print("   Install with: pip install fastapi uvicorn httpx")

# ============================================================================
# EVENT MODELS (Pydantic schemas)
# ============================================================================

if FASTAPI_AVAILABLE:
    class Detection(BaseModel):
        """Single detection object"""
        label: str = Field(..., description="Detection label (e.g., 'face', 'person')")
        confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
        bbox: List[float] = Field(..., min_items=4, max_items=4, description="Bounding box [x1, y1, x2, y2]")
        name: Optional[str] = Field(None, description="Recognized name if face recognition enabled")
    
    class DetectionEvent(BaseModel):
        """Detection event payload"""
        camera_id: str = Field(..., description="Camera identifier (e.g., 'frontdoor')")
        event_type: str = Field(..., description="Event type: 'person_detected', 'face_detected', 'training_clip_ready'")
        timestamp: str = Field(..., description="ISO 8601 timestamp")
        detections: List[Detection] = Field(default_factory=list, description="List of detections")
        frame_url: Optional[str] = Field(None, description="URL to frame image")
        frame_base64: Optional[str] = Field(None, description="Base64 encoded frame (alternative to frame_url)")
        clip_url: Optional[str] = Field(None, description="URL to video clip (for training clips)")
        metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    class TrainingClipEvent(BaseModel):
        """Training clip event payload"""
        camera_id: str = Field(..., description="Camera identifier")
        clip_path: str = Field(..., description="Path to saved clip file")
        clip_url: Optional[str] = Field(None, description="URL to access clip")
        timestamp: str = Field(..., description="ISO 8601 timestamp")
        duration: Optional[float] = Field(None, description="Clip duration in seconds")
        frame_count: Optional[int] = Field(None, description="Number of frames in clip")
        metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")

# ============================================================================
# EVENT HANDLER (n8n Webhook Client)
# ============================================================================

class N8NWebhookClient:
    """Client for sending events to n8n webhooks"""
    
    def __init__(self, webhook_url: Optional[str] = None, timeout: float = 5.0):
        """
        Initialize n8n webhook client
        
        Args:
            webhook_url: n8n webhook URL (can be None if not configured)
            timeout: HTTP request timeout in seconds
        """
        self.webhook_url = webhook_url
        self.timeout = timeout
        self.enabled = webhook_url is not None and webhook_url.strip() != ""
        self.event_queue = queue.Queue()
        self.worker_thread = None
        self.is_running = False
        
        if self.enabled:
            print(f"✅ n8n webhook client initialized: {webhook_url}")
            self.start_worker()
        else:
            print("⚠️  n8n webhook URL not configured - events will not be sent")
    
    def start_worker(self):
        """Start background worker thread for sending events"""
        if self.worker_thread is None or not self.worker_thread.is_alive():
            self.is_running = True
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()
            print("✅ n8n webhook worker thread started")
    
    def stop_worker(self):
        """Stop background worker thread"""
        self.is_running = False
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2.0)
    
    def _worker_loop(self):
        """Background worker loop for sending events"""
        while self.is_running:
            try:
                # Get event from queue (with timeout)
                try:
                    event_data = self.event_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Send event to n8n
                self._send_event(event_data)
                
                # Mark task as done
                self.event_queue.task_done()
                
            except Exception as e:
                print(f"⚠️  Error in n8n webhook worker: {e}")
    
    def _send_event(self, event_data: Dict[str, Any]):
        """
        Send event to n8n webhook
        
        Args:
            event_data: Event data dictionary
        """
        if not self.enabled or not self.webhook_url:
            return
        
        try:
            if not FASTAPI_AVAILABLE:
                print("⚠️  FastAPI/httpx not available - cannot send webhook")
                return
            
            import httpx
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    self.webhook_url,
                    json=event_data,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                print(f"✅ Event sent to n8n: {event_data.get('event_type', 'unknown')}")
        
        except httpx.TimeoutException:
            print(f"⚠️  Timeout sending event to n8n: {event_data.get('event_type', 'unknown')}")
        except httpx.HTTPStatusError as e:
            print(f"⚠️  HTTP error sending event to n8n: {e.response.status_code}")
        except Exception as e:
            print(f"⚠️  Error sending event to n8n: {e}")
    
    def send_event(self, event_data: Dict[str, Any], async_send: bool = True):
        """
        Queue event for sending to n8n
        
        Args:
            event_data: Event data dictionary
            async_send: If True, queue for async sending. If False, send immediately (blocking)
        """
        if not self.enabled:
            return
        
        if async_send:
            try:
                self.event_queue.put_nowait(event_data)
            except queue.Full:
                print("⚠️  Event queue full - dropping event")
        else:
            self._send_event(event_data)

# ============================================================================
# FRAME STORAGE MANAGER
# ============================================================================

class FrameStorageManager:
    """Manages storage and URL generation for frames"""
    
    def __init__(self, storage_dir: str = "frames", base_url: Optional[str] = None):
        """
        Initialize frame storage manager
        
        Args:
            storage_dir: Directory to store frames
            base_url: Base URL for accessing frames (e.g., "http://raspberrypi.local:8000/frames")
        """
        self.storage_dir = Path(storage_dir)
        self.base_url = base_url
        self.storage_dir.mkdir(exist_ok=True)
        
        # Clean old frames periodically (keep last 100)
        self.max_frames = 100
    
    def save_frame(self, frame_data: bytes, filename: Optional[str] = None) -> tuple[str, Optional[str]]:
        """
        Save frame to disk and return filename and URL
        
        Args:
            frame_data: Frame image data (bytes)
            filename: Optional filename (auto-generated if None)
            
        Returns:
            Tuple of (filename, url)
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"frame_{timestamp}.jpg"
        
        filepath = self.storage_dir / filename
        
        try:
            filepath.write_bytes(frame_data)
            
            # Generate URL if base_url is configured
            url = None
            if self.base_url:
                url = f"{self.base_url.rstrip('/')}/{filename}"
            
            # Clean old frames if needed
            self._cleanup_old_frames()
            
            return filename, url
        
        except Exception as e:
            print(f"⚠️  Error saving frame: {e}")
            return filename, None
    
    def _cleanup_old_frames(self):
        """Remove old frames if exceeding max_frames limit"""
        try:
            frames = sorted(self.storage_dir.glob("frame_*.jpg"), key=lambda p: p.stat().st_mtime)
            if len(frames) > self.max_frames:
                for frame_file in frames[:-self.max_frames]:
                    frame_file.unlink()
        except Exception as e:
            print(f"⚠️  Error cleaning up frames: {e}")

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="Raspberry Pi Face Detection API",
        description="API for sending detection events to n8n",
        version="1.0.0"
    )
    
    # Global instances
    webhook_client: Optional[N8NWebhookClient] = None
    frame_storage: Optional[FrameStorageManager] = None
    
    @app.post("/event", response_model=Dict[str, Any])
    async def receive_event(event: DetectionEvent):
        """
        Receive detection event and forward to n8n webhook
        
        This endpoint is called internally by the detection system when events occur.
        """
        try:
            # Convert event to dictionary
            event_dict = event.dict()
            
            # Send to n8n webhook (async)
            if webhook_client:
                webhook_client.send_event(event_dict, async_send=True)
            
            return {
                "status": "success",
                "message": "Event received and queued for n8n",
                "event_type": event.event_type,
                "timestamp": event.timestamp
            }
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing event: {str(e)}")
    
    @app.post("/training-clip", response_model=Dict[str, Any])
    async def receive_training_clip(
        clip_path: str = Form(...),
        camera_id: str = Form(...),
        clip_url: Optional[str] = Form(None),
        duration: Optional[float] = Form(None),
        frame_count: Optional[int] = Form(None),
        metadata: Optional[str] = Form(None),  # JSON string
        frame_preview: Optional[UploadFile] = File(None)
    ):
        """
        Receive training clip metadata and optionally a preview frame
        
        This endpoint accepts metadata about saved training clips.
        """
        try:
            # Parse metadata if provided
            metadata_dict = {}
            if metadata:
                try:
                    metadata_dict = json.loads(metadata)
                except json.JSONDecodeError:
                    pass
            
            # Handle preview frame if provided
            frame_url = None
            if frame_preview:
                frame_data = await frame_preview.read()
                if frame_storage:
                    _, frame_url = frame_storage.save_frame(frame_data)
            
            # Create training clip event
            clip_event = TrainingClipEvent(
                camera_id=camera_id,
                clip_path=clip_path,
                clip_url=clip_url,
                timestamp=datetime.now().isoformat(),
                duration=duration,
                frame_count=frame_count,
                metadata=metadata_dict
            )
            
            # Convert to dictionary for n8n
            event_dict = clip_event.dict()
            event_dict["event_type"] = "training_clip_ready"
            
            # Send to n8n webhook
            if webhook_client:
                webhook_client.send_event(event_dict, async_send=True)
            
            return {
                "status": "success",
                "message": "Training clip event received",
                "clip_path": clip_path,
                "frame_url": frame_url
            }
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing training clip: {str(e)}")
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "webhook_enabled": webhook_client.enabled if webhook_client else False,
            "webhook_url": webhook_client.webhook_url if webhook_client else None
        }
    
    @app.post("/unknown-person-alert", response_model=Dict[str, Any])
    async def unknown_person_alert(
        camera_id: str = Form(...),
        bbox: str = Form(...),  # JSON string: [x1, y1, x2, y2]
        confidence: float = Form(...),
        frame: UploadFile = File(...),
        metadata: Optional[str] = Form(None)  # JSON string
    ):
        """
        Send alert for unknown person detection with captured image
        
        This endpoint accepts an image of an unknown person and sends an alert to n8n.
        Can be called directly from external systems or used as a webhook target.
        """
        try:
            # Parse bbox
            try:
                bbox_list = json.loads(bbox)
                if not isinstance(bbox_list, list) or len(bbox_list) != 4:
                    raise ValueError("bbox must be a list of 4 numbers")
            except (json.JSONDecodeError, ValueError) as e:
                raise HTTPException(status_code=400, detail=f"Invalid bbox format: {e}")
            
            # Parse metadata if provided
            metadata_dict = {}
            if metadata:
                try:
                    metadata_dict = json.loads(metadata)
                except json.JSONDecodeError:
                    pass
            
            # Read and save frame
            frame_data = await frame.read()
            frame_url = None
            
            if frame_storage:
                # Generate filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                filename = f"unknown_person_{timestamp}.jpg"
                _, frame_url = frame_storage.save_frame(frame_data, filename=filename)
            
            # Create detection event
            detection_event = {
                "camera_id": camera_id,
                "event_type": "unknown_person_detected",
                "timestamp": datetime.now().isoformat(),
                "detections": [
                    {
                        "label": "unknown_person",
                        "confidence": float(confidence),
                        "bbox": [float(x) for x in bbox_list],
                        "name": None
                    }
                ],
                "frame_url": frame_url,
                "frame_base64": None,
                "clip_url": None,
                "metadata": {
                    **metadata_dict,
                    "alert_source": "api_endpoint",
                    "alert_type": "unknown_person"
                }
            }
            
            # Send to n8n webhook
            if webhook_client:
                webhook_client.send_event(detection_event, async_send=True)
            
            return {
                "status": "success",
                "message": "Unknown person alert sent",
                "event_type": "unknown_person_detected",
                "frame_url": frame_url,
                "timestamp": detection_event["timestamp"]
            }
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing unknown person alert: {str(e)}")
    
    @app.get("/")
    async def root():
        """Root endpoint with API information"""
        return {
            "name": "Raspberry Pi Face Detection API",
            "version": "1.0.0",
            "endpoints": {
                "POST /event": "Receive detection events",
                "POST /training-clip": "Receive training clip metadata",
                "POST /unknown-person-alert": "Send unknown person alert with image",
                "GET /health": "Health check",
                "GET /": "API information"
            }
        }

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_detection_event(
    camera_id: str,
    event_type: str,
    detections: List[Dict[str, Any]],
    frame: Optional[Any] = None,
    frame_url: Optional[str] = None,
    clip_url: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a detection event dictionary
    
    Args:
        camera_id: Camera identifier
        event_type: Event type ("person_detected", "face_detected", etc.)
        detections: List of detection dictionaries with label, confidence, bbox, name
        frame: Optional numpy array frame (will be saved if provided)
        frame_url: Optional frame URL
        clip_url: Optional clip URL
        metadata: Optional additional metadata
        
    Returns:
        Event dictionary ready for n8n
    """
    # Convert detections to proper format
    detection_list = []
    for det in detections:
        detection_list.append({
            "label": det.get("label", "face"),
            "confidence": float(det.get("confidence", 0.0)),
            "bbox": [float(x) for x in det.get("bbox", [0, 0, 0, 0])],
            "name": det.get("name")
        })
    
    # Handle frame if provided
    final_frame_url = frame_url
    frame_base64 = None
    
    if frame is not None and frame_storage:
        try:
            # Convert numpy array to JPEG bytes
            from PIL import Image
            import numpy as np
            
            if isinstance(frame, np.ndarray):
                pil_image = Image.fromarray(frame)
                import io
                buffer = io.BytesIO()
                pil_image.save(buffer, format="JPEG", quality=85)
                frame_bytes = buffer.getvalue()
                
                # Save frame and get URL
                _, final_frame_url = frame_storage.save_frame(frame_bytes)
        except Exception as e:
            print(f"⚠️  Error processing frame: {e}")
    
    # Create event
    event = {
        "camera_id": camera_id,
        "event_type": event_type,
        "timestamp": datetime.now().isoformat(),
        "detections": detection_list,
        "frame_url": final_frame_url,
        "frame_base64": frame_base64,
        "clip_url": clip_url,
        "metadata": metadata or {}
    }
    
    return event

def initialize_api_server(
    webhook_url: Optional[str] = None,
    storage_dir: str = "frames",
    base_url: Optional[str] = None,
    host: str = "0.0.0.0",
    port: int = 8000
):
    """
    Initialize and start the FastAPI server
    
    Args:
        webhook_url: n8n webhook URL
        storage_dir: Directory for storing frames
        base_url: Base URL for accessing frames
        host: Server host
        port: Server port
    """
    global webhook_client, frame_storage
    
    if not FASTAPI_AVAILABLE:
        print("❌ FastAPI not available - API server cannot start")
        print("   Install with: pip install fastapi uvicorn httpx")
        return None
    
    # Initialize components
    webhook_client = N8NWebhookClient(webhook_url=webhook_url)
    frame_storage = FrameStorageManager(storage_dir=storage_dir, base_url=base_url)
    
    print(f"🚀 Starting API server on {host}:{port}")
    print(f"   Webhook URL: {webhook_url or 'Not configured'}")
    print(f"   Frame storage: {storage_dir}")
    
    # Start server in background thread
    def run_server():
        uvicorn.run(app, host=host, port=port, log_level="info")
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    return webhook_client

if __name__ == "__main__":
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description="Start API server for n8n integration")
    parser.add_argument("--webhook-url", type=str, help="n8n webhook URL")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Server host")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--storage-dir", type=str, default="frames", help="Frame storage directory")
    parser.add_argument("--base-url", type=str, help="Base URL for frame access")
    
    args = parser.parse_args()
    
    initialize_api_server(
        webhook_url=args.webhook_url,
        storage_dir=args.storage_dir,
        base_url=args.base_url,
        host=args.host,
        port=args.port
    )
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down API server...")

