#!/usr/bin/env python3
"""
Face Enrollment Script for Raspberry Pi 5 (Video-Based)
========================================================

This script processes a video file to enroll faces into the face recognition database.
The user provides a video of their face rotating, and the system extracts face encodings
from multiple frames automatically.

Usage:
    python3 enroll_face.py --name "John Doe" --video "face_video.mp4"
    python3 enroll_face.py --name "Jane Smith" --video "video.mp4" --max-frames 20

Author: AI Assistant
Date: 2024
"""

import numpy as np
import json
import argparse
import sys
from pathlib import Path

# Try to import face_recognition library
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    face_recognition = None
    print("❌ face_recognition library not available.")
    print("   Install with: python3 -m pip install --break-system-packages face_recognition")
    sys.exit(1)

# Try to import imageio for video processing (lightweight)
try:
    import imageio
    IMAGEIO_AVAILABLE = True
except ImportError:
    IMAGEIO_AVAILABLE = False
    imageio = None
    print("❌ imageio library not available.")
    print("   Install with: python3 -m pip install --break-system-packages imageio imageio-ffmpeg")
    sys.exit(1)

# Configuration
# Get base directory (parent of src/)
BASE_DIR = Path(__file__).parent.parent
FACE_DATABASE_PATH = str(BASE_DIR / "known_faces.json")
DEFAULT_MAX_FRAMES = 30  # Maximum number of frames to process
FRAME_SKIP = 5  # Process every Nth frame (for efficiency)
MIN_FACE_SIZE = 80  # Minimum face size in pixels
FACE_DETECTION_MODEL = "hog"  # "hog" (faster) or "cnn" (more accurate, slower)


def load_database():
    """Load existing face database"""
    db_path = Path(FACE_DATABASE_PATH)
    if db_path.exists():
        try:
            with open(db_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Error loading database: {e}")
            return {}
    return {}


def save_database(data):
    """Save face database to file"""
    db_path = Path(FACE_DATABASE_PATH)
    try:
        with open(db_path, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"✅ Database saved to {db_path}")
        return True
    except Exception as e:
        print(f"❌ Error saving database: {e}")
        return False


def resize_frame_if_needed(frame, max_dimension=800):
    """
    Resize frame if too large (for efficiency on Raspberry Pi)
    
    Args:
        frame: Input frame (numpy array)
        max_dimension: Maximum width or height
        
    Returns:
        Resized frame
    """
    height, width = frame.shape[:2]
    
    if max(width, height) > max_dimension:
        # Calculate scaling factor
        scale = max_dimension / max(width, height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        
        # Use PIL for resizing (more efficient than numpy)
        from PIL import Image
        pil_image = Image.fromarray(frame)
        pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        return np.array(pil_image)
    
    return frame


def extract_face_encodings_from_frame(frame):
    """
    Extract face encodings from a single frame
    
    Args:
        frame: Input frame (numpy array, RGB format)
        
    Returns:
        List of face encodings (each encoding is a 128-dimensional vector)
    """
    try:
        # Resize frame for faster processing (if needed)
        frame_resized = resize_frame_if_needed(frame, max_dimension=800)
        
        # Detect face locations using face_recognition (lightweight)
        # Using "hog" model for speed on Raspberry Pi
        face_locations = face_recognition.face_locations(
            frame_resized, 
            model=FACE_DETECTION_MODEL
        )
        
        if len(face_locations) == 0:
            return []
        
        # Extract encodings for all detected faces
        face_encodings = face_recognition.face_encodings(
            frame_resized, 
            face_locations
        )
        
        return face_encodings
        
    except Exception as e:
        print(f"⚠️  Error processing frame: {e}")
        return []


def process_video(video_path, max_frames=DEFAULT_MAX_FRAMES, frame_skip=FRAME_SKIP):
    """
    Process video file and extract face encodings
    
    Args:
        video_path: Path to video file
        max_frames: Maximum number of frames to process
        frame_skip: Process every Nth frame
        
    Returns:
        List of face encodings
    """
    video_path = Path(video_path)
    
    if not video_path.exists():
        print(f"❌ Video file not found: {video_path}")
        return []
    
    print(f"📹 Processing video: {video_path.name}")
    print(f"   Max frames to process: {max_frames}")
    print(f"   Frame skip: {frame_skip} (processing every {frame_skip}th frame)")
    print()
    
    encodings = []
    frame_count = 0
    processed_count = 0
    
    try:
        # Open video file
        print("   Opening video file...")
        video_path_str = str(video_path.absolute())
        print(f"   Video path: {video_path_str}")
        reader = imageio.get_reader(video_path_str)
        
        # Get video info
        fps = reader.get_meta_data().get('fps', 30)
        duration = reader.get_meta_data().get('duration', 0)
        total_frames = reader.count_frames() if hasattr(reader, 'count_frames') else 0
        
        print(f"   Video info: {fps:.1f} FPS, {duration:.1f}s duration")
        if total_frames > 0:
            print(f"   Total frames: {total_frames}")
        print()
        
        print("🎬 Processing frames...")
        print("   (This may take a few minutes on Raspberry Pi)")
        print()
        
        # Process frames
        for frame_idx, frame in enumerate(reader):
            # Skip frames for efficiency
            if frame_idx % frame_skip != 0:
                continue
            
            # Limit total frames processed
            if processed_count >= max_frames:
                break
            
            frame_count += 1
            
            # Convert to RGB if needed (imageio may return different formats)
            if len(frame.shape) == 3:
                if frame.shape[2] == 4:  # RGBA
                    from PIL import Image
                    pil_image = Image.fromarray(frame).convert('RGB')
                    frame = np.array(pil_image)
                elif frame.shape[2] == 1:  # Grayscale
                    from PIL import Image
                    pil_image = Image.fromarray(frame).convert('RGB')
                    frame = np.array(pil_image)
            
            # Extract face encodings from this frame
            frame_encodings = extract_face_encodings_from_frame(frame)
            
            if len(frame_encodings) > 0:
                # Use the first (largest) face if multiple detected
                encoding = frame_encodings[0]
                encodings.append(encoding.tolist())
                processed_count += 1
                
                if processed_count % 5 == 0:
                    print(f"   ✅ Processed {processed_count}/{max_frames} frames with faces...")
            else:
                if frame_count % 10 == 0:
                    print(f"   ⏳ Processed {frame_count} frames, found {processed_count} faces...")
        
        reader.close()
        
        print()
        print(f"✅ Video processing complete!")
        print(f"   Total frames processed: {frame_count}")
        print(f"   Frames with faces: {processed_count}")
        print(f"   Face encodings extracted: {len(encodings)}")
        
        return encodings
        
    except Exception as e:
        print(f"❌ Error processing video: {e}")
        import traceback
        traceback.print_exc()
        return []


def enroll_face_from_video(name, video_path, max_frames=DEFAULT_MAX_FRAMES, frame_skip=FRAME_SKIP):
    """
    Enroll a new face from a video file
    
    Args:
        name: Name of the person
        video_path: Path to video file
        max_frames: Maximum number of frames to process
        frame_skip: Process every Nth frame
    """
    print(f"\n👤 Enrolling face for: {name}")
    print("=" * 60)
    
    # Load existing database
    database = load_database()
    
    # Process video
    encodings = process_video(video_path, max_frames=max_frames, frame_skip=frame_skip)
    
    if len(encodings) == 0:
        print("\n❌ No face encodings extracted from video")
        print("   Make sure:")
        print("   - Video contains clear face footage")
        print("   - Face is well-lit and clearly visible")
        print("   - Video format is supported (MP4, AVI, MOV, etc.)")
        return False
    
    # Add to database
    if name not in database:
        database[name] = []
    
    database[name].extend(encodings)
    
    # Save database
    if save_database(database):
        print(f"\n✅ Successfully enrolled {name}!")
        print(f"   Added {len(encodings)} face encoding(s)")
        print(f"   Total encodings for {name}: {len(database[name])}")
        return True
    else:
        return False


def list_enrolled_faces():
    """List all enrolled faces"""
    database = load_database()
    
    if len(database) == 0:
        print("📚 No faces enrolled yet")
        return
    
    print("\n📚 Enrolled Faces:")
    print("=" * 50)
    for name, encodings in database.items():
        print(f"  {name}: {len(encodings)} encoding(s)")
    print("=" * 50)


def delete_face(name):
    """Delete a face from the database"""
    database = load_database()
    
    if name not in database:
        print(f"❌ {name} not found in database")
        return False
    
    del database[name]
    
    if save_database(database):
        print(f"✅ Deleted {name} from database")
        return True
    else:
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Enroll faces from video files for face recognition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic enrollment
  python3 enroll_face.py --name "John Doe" --video "face_video.mp4"
  
  # Process more frames for better accuracy
  python3 enroll_face.py --name "Jane Smith" --video "video.mp4" --max-frames 50
  
  # Process every frame (slower but more thorough)
  python3 enroll_face.py --name "Bob" --video "video.mp4" --frame-skip 1
  
  # List enrolled faces
  python3 enroll_face.py --list
  
  # Delete a face
  python3 enroll_face.py --delete "John Doe"

Video Requirements:
  - Supported formats: MP4, AVI, MOV, MKV, etc. (any format supported by ffmpeg)
  - Face should be clearly visible and well-lit
  - Rotating face video works best (captures multiple angles)
  - Recommended: 10-30 second video with face rotating slowly
        """
    )
    
    parser.add_argument("--name", type=str, help="Name of the person to enroll")
    parser.add_argument("--video", type=str, help="Path to video file")
    parser.add_argument("--max-frames", type=int, default=DEFAULT_MAX_FRAMES,
                       help=f"Maximum number of frames to process (default: {DEFAULT_MAX_FRAMES})")
    parser.add_argument("--frame-skip", type=int, default=FRAME_SKIP,
                       help=f"Process every Nth frame (default: {FRAME_SKIP}, lower = more thorough but slower)")
    parser.add_argument("--list", action="store_true", help="List all enrolled faces")
    parser.add_argument("--delete", type=str, help="Delete a face from the database")
    
    args = parser.parse_args()
    
    if args.list:
        list_enrolled_faces()
    elif args.delete:
        delete_face(args.delete)
    elif args.name and args.video:
        if args.max_frames < 1:
            print("❌ max-frames must be at least 1")
            sys.exit(1)
        if args.frame_skip < 1:
            print("❌ frame-skip must be at least 1")
            sys.exit(1)
        enroll_face_from_video(args.name, args.video, args.max_frames, args.frame_skip)
    else:
        parser.print_help()
        print("\n❌ Error: --name and --video are required for enrollment")
        sys.exit(1)


if __name__ == "__main__":
    main()
