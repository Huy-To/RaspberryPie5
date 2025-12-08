#!/usr/bin/env python3
"""
Raspberry Pi 5 Face Detection System
====================================

A real-time face detection system optimized for Raspberry Pi 5 using YOLOv12n-face.pt
Features:
- Real-time camera feed
- Optimized for Raspberry Pi 5 performance
- Configurable detection parameters
- FPS monitoring and performance stats
- Keyboard controls for runtime configuration

Author: AI Assistant
Date: 2024
"""

import cv2
import numpy as np
import time
import threading
import queue
from ultralytics import YOLO
import argparse
import os
import sys
from pathlib import Path

# Try to import picamera2 for Raspberry Pi Camera Module
try:
    from picamera2 import Picamera2
    PICAMERA2_AVAILABLE = True
except ImportError:
    PICAMERA2_AVAILABLE = False
    Picamera2 = None

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
    CAMERA_TYPE = "auto"  # "auto", "picamera2", or "opencv"
    CAMERA_INDEX = 0
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
    WINDOW_NAME = "Raspberry Pi 5 - Face Detection"
    
    # Colors (BGR format)
    BOX_COLOR = (0, 255, 0)  # Green
    TEXT_COLOR = (0, 255, 0)  # Green
    FPS_COLOR = (255, 255, 0)  # Yellow
    WARNING_COLOR = (0, 0, 255)  # Red

# ============================================================================
# FACE DETECTION SYSTEM
# ============================================================================

class RaspberryPiFaceDetector:
    """
    Face detection system optimized for Raspberry Pi 5
    """
    
    def __init__(self, config=Config()):
        """
        Initialize the face detection system
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.model = None
        self.cap = None
        self.picam2 = None
        self.camera_type = None  # "picamera2" or "opencv"
        
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
        self.last_detections = []
        self.last_detection_time = 0
        
        print("🚀 Initializing Raspberry Pi 5 Face Detection System...")
        self.initialize_model()
        self.initialize_camera()
        
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
        """Initialize camera capture - tries picamera2 first, then OpenCV"""
        print("📹 Initializing camera...")
        
        # Determine camera type
        camera_type = self.config.CAMERA_TYPE.lower()
        
        # Try picamera2 first (for Raspberry Pi Camera Module)
        if (camera_type == "auto" or camera_type == "picamera2") and PICAMERA2_AVAILABLE:
            try:
                print("   Trying picamera2 (Raspberry Pi Camera Module)...")
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
                    self.camera_type = "picamera2"
                    actual_width = test_frame.shape[1]
                    actual_height = test_frame.shape[0]
                    print(f"✅ Camera initialized (picamera2): {actual_width}x{actual_height}")
                    return
                else:
                    self.picam2.stop()
                    self.picam2 = None
            except Exception as e:
                print(f"   ⚠️  picamera2 failed: {e}")
                if self.picam2:
                    try:
                        self.picam2.stop()
                    except:
                        pass
                    self.picam2 = None
        
        # Fall back to OpenCV (for USB webcams or if picamera2 not available)
        if camera_type == "auto" or camera_type == "opencv":
            try:
                print(f"   Trying OpenCV (USB webcam at index {self.config.CAMERA_INDEX})...")
                self.cap = cv2.VideoCapture(self.config.CAMERA_INDEX)
                
                # For Raspberry Pi, try V4L2 backend
                if not self.cap.isOpened():
                    self.cap = cv2.VideoCapture(self.config.CAMERA_INDEX, cv2.CAP_V4L2)
                
                if not self.cap.isOpened():
                    raise RuntimeError("Could not open camera")
                
                # Set camera properties
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.CAMERA_WIDTH)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.CAMERA_HEIGHT)
                self.cap.set(cv2.CAP_PROP_FPS, self.config.CAMERA_FPS)
                
                # Give camera time to adjust
                time.sleep(0.5)
                
                # Test capture
                ret, test_frame = self.cap.read()
                if ret and test_frame is not None:
                    self.camera_type = "opencv"
                    actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
                    print(f"✅ Camera initialized (OpenCV): {actual_width}x{actual_height} @ {actual_fps:.1f} FPS")
                    return
                else:
                    self.cap.release()
                    self.cap = None
            except Exception as e:
                print(f"   ⚠️  OpenCV failed: {e}")
                if self.cap:
                    try:
                        self.cap.release()
                    except:
                        pass
                    self.cap = None
        
        # If we get here, both methods failed
        raise RuntimeError(
            "Could not initialize camera with either picamera2 or OpenCV.\n"
            "Troubleshooting:\n"
            "  - For Raspberry Pi Camera Module: Install picamera2 (pip install picamera2)\n"
            "  - For USB webcam: Check connection and try --camera 0, 1, or 2\n"
            "  - Enable camera in raspi-config: sudo raspi-config → Interface Options → Camera\n"
            "  - Check camera: lsusb (for USB) or rpicam-hello (for Pi Camera)"
        )
    
    def detect_faces(self, frame):
        """
        Detect faces in a frame using YOLO
        
        Args:
            frame: Input image frame (BGR format)
            
        Returns:
            tuple: (boxes, scores) - bounding boxes and confidence scores
        """
        if self.model is None:
            return [], []
        
        H, W = frame.shape[:2]
        
        # Resize frame for faster processing
        if self.config.RESIZE_FACTOR != 1.0:
            new_w = int(W * self.config.RESIZE_FACTOR)
            new_h = int(H * self.config.RESIZE_FACTOR)
            frame_resized = cv2.resize(frame, (new_w, new_h))
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
            
            return boxes, scores
            
        except Exception as e:
            print(f"⚠️ Error in face detection: {e}")
            return [], []
    
    def draw_detections(self, frame, boxes, scores):
        """
        Draw bounding boxes and labels on the frame
        
        Args:
            frame: Input frame to draw on
            boxes: List of bounding boxes
            scores: List of confidence scores
        """
        for i, (box, score) in enumerate(zip(boxes, scores)):
            x1, y1, x2, y2 = map(int, box)
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), self.config.BOX_COLOR, 2)
            
            # Draw confidence score
            label = f"Face: {score:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
            
            # Background rectangle for text
            cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
                         (x1 + label_size[0], y1), self.config.BOX_COLOR, -1)
            
            # Text
            cv2.putText(frame, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    
    def add_performance_info(self, frame):
        """
        Add performance information overlay to the frame
        
        Args:
            frame: Input frame to add overlay to
        """
        if not self.config.SHOW_FPS and not self.config.SHOW_DETECTION_INFO:
            return
        
        info_lines = []
        y_offset = 30
        
        # FPS information
        if self.config.SHOW_FPS:
            info_lines.append(f"FPS: {self.current_fps:.1f}")
        
        # Detection information
        if self.config.SHOW_DETECTION_INFO:
            info_lines.append(f"Faces: {len(self.last_detections)}")
            if self.processing_times:
                avg_time = np.mean(self.processing_times[-10:])  # Last 10 frames
                info_lines.append(f"Avg Time: {avg_time*1000:.1f}ms")
        
        # Performance stats
        if self.config.SHOW_PERFORMANCE_STATS:
            info_lines.append(f"Frame: {self.frame_count}")
            info_lines.append(f"Queue: {self.frame_queue.qsize()}")
        
        # Draw information
        for i, line in enumerate(info_lines):
            cv2.putText(frame, line, (10, y_offset + i * 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.config.TEXT_COLOR, 2)
    
    def calculate_fps(self):
        """Calculate current FPS"""
        self.fps_counter += 1
        current_time = time.time()
        
        if current_time - self.fps_start_time >= 1.0:  # Update every second
            self.current_fps = self.fps_counter / (current_time - self.fps_start_time)
            self.fps_counter = 0
            self.fps_start_time = current_time
    
    def process_frames_parallel(self):
        """Process frames in a separate thread for parallel processing"""
        while self.is_running:
            try:
                frame, frame_id = self.frame_queue.get(timeout=1.0)
                
                # Perform face detection
                start_time = time.time()
                boxes, scores = self.detect_faces(frame)
                processing_time = time.time() - start_time
                
                # Put result in queue
                self.result_queue.put((frame, boxes, scores, processing_time, frame_id))
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"⚠️ Error in parallel processing: {e}")
    
    def run(self):
        """Main detection loop"""
        print("🎬 Starting face detection...")
        print("📋 Controls:")
        print("   - 'q' or ESC: Quit")
        print("   - 'r': Reset FPS counter")
        print("   - 'f': Toggle FPS display")
        print("   - 'd': Toggle detection info")
        print("   - 's': Toggle performance stats")
        print("   - 'c': Toggle confidence threshold")
        print("   - SPACE: Pause/Resume")
        print()
        
        self.is_running = True
        paused = False
        
        # Start parallel processing thread
        if self.config.ENABLE_PARALLEL_PROCESSING:
            self.processing_thread = threading.Thread(target=self.process_frames_parallel, daemon=True)
            self.processing_thread.start()
        
        try:
            while True:
                # Read frame based on camera type
                if self.camera_type == "picamera2":
                    try:
                        frame = self.picam2.capture_array()
                        if frame is None or frame.size == 0:
                            print("⚠️  Warning: Empty frame from picamera2")
                            time.sleep(0.1)
                            continue
                        # picamera2 returns RGB, convert to BGR for OpenCV
                        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                        ret = True
                    except Exception as e:
                        print(f"❌ Error reading frame from picamera2: {e}")
                        break
                else:  # opencv
                    ret, frame = self.cap.read()
                    if not ret:
                        print("❌ Error reading frame from OpenCV camera")
                        break
                
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
                            processed_frame, boxes, scores, processing_time, frame_id = self.result_queue.get_nowait()
                            self.last_detections = boxes
                            self.last_detection_time = time.time()
                            self.processing_times.append(processing_time)
                            
                            # Keep only last 30 processing times
                            if len(self.processing_times) > 30:
                                self.processing_times.pop(0)
                            
                            self.draw_detections(frame, boxes, scores)
                        except queue.Empty:
                            # Use cached results if no new results available
                            if time.time() - self.last_detection_time < 0.5:  # Use cache for 0.5 seconds
                                self.draw_detections(frame, self.last_detections, [0.9] * len(self.last_detections))
                    else:
                        # Synchronous processing
                        if should_process:
                            start_time = time.time()
                            boxes, scores = self.detect_faces(frame)
                            processing_time = time.time() - start_time
                            self.last_detections = boxes
                            self.last_detection_time = time.time()
                            self.processing_times.append(processing_time)
                            
                            # Keep only last 30 processing times
                            if len(self.processing_times) > 30:
                                self.processing_times.pop(0)
                            
                            self.draw_detections(frame, boxes, scores)
                
                # Calculate FPS
                self.calculate_fps()
                
                # Add performance information
                self.add_performance_info(frame)
                
                # Add pause indicator
                if paused:
                    cv2.putText(frame, "PAUSED - Press SPACE to resume", (10, frame.shape[0] - 20), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.config.WARNING_COLOR, 2)
                
                # Display frame (check if display is available)
                try:
                    cv2.imshow(self.config.WINDOW_NAME, frame)
                except cv2.error as e:
                    # Handle headless mode or display issues
                    if "Can't initialize GTK backend" in str(e) or "display" in str(e).lower():
                        print("⚠️  Display not available. Running in headless mode.")
                        print("   Press Ctrl+C to stop.")
                        # Still process frames but don't display
                        time.sleep(0.1)
                        continue
                    else:
                        raise
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # 'q' or ESC
                    break
                elif key == ord('r'):  # Reset FPS
                    self.fps_counter = 0
                    self.fps_start_time = time.time()
                    print("🔄 FPS counter reset")
                elif key == ord('f'):  # Toggle FPS display
                    self.config.SHOW_FPS = not self.config.SHOW_FPS
                    print(f"📊 FPS display: {'ON' if self.config.SHOW_FPS else 'OFF'}")
                elif key == ord('d'):  # Toggle detection info
                    self.config.SHOW_DETECTION_INFO = not self.config.SHOW_DETECTION_INFO
                    print(f"👁️ Detection info: {'ON' if self.config.SHOW_DETECTION_INFO else 'OFF'}")
                elif key == ord('s'):  # Toggle performance stats
                    self.config.SHOW_PERFORMANCE_STATS = not self.config.SHOW_PERFORMANCE_STATS
                    print(f"📈 Performance stats: {'ON' if self.config.SHOW_PERFORMANCE_STATS else 'OFF'}")
                elif key == ord('c'):  # Toggle confidence threshold
                    if self.config.CONFIDENCE_THRESHOLD == 0.5:
                        self.config.CONFIDENCE_THRESHOLD = 0.3
                    elif self.config.CONFIDENCE_THRESHOLD == 0.3:
                        self.config.CONFIDENCE_THRESHOLD = 0.7
                    else:
                        self.config.CONFIDENCE_THRESHOLD = 0.5
                    print(f"🎯 Confidence threshold: {self.config.CONFIDENCE_THRESHOLD}")
                elif key == ord(' '):  # Space - Pause/Resume
                    paused = not paused
                    print(f"⏸️ {'Paused' if paused else 'Resumed'}")
        
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
        
        # Clean up camera based on type
        if self.camera_type == "picamera2" and self.picam2:
            try:
                self.picam2.stop()
            except:
                pass
        
        if self.cap:
            try:
                self.cap.release()
            except:
                pass
        
        try:
            cv2.destroyAllWindows()
        except:
            pass  # Ignore errors if no windows were created
        
        print("✅ Cleanup complete")

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Raspberry Pi 5 Face Detection System")
    parser.add_argument("--model", type=str, default="yolov12n-face.pt", 
                       help="Path to YOLO model file")
    parser.add_argument("--conf", type=float, default=0.5, 
                       help="Confidence threshold (0.0-1.0)")
    parser.add_argument("--camera-type", type=str, default="auto", 
                       choices=["auto", "picamera2", "opencv"],
                       help="Camera type: auto (try picamera2 first), picamera2, or opencv")
    parser.add_argument("--camera", type=int, default=0, 
                       help="Camera index (for OpenCV/USB webcams)")
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
    
    args = parser.parse_args()
    
    # Create configuration
    config = Config()
    config.MODEL_PATH = args.model
    config.CONFIDENCE_THRESHOLD = args.conf
    config.CAMERA_TYPE = args.camera_type
    config.CAMERA_INDEX = args.camera
    config.CAMERA_WIDTH = args.width
    config.CAMERA_HEIGHT = args.height
    config.RESIZE_FACTOR = args.resize
    config.SKIP_FRAMES = args.skip_frames
    config.ENABLE_PARALLEL_PROCESSING = not args.no_parallel
    
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
