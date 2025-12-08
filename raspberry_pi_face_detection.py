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
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Import picamera2 for Raspberry Pi Camera Module
try:
    from picamera2 import Picamera2
    PICAMERA2_AVAILABLE = True
except ImportError:
    PICAMERA2_AVAILABLE = False
    Picamera2 = None
    print("❌ picamera2 is required but not installed.")
    print("   Install with: pip install picamera2")
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
    
    # Colors (RGB format for PIL)
    BOX_COLOR = (0, 255, 0)  # Green
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
        self.last_detections = []
        self.last_detection_time = 0
        
        print("🚀 Initializing Raspberry Pi 5 Face Detection System (Picamera2 Only)...")
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
        
        H, W = frame.shape[:2]
        
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
            
            return boxes, scores
            
        except Exception as e:
            print(f"⚠️ Error in face detection: {e}")
            return [], []
    
    def draw_detections(self, frame, boxes, scores):
        """
        Draw bounding boxes and labels on the frame using PIL
        
        Args:
            frame: Input frame (numpy array, RGB format)
            boxes: List of bounding boxes
            scores: List of confidence scores
        """
        if len(boxes) == 0:
            return frame
        
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
        
        for i, (box, score) in enumerate(zip(boxes, scores)):
            x1, y1, x2, y2 = map(int, box)
            
            # Draw bounding box
            draw.rectangle([x1, y1, x2, y2], outline=self.config.BOX_COLOR, width=2)
            
            # Draw confidence score
            label = f"Face: {score:.2f}"
            # Get text size for background
            bbox = draw.textbbox((0, 0), label, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Draw background rectangle for text
            draw.rectangle([x1, y1 - text_height - 4, x1 + text_width + 4, y1], 
                          fill=self.config.BOX_COLOR)
            
            # Draw text
            draw.text((x1 + 2, y1 - text_height - 2), label, fill=(0, 0, 0), font=font)
        
        # Convert back to numpy array
        return np.array(pil_image)
    
    def add_performance_info(self, frame):
        """
        Add performance information overlay to the frame using PIL
        
        Args:
            frame: Input frame (numpy array, RGB format)
        """
        if not self.config.SHOW_FPS and not self.config.SHOW_DETECTION_INFO:
            return frame
        
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
            # Draw text with outline for visibility
            x, y = 10, y_offset + i * 20
            draw.text((x, y), line, fill=self.config.TEXT_COLOR, font=font)
        
        # Convert back to numpy array
        return np.array(pil_image)
    
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
        print("📋 System Information:")
        print("   - Camera: Raspberry Pi Camera Module (picamera2)")
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
                except Exception as e:
                    print(f"❌ Error reading frame from picamera2: {e}")
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
                            
                            # Draw detections
                            frame = self.draw_detections(frame, boxes, scores)
                        except queue.Empty:
                            # Use cached results if no new results available
                            if time.time() - self.last_detection_time < 0.5:  # Use cache for 0.5 seconds
                                frame = self.draw_detections(frame, self.last_detections, [0.9] * len(self.last_detections))
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
                            
                            # Draw detections
                            frame = self.draw_detections(frame, boxes, scores)
                
                # Calculate FPS
                self.calculate_fps()
                
                # Add performance information
                frame = self.add_performance_info(frame)
                
                # Print to console if enabled
                if self.config.PRINT_TO_CONSOLE and should_process:
                    if len(self.last_detections) > 0:
                        print(f"Frame {self.frame_count}: {len(self.last_detections)} face(s) detected | "
                              f"FPS: {self.current_fps:.1f} | "
                              f"Confidence: {[f'{s:.2f}' for s in self.last_detections]}")
                
                # Add pause indicator
                if paused:
                    pil_image = Image.fromarray(frame)
                    draw = ImageDraw.Draw(pil_image)
                    try:
                        font = ImageFont.load_default()
                    except:
                        font = None
                    draw.text((10, frame.shape[0] - 20), "PAUSED - Press Ctrl+C to quit", 
                             fill=self.config.WARNING_COLOR, font=font)
                    frame = np.array(pil_image)
                
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
