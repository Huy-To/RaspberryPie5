#!/usr/bin/env python3
"""
Raspberry Pi 5 Face Detection System (Picamera2 Only)
=====================================================

A real-time face detection system optimized for Raspberry Pi 5 using YOLOv12n-face.pt
Features:
- Real-time camera feed using picamera2 (Raspberry Pi Camera Module only)
- Optimized for Raspberry Pi 5 performance
- Configurable detection parameters
- FPS monitoring and performance stats
- Console output with detection results

Author: AI Assistant
Date: 2024
"""

import numpy as np
import time
import threading
import queue
from ultralytics import YOLO
import argparse
import sys
import json
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Try to import face_recognition library
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    face_recognition = None
    print("⚠️  Warning: face_recognition library not available.")
    print("   Facial recognition features will be disabled.")
    print("   Install with: pip install face_recognition")

# Try to import ImageTk (requires both Pillow and tkinter)
try:
    from PIL import ImageTk
    IMAGETK_AVAILABLE = True
except ImportError:
    IMAGETK_AVAILABLE = False
    ImageTk = None

# Try to import tkinter
try:
    import tkinter as tk
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    tk = None

# Display is only available if both tkinter and ImageTk are available
DISPLAY_AVAILABLE = TKINTER_AVAILABLE and IMAGETK_AVAILABLE

if not DISPLAY_AVAILABLE:
    if not TKINTER_AVAILABLE:
        print("⚠️  Warning: tkinter not available. Display window will not be shown.")
    elif not IMAGETK_AVAILABLE:
        print("⚠️  Warning: ImageTk not available. Display window will not be shown.")
        print("   Install with: sudo apt install -y python3-pil.imagetk")

# Import picamera2 for Raspberry Pi Camera Module
try:
    from picamera2 import Picamera2
    PICAMERA2_AVAILABLE = True
except ImportError as e:
    # Try to provide more helpful error message
    PICAMERA2_AVAILABLE = False
    Picamera2 = None
    print(f"❌ picamera2 import failed: {e}")
    print("   picamera2 is required but could not be imported.")
    print("   If installed via apt: sudo apt install -y python3-picamera2")
    print("   If installing via pip: python3 -m pip install --break-system-packages picamera2")
    print("   Check installation: python3 -c 'from picamera2 import Picamera2'")
    sys.exit(1)

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Configuration class for the face detection system"""
    
    # Model settings
    MODEL_PATH = "yolov12n-face.pt"
    CONFIDENCE_THRESHOLD = 0.5
    IOU_THRESHOLD = 0.45
    
    # Camera settings
    CAMERA_WIDTH = 640
    CAMERA_HEIGHT = 480
    CAMERA_FPS = 30
    
    # Performance settings
    RESIZE_FACTOR = 0.75  # Resize input for faster processing
    SKIP_FRAMES = 2  # Process every 3rd frame for better performance
    ENABLE_PARALLEL_PROCESSING = True
    MAX_QUEUE_SIZE = 3
    
    # Display settings
    SHOW_FPS = True
    SHOW_DETECTION_INFO = True
    SHOW_PERFORMANCE_STATS = True
    PRINT_TO_CONSOLE = True  # Print detection info to console
    
    # Face recognition settings
    FACE_DATABASE_PATH = "known_faces.json"
    RECOGNITION_TOLERANCE = 0.6  # Lower = more strict (0.4-0.6 recommended)
    ENABLE_FACE_RECOGNITION = True  # Set to False to disable recognition
    
    # API/n8n integration settings
    ENABLE_N8N_INTEGRATION = False  # Set to True to enable n8n webhook integration
    N8N_WEBHOOK_URL = ""  # n8n webhook URL (e.g., "http://n8n.local:5678/webhook/abc123")
    API_SERVER_ENABLED = False  # Set to True to start FastAPI server
    API_SERVER_HOST = "0.0.0.0"
    API_SERVER_PORT = 8000
    API_FRAME_STORAGE_DIR = "frames"
    API_FRAME_BASE_URL = None  # e.g., "http://raspberrypi.local:8000/frames"
    CAMERA_ID = "raspberry_pi_camera"  # Camera identifier for events
    
    # Unknown person alert settings
    ENABLE_UNKNOWN_PERSON_ALERTS = True  # Set to True to enable unknown person alerts
    UNKNOWN_PERSON_ALERT_COOLDOWN = 30  # Seconds between alerts for same unknown person (prevents spam)
    
    # Colors (RGB format for PIL)
    BOX_COLOR = (0, 255, 0)  # Green for detected faces
    RECOGNIZED_COLOR = (0, 255, 0)  # Green for recognized faces
    UNKNOWN_COLOR = (255, 165, 0)  # Orange for unknown faces
    TEXT_COLOR = (0, 255, 0)  # Green
    FPS_COLOR = (255, 255, 0)  # Yellow
    WARNING_COLOR = (255, 0, 0)  # Red

# ============================================================================
# FACE DETECTION SYSTEM
# ============================================================================

class RaspberryPiFaceDetector:
    """
    Face detection system optimized for Raspberry Pi 5 using picamera2 only
    """
    
    def __init__(self, config=Config()):
        """
        Initialize the face detection system
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.model = None
        self.picam2 = None
        
        # Performance tracking
        self.fps_counter = 0
        self.fps_start_time = time.time()
        self.current_fps = 0
        self.frame_count = 0
        self.processing_times = []
        
        # Parallel processing
        self.frame_queue = queue.Queue(maxsize=config.MAX_QUEUE_SIZE)
        self.result_queue = queue.Queue(maxsize=config.MAX_QUEUE_SIZE)
        self.is_running = False
        self.processing_thread = None
        
        # Detection results cache
        self.last_boxes = []
        self.last_scores = []
        self.last_names = []  # For face recognition
        self.last_detection_time = 0
        
        # Face recognition database
        self.known_face_encodings = []
        self.known_face_names = []
        self.face_recognition_enabled = False
        
        # Display window (tkinter)
        self.root = None
        self.display_label = None
        self.display_enabled = False
        
        # API/n8n integration
        self.n8n_client = None
        self.api_frame_storage = None
        self.create_detection_event = None
        
        # Unknown person alert tracking
        self.last_unknown_alert_time = {}  # Track last alert time per unknown face (by bbox hash)
        
        print("🚀 Initializing Raspberry Pi 5 Face Detection & Recognition System (Picamera2 Only)...")
        self.initialize_model()
        self.initialize_camera()
        self.initialize_face_recognition()
        self.initialize_api_integration()
        self.initialize_display()
        
    def initialize_model(self):
        """Initialize the YOLO face detection model"""
        try:
            # Get absolute path to model file
            model_path = Path(self.config.MODEL_PATH)
            if not model_path.is_absolute():
                # If relative path, make it relative to script directory
                script_dir = Path(__file__).parent.absolute()
                model_path = script_dir / model_path
            
            if not model_path.exists():
                raise FileNotFoundError(
                    f"Model file not found: {model_path}\n"
                    f"Please ensure yolov12n-face.pt is in the same directory as this script."
                )
            
            print(f"📦 Loading model: {model_path}")
            self.model = YOLO(str(model_path))
            print("✅ Model loaded successfully")
            
        except FileNotFoundError as e:
            print(f"❌ {e}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            print("   Make sure ultralytics is installed: pip install ultralytics")
            sys.exit(1)
    
    def initialize_camera(self):
        """Initialize picamera2 camera capture"""
        if not PICAMERA2_AVAILABLE:
            raise RuntimeError(
                "picamera2 is not available. Install with: pip install picamera2\n"
                "Note: This system only supports Raspberry Pi Camera Module via picamera2."
            )
        
        try:
            print("📹 Initializing picamera2 (Raspberry Pi Camera Module)...")
            
            self.picam2 = Picamera2()
            
            # Configure camera
            config = self.picam2.create_preview_configuration(
                main={"size": (self.config.CAMERA_WIDTH, self.config.CAMERA_HEIGHT), "format": "RGB888"}
            )
            self.picam2.configure(config)
            self.picam2.start()
            
            # Give camera time to start
            time.sleep(1.0)
            
            # Test capture
            test_frame = self.picam2.capture_array()
            if test_frame is not None and test_frame.size > 0:
                actual_width = test_frame.shape[1]
                actual_height = test_frame.shape[0]
                print(f"✅ Camera initialized: {actual_width}x{actual_height}")
            else:
                raise RuntimeError("Camera test capture failed")
            
        except Exception as e:
            print(f"❌ Error initializing camera: {e}")
            print("\n💡 Troubleshooting tips:")
            print("   1. Make sure Raspberry Pi Camera Module is connected")
            print("   2. Enable camera: sudo raspi-config → Interface Options → Camera")
            print("   3. Test camera: rpicam-hello")
            print("   4. Check camera connection and cable")
            sys.exit(1)
    
    def initialize_face_recognition(self):
        """Initialize face recognition system and load known faces database"""
        if not self.config.ENABLE_FACE_RECOGNITION:
            print("ℹ️  Face recognition disabled in config")
            return
        
        if not FACE_RECOGNITION_AVAILABLE:
            print("⚠️  face_recognition library not available - recognition disabled")
            print("   Install with: pip install face_recognition")
            return
        
        try:
            # Load known faces database
            db_path = Path(self.config.FACE_DATABASE_PATH)
            if db_path.exists():
                print(f"📚 Loading face database from {db_path}...")
                with open(db_path, 'r') as f:
                    data = json.load(f)
                
                self.known_face_encodings = []
                self.known_face_names = []
                
                for person_name, encodings in data.items():
                    for encoding in encodings:
                        # Convert list back to numpy array
                        encoding_array = np.array(encoding)
                        self.known_face_encodings.append(encoding_array)
                        self.known_face_names.append(person_name)
                
                if len(self.known_face_names) > 0:
                    unique_names = set(self.known_face_names)
                    print(f"✅ Loaded {len(self.known_face_names)} face encoding(s) for {len(unique_names)} person(s)")
                    for name in unique_names:
                        count = self.known_face_names.count(name)
                        print(f"   - {name}: {count} encoding(s)")
                    self.face_recognition_enabled = True
                else:
                    print("⚠️  Face database is empty - recognition disabled")
            else:
                print(f"ℹ️  Face database not found at {db_path}")
                print("   Run enrollment script to add faces: python3 enroll_face.py")
                print("   Recognition will be disabled until faces are enrolled")
        
        except Exception as e:
            print(f"⚠️  Error loading face database: {e}")
            print("   Recognition disabled")
    
    def initialize_api_integration(self):
        """Initialize API and n8n integration"""
        if not self.config.ENABLE_N8N_INTEGRATION and not self.config.API_SERVER_ENABLED:
            return
        
        try:
            # Try to import API server module
            from api_server import (
                N8NWebhookClient, 
                FrameStorageManager,
                initialize_api_server,
                create_detection_event
            )
            
            # Initialize n8n webhook client if enabled
            if self.config.ENABLE_N8N_INTEGRATION and self.config.N8N_WEBHOOK_URL:
                self.n8n_client = N8NWebhookClient(webhook_url=self.config.N8N_WEBHOOK_URL)
                print(f"✅ n8n webhook client initialized: {self.config.N8N_WEBHOOK_URL}")
            
            # Initialize frame storage
            if self.config.API_FRAME_STORAGE_DIR:
                self.api_frame_storage = FrameStorageManager(
                    storage_dir=self.config.API_FRAME_STORAGE_DIR,
                    base_url=self.config.API_FRAME_BASE_URL
                )
                print(f"✅ Frame storage initialized: {self.config.API_FRAME_STORAGE_DIR}")
            
            # Start API server if enabled
            if self.config.API_SERVER_ENABLED:
                webhook_url = self.config.N8N_WEBHOOK_URL if self.config.ENABLE_N8N_INTEGRATION else None
                initialize_api_server(
                    webhook_url=webhook_url,
                    storage_dir=self.config.API_FRAME_STORAGE_DIR,
                    base_url=self.config.API_FRAME_BASE_URL,
                    host=self.config.API_SERVER_HOST,
                    port=self.config.API_SERVER_PORT
                )
                print(f"✅ API server started on {self.config.API_SERVER_HOST}:{self.config.API_SERVER_PORT}")
            
            # Store create_detection_event function for later use
            self.create_detection_event = create_detection_event
            
        except ImportError as e:
            print(f"⚠️  API integration not available: {e}")
            print("   Install with: pip install fastapi uvicorn httpx")
        except Exception as e:
            print(f"⚠️  Error initializing API integration: {e}")
    
    def send_detection_event(self, boxes, scores, names, frame=None):
        """
        Send detection event to n8n
        
        Args:
            boxes: List of bounding boxes
            scores: List of confidence scores
            names: List of recognized names
            frame: Optional frame numpy array
        """
        if not self.n8n_client or len(boxes) == 0 or not self.create_detection_event:
            return
        
        try:
            # Prepare detections
            detections = []
            for i, (box, score) in enumerate(zip(boxes, scores)):
                name = names[i] if i < len(names) else None
                detections.append({
                    "label": "face",
                    "confidence": float(score),
                    "bbox": [float(x) for x in box[:4]] if len(box) >= 4 else [0, 0, 0, 0],
                    "name": name
                })
            
            # Create event
            event = self.create_detection_event(
                camera_id=self.config.CAMERA_ID,
                event_type="face_detected",
                detections=detections,
                frame=frame,
                metadata={
                    "frame_count": self.frame_count,
                    "fps": self.current_fps
                }
            )
            
            # Send to n8n
            self.n8n_client.send_event(event, async_send=True)
        
        except Exception as e:
            print(f"⚠️  Error sending detection event: {e}")
    
    def send_unknown_person_alert(self, boxes, scores, frame):
        """
        Send alert for unknown person detection with captured image
        
        Args:
            boxes: List of bounding boxes for unknown faces
            scores: List of confidence scores
            frame: Frame numpy array with the unknown person
        """
        if not self.config.ENABLE_UNKNOWN_PERSON_ALERTS:
            return
        
        if not self.n8n_client or len(boxes) == 0 or not self.create_detection_event:
            return
        
        try:
            import hashlib
            
            # Filter for unknown faces only and check cooldown
            unknown_detections = []
            unknown_boxes = []
            unknown_scores = []
            current_time = time.time()
            
            for i, (box, score) in enumerate(zip(boxes, scores)):
                # Check if this is an unknown face (name would be "Unknown" or None)
                # We'll check this by seeing if recognition is enabled and face wasn't recognized
                # For now, we'll send alert for all faces if recognition is disabled
                # or if we detect unknown faces
                
                # Create a hash of the bbox for cooldown tracking
                bbox_str = f"{box[0]:.1f},{box[1]:.1f},{box[2]:.1f},{box[3]:.1f}"
                bbox_hash = hashlib.md5(bbox_str.encode()).hexdigest()
                
                # Check cooldown
                if bbox_hash in self.last_unknown_alert_time:
                    time_since_last = current_time - self.last_unknown_alert_time[bbox_hash]
                    if time_since_last < self.config.UNKNOWN_PERSON_ALERT_COOLDOWN:
                        continue  # Skip this detection (still in cooldown)
                
                # Add to unknown detections
                unknown_boxes.append(box)
                unknown_scores.append(score)
                unknown_detections.append({
                    "label": "unknown_person",
                    "confidence": float(score),
                    "bbox": [float(x) for x in box[:4]] if len(box) >= 4 else [0, 0, 0, 0],
                    "name": None
                })
                
                # Update last alert time
                self.last_unknown_alert_time[bbox_hash] = current_time
            
            # Only send alert if we have unknown detections
            if len(unknown_detections) == 0:
                return
            
            # Crop the frame to show the unknown person(s) more clearly
            # Get bounding box that encompasses all unknown faces
            if len(unknown_boxes) > 0:
                min_x = min(box[0] for box in unknown_boxes)
                min_y = min(box[1] for box in unknown_boxes)
                max_x = max(box[2] for box in unknown_boxes)
                max_y = max(box[3] for box in unknown_boxes)
                
                # Add padding
                padding = 20
                h, w = frame.shape[:2]
                crop_x1 = max(0, int(min_x) - padding)
                crop_y1 = max(0, int(min_y) - padding)
                crop_x2 = min(w, int(max_x) + padding)
                crop_y2 = min(h, int(max_y) + padding)
                
                # Crop frame
                cropped_frame = frame[crop_y1:crop_y2, crop_x1:crop_x2]
            else:
                cropped_frame = frame
            
            # Create alert event
            event = self.create_detection_event(
                camera_id=self.config.CAMERA_ID,
                event_type="unknown_person_detected",
                detections=unknown_detections,
                frame=cropped_frame,  # Send cropped frame focusing on unknown person
                metadata={
                    "frame_count": self.frame_count,
                    "fps": self.current_fps,
                    "alert_type": "unknown_person",
                    "count": len(unknown_detections),
                    "cooldown_seconds": self.config.UNKNOWN_PERSON_ALERT_COOLDOWN
                }
            )
            
            # Send to n8n
            self.n8n_client.send_event(event, async_send=True)
            
            print(f"🚨 Unknown person alert sent: {len(unknown_detections)} unknown face(s) detected")
        
        except Exception as e:
            print(f"⚠️  Error sending unknown person alert: {e}")
    
    def initialize_display(self):
        """Initialize tkinter display window"""
        if not DISPLAY_AVAILABLE:
            if not TKINTER_AVAILABLE:
                print("⚠️  tkinter not available - running in console-only mode")
            elif not IMAGETK_AVAILABLE:
                print("⚠️  ImageTk not available - running in console-only mode")
                print("   Install with: sudo apt install -y python3-pil.imagetk")
            self.display_enabled = False
            return
        
        try:
            self.root = tk.Tk()
            self.root.title("Raspberry Pi Face Detection")
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            # Create label for displaying frames
            self.display_label = tk.Label(self.root)
            self.display_label.pack()
            
            self.display_enabled = True
            print("✅ Display window initialized")
        except Exception as e:
            print(f"⚠️  Could not initialize display window: {e}")
            print("   Running in console-only mode")
            self.display_enabled = False
    
    def update_display(self, frame):
        """
        Update the display window with a new frame
        
        Args:
            frame: PIL Image or numpy array (RGB format)
        """
        if not self.display_enabled or self.root is None or self.display_label is None:
            return
        
        if not IMAGETK_AVAILABLE:
            return
        
        try:
            # Convert to PIL Image if needed
            if isinstance(frame, np.ndarray):
                pil_image = Image.fromarray(frame)
            else:
                pil_image = frame
            
            # Resize if needed to fit window (optional - can be removed for full resolution)
            # For now, keep original size
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image=pil_image)
            
            # Update label
            self.display_label.configure(image=photo)
            self.display_label.image = photo  # Keep a reference
            
            # Update window size to match image
            self.root.geometry(f"{pil_image.width}x{pil_image.height}")
            
            # Process tkinter events (non-blocking)
            self.root.update_idletasks()
            self.root.update()
            
        except Exception as e:
            # Silently handle display errors to avoid breaking the main loop
            pass
    
    def on_closing(self):
        """Handle window closing event"""
        print("\n🛑 Window closed by user")
        self.is_running = False
        if self.root:
            self.root.destroy()
    
    def detect_faces(self, frame):
        """
        Detect faces in a frame using YOLO
        
        Args:
            frame: Input image frame (RGB format from picamera2)
            
        Returns:
            tuple: (boxes, scores) - bounding boxes and confidence scores
        """
        if self.model is None:
            return [], []
        
        # Validate frame
        if frame is None or (isinstance(frame, np.ndarray) and frame.size == 0):
            return [], []
        
        try:
            H, W = frame.shape[:2]
        except (AttributeError, IndexError):
            return [], []
        
        # Resize frame for faster processing
        if self.config.RESIZE_FACTOR != 1.0:
            new_w = int(W * self.config.RESIZE_FACTOR)
            new_h = int(H * self.config.RESIZE_FACTOR)
            # Use PIL for resizing (more efficient than numpy)
            pil_image = Image.fromarray(frame)
            pil_image = pil_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
            frame_resized = np.array(pil_image)
            scale_factor = 1.0 / self.config.RESIZE_FACTOR
        else:
            frame_resized = frame
            scale_factor = 1.0
        
        try:
            # Run YOLO detection
            results = self.model(
                frame_resized, 
                conf=self.config.CONFIDENCE_THRESHOLD,
                iou=self.config.IOU_THRESHOLD,
                verbose=False
            )
            
            boxes = []
            scores = []
            
            if len(results) > 0 and results[0].boxes is not None:
                yolo_boxes = results[0].boxes
                if len(yolo_boxes) > 0:
                    # Filter for face class (class 0 in face detection models)
                    face_mask = yolo_boxes.cls == 0
                    if face_mask.any():
                        boxes = yolo_boxes.xyxy[face_mask].cpu().numpy()
                        scores = yolo_boxes.conf[face_mask].cpu().numpy()
                        
                        # Scale boxes back to original frame size
                        if scale_factor != 1.0:
                            boxes *= scale_factor
            
            # Ensure we return lists, not numpy arrays
            if isinstance(boxes, np.ndarray):
                boxes = boxes.tolist()
            if isinstance(scores, np.ndarray):
                scores = scores.tolist()
            
            # Ensure boxes and scores are lists
            if not isinstance(boxes, list):
                boxes = list(boxes) if boxes else []
            if not isinstance(scores, list):
                scores = list(scores) if scores else []
            
            return boxes, scores
            
        except Exception as e:
            print(f"⚠️ Error in face detection: {e}")
            return [], []
    
    def recognize_faces(self, frame, boxes):
        """
        Recognize faces in detected boxes using face encodings
        
        Args:
            frame: Input frame (numpy array, RGB format)
            boxes: List of bounding boxes
            
        Returns:
            list: List of recognized names (or "Unknown" for unrecognized faces)
        """
        if not self.face_recognition_enabled or len(self.known_face_encodings) == 0:
            return ["Unknown"] * len(boxes) if boxes else []
        
        if not FACE_RECOGNITION_AVAILABLE or len(boxes) == 0:
            return ["Unknown"] * len(boxes) if boxes else []
        
        try:
            # Convert boxes to face_recognition format (top, right, bottom, left)
            face_locations = []
            for box in boxes:
                if len(box) >= 4:
                    x1, y1, x2, y2 = map(int, box[:4])
                    # face_recognition uses (top, right, bottom, left)
                    face_locations.append((y1, x2, y2, x1))
            
            if len(face_locations) == 0:
                return []
            
            # Extract face encodings from the frame
            # face_recognition expects RGB format (which picamera2 provides)
            face_encodings = face_recognition.face_encodings(frame, face_locations)
            
            # Match each face encoding with known faces
            names = []
            for face_encoding in face_encodings:
                # Compare with known faces
                matches = face_recognition.compare_faces(
                    self.known_face_encodings, 
                    face_encoding, 
                    tolerance=self.config.RECOGNITION_TOLERANCE
                )
                
                # Find the best match
                name = "Unknown"
                if True in matches:
                    # Get the distances to all known faces
                    face_distances = face_recognition.face_distance(
                        self.known_face_encodings, 
                        face_encoding
                    )
                    # Get the index of the best match
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
                
                names.append(name)
            
            return names
            
        except Exception as e:
            print(f"⚠️ Error in face recognition: {e}")
            return ["Unknown"] * len(boxes) if boxes else []
    
    def draw_detections(self, frame, boxes, scores, names=None):
        """
        Draw bounding boxes and labels on the frame using PIL
        
        Args:
            frame: Input frame (numpy array, RGB format)
            boxes: List of bounding boxes (numpy array or list)
            scores: List of confidence scores (numpy array or list)
        """
        # Convert to lists if numpy arrays
        if isinstance(boxes, np.ndarray):
            boxes = boxes.tolist()
        if isinstance(scores, np.ndarray):
            scores = scores.tolist()
        
        # Ensure boxes and scores are lists
        if not isinstance(boxes, list):
            boxes = list(boxes) if boxes else []
        if not isinstance(scores, list):
            scores = list(scores) if scores else []
        
        # Safety check: ensure boxes and scores have same length
        min_len = min(len(boxes), len(scores))
        if min_len == 0:
            return frame
        
        boxes = boxes[:min_len]
        scores = scores[:min_len]
        
        # Convert to PIL Image for drawing
        pil_image = Image.fromarray(frame)
        draw = ImageDraw.Draw(pil_image)
        
        # Try to load a font, fall back to default if not available
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 16)
            except:
                font = ImageFont.load_default()
        
        # Ensure names list matches boxes length
        if names is None:
            names = ["Unknown"] * len(boxes)
        elif len(names) != len(boxes):
            names = names[:len(boxes)] + ["Unknown"] * (len(boxes) - len(names))
        
        for i, (box, score) in enumerate(zip(boxes, scores)):
            try:
                # Ensure box is a list/array with 4 elements
                if not box or len(box) < 4:
                    continue
                x1, y1, x2, y2 = map(int, box[:4])
                
                # Ensure score is a number
                if isinstance(score, (np.ndarray, np.generic)):
                    score = float(score)
                else:
                    score = float(score)
                
                # Get name for this face
                name = names[i] if i < len(names) else "Unknown"
                
                # Choose color based on recognition
                if name != "Unknown" and self.face_recognition_enabled:
                    box_color = self.config.RECOGNIZED_COLOR
                    label = f"{name} ({score:.2f})"
                else:
                    box_color = self.config.UNKNOWN_COLOR if self.face_recognition_enabled else self.config.BOX_COLOR
                    label = f"{name}: {score:.2f}" if self.face_recognition_enabled else f"Face: {score:.2f}"
                
                # Draw bounding box
                draw.rectangle([x1, y1, x2, y2], outline=box_color, width=2)
                
                # Get text size for background
                bbox = draw.textbbox((0, 0), label, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # Draw background rectangle for text
                draw.rectangle([x1, y1 - text_height - 4, x1 + text_width + 4, y1], 
                              fill=box_color)
                
                # Draw text
                draw.text((x1 + 2, y1 - text_height - 2), label, fill=(0, 0, 0), font=font)
            except (ValueError, TypeError, IndexError, AttributeError) as e:
                # Skip this detection if there's an error
                continue
        
        # Convert back to numpy array
        return np.array(pil_image)
    
    def add_performance_info(self, frame):
        """
        Add performance information overlay to the frame using PIL
        
        Args:
            frame: Input frame (numpy array, RGB format)
        """
        if not self.config.SHOW_FPS and not self.config.SHOW_DETECTION_INFO and not self.config.SHOW_PERFORMANCE_STATS:
            return frame
        
        # Validate frame
        if frame is None or (isinstance(frame, np.ndarray) and frame.size == 0):
            return frame
        
        try:
            # Convert to PIL Image
            pil_image = Image.fromarray(frame)
            draw = ImageDraw.Draw(pil_image)
            
            # Try to load a font
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
            except:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf", 14)
                except:
                    font = ImageFont.load_default()
            
            info_lines = []
            y_offset = 10
            
            # FPS information
            if self.config.SHOW_FPS:
                info_lines.append(f"FPS: {self.current_fps:.1f}")
            
            # Detection information
            if self.config.SHOW_DETECTION_INFO:
                num_faces = len(self.last_boxes) if isinstance(self.last_boxes, (list, np.ndarray)) else 0
                info_lines.append(f"Faces: {num_faces}")
                if self.processing_times and len(self.processing_times) > 0:
                    try:
                        avg_time = np.mean(self.processing_times[-10:])  # Last 10 frames
                        info_lines.append(f"Avg Time: {avg_time*1000:.1f}ms")
                    except (ValueError, TypeError):
                        pass  # Skip if calculation fails
            
            # Performance stats
            if self.config.SHOW_PERFORMANCE_STATS:
                info_lines.append(f"Frame: {self.frame_count}")
                info_lines.append(f"Queue: {self.frame_queue.qsize()}")
            
            # Draw information
            for i, line in enumerate(info_lines):
                # Draw text with outline for visibility
                x, y = 10, y_offset + i * 20
                draw.text((x, y), line, fill=self.config.TEXT_COLOR, font=font)
            
            # Convert back to numpy array
            return np.array(pil_image)
        except Exception as e:
            # Return original frame if there's an error
            return frame
    
    def calculate_fps(self):
        """Calculate current FPS"""
        self.fps_counter += 1
        current_time = time.time()
        
        try:
            time_diff = current_time - self.fps_start_time
            if time_diff >= 1.0:  # Update every second
                if time_diff > 0:
                    self.current_fps = self.fps_counter / time_diff
                else:
                    self.current_fps = 0.0
                self.fps_counter = 0
                self.fps_start_time = current_time
        except (ZeroDivisionError, ValueError):
            self.current_fps = 0.0
    
    def process_frames_parallel(self):
        """Process frames in a separate thread for parallel processing"""
        while self.is_running:
            try:
                frame, frame_id = self.frame_queue.get(timeout=1.0)
                
                # Perform face detection
                start_time = time.time()
                boxes, scores = self.detect_faces(frame)
                
                # Recognize faces if enabled (this adds some processing time)
                names = []
                if self.face_recognition_enabled and len(boxes) > 0:
                    names = self.recognize_faces(frame, boxes)
                
                processing_time = time.time() - start_time
                
                # Put result in queue (including names)
                self.result_queue.put((frame, boxes, scores, names, processing_time, frame_id))
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"⚠️ Error in parallel processing: {e}")
    
    def run(self):
        """Main detection loop"""
        print("🎬 Starting face detection and recognition...")
        print("📋 System Information:")
        print("   - Camera: Raspberry Pi Camera Module (picamera2)")
        if self.face_recognition_enabled:
            print(f"   - Face Recognition: Enabled ({len(self.known_face_names)} encoding(s) loaded)")
        else:
            print("   - Face Recognition: Disabled")
        if self.display_enabled:
            print("   - Display: Window + Console output")
            print("   - Close window or Press Ctrl+C to quit")
        else:
            print("   - Display: Console output only")
            print("   - Press Ctrl+C to quit")
        print()
        
        self.is_running = True
        paused = False
        
        # Start parallel processing thread
        if self.config.ENABLE_PARALLEL_PROCESSING:
            self.processing_thread = threading.Thread(target=self.process_frames_parallel, daemon=True)
            self.processing_thread.start()
        
        try:
            while True:
                # Read frame from picamera2
                try:
                    frame = self.picam2.capture_array()
                    if frame is None or frame.size == 0:
                        print("⚠️  Warning: Empty frame from picamera2")
                        time.sleep(0.1)
                        continue
                    
                    # Validate frame shape
                    if len(frame.shape) < 2 or frame.shape[0] == 0 or frame.shape[1] == 0:
                        print("⚠️  Warning: Invalid frame shape from picamera2")
                        time.sleep(0.1)
                        continue
                except Exception as e:
                    print(f"❌ Error reading frame from picamera2: {e}")
                    time.sleep(0.1)
                    continue  # Continue instead of breaking to be more resilient
                
                self.frame_count += 1
                
                # Skip frames for performance
                should_process = True
                if self.config.SKIP_FRAMES > 0 and self.frame_count % (self.config.SKIP_FRAMES + 1) != 0:
                    should_process = False
                
                # Process frame
                if not paused:
                    if self.config.ENABLE_PARALLEL_PROCESSING and should_process:
                        # Add frame to processing queue
                        try:
                            self.frame_queue.put_nowait((frame.copy(), self.frame_count))
                        except queue.Full:
                            pass  # Skip frame if queue is full
                        
                        # Get results from result queue
                        try:
                            processed_frame, boxes, scores, names, processing_time, frame_id = self.result_queue.get_nowait()
                            # Convert to lists if numpy arrays
                            if isinstance(boxes, np.ndarray):
                                self.last_boxes = boxes.tolist()
                            else:
                                self.last_boxes = list(boxes) if boxes else []
                            if isinstance(scores, np.ndarray):
                                self.last_scores = scores.tolist()
                            else:
                                self.last_scores = list(scores) if scores else []
                            self.last_names = names if names else []
                            self.last_detection_time = time.time()
                            self.processing_times.append(processing_time)
                            
                            # Keep only last 30 processing times
                            if len(self.processing_times) > 30:
                                self.processing_times.pop(0)
                            
                            # Draw detections with names
                            frame = self.draw_detections(frame, boxes, scores, self.last_names)
                            
                            # Send detection event to n8n if enabled
                            if self.n8n_client and len(boxes) > 0:
                                self.send_detection_event(boxes, scores, self.last_names, frame)
                                
                                # Check for unknown persons and send alert
                                if self.config.ENABLE_UNKNOWN_PERSON_ALERTS:
                                    # Filter for unknown faces
                                    unknown_boxes = []
                                    unknown_scores = []
                                    for i, name in enumerate(self.last_names):
                                        if name == "Unknown" or name is None:
                                            unknown_boxes.append(boxes[i])
                                            unknown_scores.append(scores[i])
                                    
                                    if len(unknown_boxes) > 0:
                                        self.send_unknown_person_alert(unknown_boxes, unknown_scores, frame)
                        except queue.Empty:
                            # Use cached results if no new results available
                            if time.time() - self.last_detection_time < 0.5:  # Use cache for 0.5 seconds
                                cached_scores = self.last_scores if len(self.last_scores) == len(self.last_boxes) else [0.9] * len(self.last_boxes)
                                cached_names = self.last_names if len(self.last_names) == len(self.last_boxes) else ["Unknown"] * len(self.last_boxes)
                                frame = self.draw_detections(frame, self.last_boxes, cached_scores, cached_names)
                    else:
                        # Synchronous processing
                        if should_process:
                            start_time = time.time()
                            boxes, scores = self.detect_faces(frame)
                            
                            # Recognize faces if enabled
                            names = []
                            if self.face_recognition_enabled and len(boxes) > 0:
                                names = self.recognize_faces(frame, boxes)
                            
                            processing_time = time.time() - start_time
                            # Convert to lists if numpy arrays
                            if isinstance(boxes, np.ndarray):
                                self.last_boxes = boxes.tolist()
                            else:
                                self.last_boxes = list(boxes) if boxes else []
                            if isinstance(scores, np.ndarray):
                                self.last_scores = scores.tolist()
                            else:
                                self.last_scores = list(scores) if scores else []
                            self.last_names = names if names else []
                            self.last_detection_time = time.time()
                            self.processing_times.append(processing_time)
                            
                            # Keep only last 30 processing times
                            if len(self.processing_times) > 30:
                                self.processing_times.pop(0)
                            
                            # Draw detections with names
                            frame = self.draw_detections(frame, boxes, scores, self.last_names)
                            
                            # Send detection event to n8n if enabled
                            if self.n8n_client and len(boxes) > 0:
                                self.send_detection_event(boxes, scores, self.last_names, frame)
                                
                                # Check for unknown persons and send alert
                                if self.config.ENABLE_UNKNOWN_PERSON_ALERTS:
                                    # Filter for unknown faces
                                    unknown_boxes = []
                                    unknown_scores = []
                                    for i, name in enumerate(self.last_names):
                                        if name == "Unknown" or name is None:
                                            unknown_boxes.append(boxes[i])
                                            unknown_scores.append(scores[i])
                                    
                                    if len(unknown_boxes) > 0:
                                        self.send_unknown_person_alert(unknown_boxes, unknown_scores, frame)
                
                # Calculate FPS
                self.calculate_fps()
                
                # Add performance information
                frame = self.add_performance_info(frame)
                
                # Print to console if enabled
                if self.config.PRINT_TO_CONSOLE and should_process:
                    num_faces = len(self.last_boxes) if isinstance(self.last_boxes, (list, np.ndarray)) else 0
                    if num_faces > 0:
                        # Format scores safely
                        try:
                            # Convert scores to list of floats
                            score_list = []
                            for s in self.last_scores:
                                if isinstance(s, (np.ndarray, np.generic)):
                                    score_list.append(float(s))
                                else:
                                    score_list.append(float(s))
                            scores_str = [f'{s:.2f}' for s in score_list]
                        except (ValueError, TypeError):
                            scores_str = ['N/A'] * num_faces
                        
                        # Format names if recognition is enabled
                        if self.face_recognition_enabled and len(self.last_names) > 0:
                            names_str = ", ".join(self.last_names)
                            print(f"Frame {self.frame_count}: {num_faces} face(s) detected | "
                                  f"FPS: {self.current_fps:.1f} | "
                                  f"Names: {names_str} | "
                                  f"Confidence: {scores_str}")
                        else:
                            print(f"Frame {self.frame_count}: {num_faces} face(s) detected | "
                                  f"FPS: {self.current_fps:.1f} | "
                                  f"Confidence: {scores_str}")
                
                # Add pause indicator
                if paused:
                    try:
                        pil_image = Image.fromarray(frame)
                        draw = ImageDraw.Draw(pil_image)
                        try:
                            font = ImageFont.load_default()
                        except:
                            font = None
                        frame_height = frame.shape[0] if isinstance(frame, np.ndarray) else pil_image.height
                        draw.text((10, frame_height - 20), "PAUSED - Press Ctrl+C to quit", 
                                 fill=self.config.WARNING_COLOR, font=font)
                        frame = np.array(pil_image)
                    except Exception:
                        pass  # Skip pause indicator if there's an error
                
                # Update display window
                self.update_display(frame)
                
                # Check if window was closed
                if not self.is_running:
                    break
                
                # Small delay to prevent overwhelming the system
                time.sleep(0.01)
        
        except KeyboardInterrupt:
            print("\n🛑 Interrupted by user")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("🧹 Cleaning up...")
        self.is_running = False
        
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=1.0)
        
        # Clean up camera
        if self.picam2:
            try:
                self.picam2.stop()
            except:
                pass
        
        # Clean up display window
        if self.root:
            try:
                self.root.destroy()
            except:
                pass
        
        print("✅ Cleanup complete")

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Raspberry Pi 5 Face Detection System (Picamera2 Only)")
    parser.add_argument("--model", type=str, default="yolov12n-face.pt", 
                       help="Path to YOLO model file")
    parser.add_argument("--conf", type=float, default=0.5, 
                       help="Confidence threshold (0.0-1.0)")
    parser.add_argument("--width", type=int, default=640, 
                       help="Camera width")
    parser.add_argument("--height", type=int, default=480, 
                       help="Camera height")
    parser.add_argument("--resize", type=float, default=0.75, 
                       help="Resize factor for processing (0.1-1.0)")
    parser.add_argument("--skip-frames", type=int, default=2, 
                       help="Number of frames to skip between processing")
    parser.add_argument("--no-parallel", action="store_true", 
                       help="Disable parallel processing")
    parser.add_argument("--no-console", action="store_true",
                       help="Disable console output")
    
    args = parser.parse_args()
    
    # Create configuration
    config = Config()
    config.MODEL_PATH = args.model
    config.CONFIDENCE_THRESHOLD = args.conf
    config.CAMERA_WIDTH = args.width
    config.CAMERA_HEIGHT = args.height
    config.RESIZE_FACTOR = args.resize
    config.SKIP_FRAMES = args.skip_frames
    config.ENABLE_PARALLEL_PROCESSING = not args.no_parallel
    config.PRINT_TO_CONSOLE = not args.no_console
    
    # Validate arguments
    if not (0.0 <= args.conf <= 1.0):
        print("❌ Error: Confidence threshold must be between 0.0 and 1.0")
        sys.exit(1)
    
    if not (0.1 <= args.resize <= 1.0):
        print("❌ Error: Resize factor must be between 0.1 and 1.0")
        sys.exit(1)
    
    # Create and run detector
    detector = RaspberryPiFaceDetector(config)
    detector.run()

if __name__ == "__main__":
    main()
