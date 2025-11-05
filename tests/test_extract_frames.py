"""
Policies Applied:
- Policy 6.1: Unit test coverage for business logic
- Policy 6.5: Test naming convention (should/when pattern)
- Policy 6.6: AAA Pattern (Arrange-Act-Assert)
- Policy 6.7: Test isolation

Tests for frame extraction module.
"""
import pytest
from pathlib import Path
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from extract_frames import extract_frames_at_fps


def test_extract_frames_at_fps_basic():
    """Should extract frames at specified FPS from video file"""
    # Arrange
    video_path = Path("tests/fixtures/sample_10s.mp4")
    output_dir = Path("tests/temp/frames")
    fps = 1.0

    # Act
    frames = extract_frames_at_fps(video_path, output_dir, fps)

    # Assert
    assert len(frames) == 10  # 10 seconds * 1fps
    assert all(f.exists() for f in frames)
    assert frames[0].name.startswith("frame_")


def test_extract_frames_creates_output_dir():
    """Should create output directory if it doesn't exist"""
    # Arrange
    video_path = Path("tests/fixtures/sample_10s.mp4")
    output_dir = Path("tests/temp/frames_new")
    fps = 1.0

    # Act
    frames = extract_frames_at_fps(video_path, output_dir, fps)

    # Assert
    assert output_dir.exists()
    assert output_dir.is_dir()


def test_extract_frames_handles_invalid_video():
    """Should raise error when video file doesn't exist"""
    # Arrange
    video_path = Path("nonexistent.mp4")
    output_dir = Path("tests/temp/frames")
    fps = 1.0

    # Act & Assert
    with pytest.raises(FileNotFoundError):
        extract_frames_at_fps(video_path, output_dir, fps)
