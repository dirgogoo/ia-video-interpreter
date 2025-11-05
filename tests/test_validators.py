"""
Policies Applied:
- Policy 6.1: Unit test coverage for business logic
- Policy 6.5: Test naming convention (should/when pattern)
- Policy 6.6: AAA Pattern (Arrange-Act-Assert)
- Policy 6.7: Test isolation
- Policy 10.2: Defense in Depth - Test all validation layers

Tests for input validation module.
"""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from validators import (
    ValidationError,
    validate_video_path,
    validate_task_description,
    validate_workflow_config,
    validate_fps,
    validate_audio_language
)

# Get absolute path to test resources
TEST_DIR = Path(__file__).parent.parent
TEST_RESOURCES = TEST_DIR / "tests" / "resources"


# =============================================================================
# Video Path Validation Tests
# =============================================================================

def test_validate_video_path_valid():
    """Should accept valid video file path"""
    # Arrange
    TEST_RESOURCES.mkdir(parents=True, exist_ok=True)
    video_path = TEST_RESOURCES / "test_video.mp4"
    video_path.write_text("dummy video content")

    # Act & Assert (should not raise)
    validate_video_path(video_path)


def test_validate_video_path_none():
    """Should reject None video path"""
    # Arrange
    video_path = None

    # Act & Assert
    with pytest.raises(ValidationError, match="Video path cannot be None"):
        validate_video_path(video_path)


def test_validate_video_path_nonexistent():
    """Should reject nonexistent video file"""
    # Arrange
    video_path = Path("nonexistent_video.mp4")

    # Act & Assert
    with pytest.raises(ValidationError, match="Video file not found"):
        validate_video_path(video_path)


def test_validate_video_path_directory():
    """Should reject directory path"""
    # Arrange
    TEST_RESOURCES.mkdir(parents=True, exist_ok=True)
    video_path = TEST_RESOURCES

    # Act & Assert
    with pytest.raises(ValidationError, match="Path is not a file"):
        validate_video_path(video_path)


def test_validate_video_path_invalid_extension():
    """Should reject invalid file extension"""
    # Arrange
    TEST_RESOURCES.mkdir(parents=True, exist_ok=True)
    video_path = TEST_RESOURCES / "test_file.txt"
    video_path.write_text("not a video")

    # Act & Assert
    with pytest.raises(ValidationError, match="Invalid video file extension"):
        validate_video_path(video_path)


def test_validate_video_path_empty_file():
    """Should reject empty video file"""
    # Arrange
    TEST_RESOURCES.mkdir(parents=True, exist_ok=True)
    video_path = TEST_RESOURCES / "empty_video.mp4"
    video_path.touch()

    # Act & Assert
    with pytest.raises(ValidationError, match="Video file is empty"):
        validate_video_path(video_path)


# =============================================================================
# Task Description Validation Tests
# =============================================================================

def test_validate_task_description_valid():
    """Should accept valid task description"""
    # Arrange
    task_description = "analyze geometric shapes with measurements"

    # Act & Assert (should not raise)
    validate_task_description(task_description)


def test_validate_task_description_none():
    """Should reject None task description"""
    # Arrange
    task_description = None

    # Act & Assert
    with pytest.raises(ValidationError, match="Task description cannot be None"):
        validate_task_description(task_description)


def test_validate_task_description_empty():
    """Should reject empty task description"""
    # Arrange
    task_description = ""

    # Act & Assert
    with pytest.raises(ValidationError, match="Task description cannot be empty"):
        validate_task_description(task_description)


def test_validate_task_description_whitespace_only():
    """Should reject whitespace-only task description"""
    # Arrange
    task_description = "   "

    # Act & Assert
    with pytest.raises(ValidationError, match="Task description cannot be empty"):
        validate_task_description(task_description)


def test_validate_task_description_too_short():
    """Should reject task description shorter than minimum length"""
    # Arrange
    task_description = "ab"  # Only 2 characters

    # Act & Assert
    with pytest.raises(ValidationError, match="Task description too short"):
        validate_task_description(task_description)


def test_validate_task_description_too_long():
    """Should reject task description longer than maximum length"""
    # Arrange
    task_description = "x" * 1001  # 1001 characters

    # Act & Assert
    with pytest.raises(ValidationError, match="Task description too long"):
        validate_task_description(task_description)


# =============================================================================
# Workflow Config Validation Tests
# =============================================================================

def test_validate_workflow_config_valid():
    """Should accept valid workflow configuration"""
    # Arrange
    workflow_config = {
        "fps": 0.5,
        "agents": 5,
        "focus": "shapes"
    }

    # Act & Assert (should not raise)
    validate_workflow_config(workflow_config)


def test_validate_workflow_config_none():
    """Should reject None workflow config"""
    # Arrange
    workflow_config = None

    # Act & Assert
    with pytest.raises(ValidationError, match="Workflow config cannot be None"):
        validate_workflow_config(workflow_config)


def test_validate_workflow_config_missing_fps():
    """Should reject config missing FPS field"""
    # Arrange
    workflow_config = {
        "agents": 5,
        "focus": "shapes"
    }

    # Act & Assert
    with pytest.raises(ValidationError, match="missing required field: fps"):
        validate_workflow_config(workflow_config)


def test_validate_workflow_config_invalid_fps_type():
    """Should reject non-numeric FPS"""
    # Arrange
    workflow_config = {
        "fps": "invalid",
        "agents": 5,
        "focus": "shapes"
    }

    # Act & Assert
    with pytest.raises(ValidationError, match="FPS must be numeric"):
        validate_workflow_config(workflow_config)


def test_validate_workflow_config_fps_out_of_range():
    """Should reject FPS outside valid range"""
    # Arrange
    workflow_config = {
        "fps": 15.0,  # Too high
        "agents": 5,
        "focus": "shapes"
    }

    # Act & Assert
    with pytest.raises(ValidationError, match="FPS must be between"):
        validate_workflow_config(workflow_config)


def test_validate_workflow_config_invalid_agents_type():
    """Should reject non-integer agents"""
    # Arrange
    workflow_config = {
        "fps": 0.5,
        "agents": "five",
        "focus": "shapes"
    }

    # Act & Assert
    with pytest.raises(ValidationError, match="Agents must be integer"):
        validate_workflow_config(workflow_config)


def test_validate_workflow_config_agents_out_of_range():
    """Should reject agents count outside valid range"""
    # Arrange
    workflow_config = {
        "fps": 0.5,
        "agents": 25,  # Too high
        "focus": "shapes"
    }

    # Act & Assert
    with pytest.raises(ValidationError, match="Agents count must be between"):
        validate_workflow_config(workflow_config)


def test_validate_workflow_config_invalid_focus():
    """Should reject invalid focus value"""
    # Arrange
    workflow_config = {
        "fps": 0.5,
        "agents": 5,
        "focus": "invalid_focus"
    }

    # Act & Assert
    with pytest.raises(ValidationError, match="Invalid focus value"):
        validate_workflow_config(workflow_config)


# =============================================================================
# FPS Validation Tests
# =============================================================================

def test_validate_fps_valid():
    """Should accept valid FPS value"""
    # Arrange
    fps = 1.0

    # Act & Assert (should not raise)
    validate_fps(fps)


def test_validate_fps_non_numeric():
    """Should reject non-numeric FPS"""
    # Arrange
    fps = "invalid"

    # Act & Assert
    with pytest.raises(ValidationError, match="FPS must be numeric"):
        validate_fps(fps)


def test_validate_fps_negative():
    """Should reject negative FPS"""
    # Arrange
    fps = -1.0

    # Act & Assert
    with pytest.raises(ValidationError, match="FPS must be positive"):
        validate_fps(fps)


def test_validate_fps_zero():
    """Should reject zero FPS"""
    # Arrange
    fps = 0

    # Act & Assert
    with pytest.raises(ValidationError, match="FPS must be positive"):
        validate_fps(fps)


def test_validate_fps_out_of_range():
    """Should reject FPS outside valid range"""
    # Arrange
    fps = 15.0

    # Act & Assert
    with pytest.raises(ValidationError, match="FPS must be between"):
        validate_fps(fps)


# =============================================================================
# Audio Language Validation Tests
# =============================================================================

def test_validate_audio_language_valid():
    """Should accept valid language code"""
    # Arrange
    language = "pt"

    # Act & Assert (should not raise)
    validate_audio_language(language)


def test_validate_audio_language_none():
    """Should reject None language code"""
    # Arrange
    language = None

    # Act & Assert
    with pytest.raises(ValidationError, match="Language code cannot be None"):
        validate_audio_language(language)


def test_validate_audio_language_empty():
    """Should reject empty language code"""
    # Arrange
    language = ""

    # Act & Assert
    with pytest.raises(ValidationError, match="Language code cannot be empty"):
        validate_audio_language(language)


def test_validate_audio_language_wrong_length():
    """Should reject language code with wrong length"""
    # Arrange
    language = "por"  # 3 characters instead of 2

    # Act & Assert
    with pytest.raises(ValidationError, match="Language code must be 2 characters"):
        validate_audio_language(language)


def test_validate_audio_language_non_alphabetic():
    """Should reject non-alphabetic language code"""
    # Arrange
    language = "p1"

    # Act & Assert
    with pytest.raises(ValidationError, match="Language code must be alphabetic"):
        validate_audio_language(language)


def test_validate_audio_language_uppercase():
    """Should reject uppercase language code"""
    # Arrange
    language = "PT"

    # Act & Assert
    with pytest.raises(ValidationError, match="Language code must be lowercase"):
        validate_audio_language(language)


def test_validate_audio_language_unsupported():
    """Should reject unsupported language code"""
    # Arrange
    language = "xx"

    # Act & Assert
    with pytest.raises(ValidationError, match="Unsupported language"):
        validate_audio_language(language)
