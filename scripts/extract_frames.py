"""
Policies Applied:
- Policy 3.3: SRP - Single responsibility per function
- Policy 3.5: Meaningful names
- Policy 3.6: Error handling mandatory
- Policy 3.7: No magic numbers (named constants)
- Policy 11.7: SDK over HTTP (will use opencv-python SDK)

Frame extraction module for video analysis.
"""
from pathlib import Path
from typing import List
import cv2


def extract_frames_at_fps(
    video_path: Path,
    output_dir: Path,
    fps: float
) -> List[Path]:
    """
    Extract frames from video at specified FPS using OpenCV.

    Policy 3.6: Error handling - validate inputs and raise meaningful errors
    Policy 3.5: Meaningful names - clear parameter names
    Policy 11.7: SDK over HTTP - Use opencv-python SDK

    Args:
        video_path: Path to input video file
        output_dir: Directory to save extracted frames
        fps: Frames per second to extract

    Returns:
        List of paths to extracted frame images

    Raises:
        FileNotFoundError: If video file doesn't exist
        ValueError: If fps is invalid or video cannot be opened
    """
    # Policy 3.6: Error handling mandatory
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")

    if fps <= 0:
        raise ValueError(f"FPS must be positive, got: {fps}")

    # Policy 3.7: No magic numbers
    DEFAULT_FRAME_PREFIX = "frame_"
    FRAME_NUMBER_WIDTH = 4  # Zero-pad to 4 digits

    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # Open video with OpenCV
    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        raise ValueError(f"Cannot open video file: {video_path}")

    try:
        # Get video properties
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames_in_video = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        video_duration = total_frames_in_video / video_fps if video_fps > 0 else 0

        # Calculate frame interval (every N frames to achieve target fps)
        frame_interval = int(video_fps / fps) if fps < video_fps else 1

        frames = []
        frame_count = 0
        saved_count = 0

        while True:
            ret, frame = cap.read()

            if not ret:
                break

            # Save frame at specified interval
            if frame_count % frame_interval == 0:
                frame_name = f"{DEFAULT_FRAME_PREFIX}{saved_count:0{FRAME_NUMBER_WIDTH}d}.png"
                frame_path = output_dir / frame_name

                # Save frame as PNG
                cv2.imwrite(str(frame_path), frame)
                frames.append(frame_path)
                saved_count += 1

            frame_count += 1

        return frames

    finally:
        # Always release video capture
        cap.release()
