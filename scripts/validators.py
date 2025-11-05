"""
Policies Applied:
- Policy 3.3: SRP - Single validation responsibility per function
- Policy 3.5: Meaningful names
- Policy 3.6: Error handling mandatory
- Policy 10.2: Defense in Depth - Validation at every layer

Input validation module for video-interpreter skill.
Implements defense-in-depth by validating at multiple layers.
"""
from pathlib import Path
from typing import Dict, Any


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_video_path(video_path: Path) -> None:
    """
    Validate video file path.

    Policy 10.2: Defense in Depth - Layer 1: File validation
    Policy 3.6: Error handling - raise specific errors

    Args:
        video_path: Path to video file

    Raises:
        ValidationError: If path is invalid, file doesn't exist, or not a video file
    """
    # Check if path is provided
    if video_path is None:
        raise ValidationError("Video path cannot be None")

    # Check if file exists
    if not video_path.exists():
        raise ValidationError(f"Video file not found: {video_path}")

    # Check if it's a file (not directory)
    if not video_path.is_file():
        raise ValidationError(f"Path is not a file: {video_path}")

    # Check file extension
    valid_extensions = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv"}
    if video_path.suffix.lower() not in valid_extensions:
        raise ValidationError(
            f"Invalid video file extension: {video_path.suffix}. "
            f"Supported: {', '.join(valid_extensions)}"
        )

    # Check file size (must be > 0 bytes)
    if video_path.stat().st_size == 0:
        raise ValidationError(f"Video file is empty: {video_path}")


def validate_task_description(task_description: str) -> None:
    """
    Validate task description input.

    Policy 10.2: Defense in Depth - Layer 2: Input validation
    Policy 3.6: Error handling - raise specific errors

    Args:
        task_description: User's task description

    Raises:
        ValidationError: If task description is invalid
    """
    # Check if provided
    if task_description is None:
        raise ValidationError("Task description cannot be None")

    # Check if empty or whitespace-only
    if not task_description.strip():
        raise ValidationError("Task description cannot be empty")

    # Check minimum length (at least 3 characters)
    MIN_DESCRIPTION_LENGTH = 3
    if len(task_description.strip()) < MIN_DESCRIPTION_LENGTH:
        raise ValidationError(
            f"Task description too short (minimum {MIN_DESCRIPTION_LENGTH} characters)"
        )

    # Check maximum length (prevent abuse)
    MAX_DESCRIPTION_LENGTH = 1000
    if len(task_description) > MAX_DESCRIPTION_LENGTH:
        raise ValidationError(
            f"Task description too long (maximum {MAX_DESCRIPTION_LENGTH} characters)"
        )


def validate_workflow_config(workflow_config: Dict[str, Any]) -> None:
    """
    Validate workflow configuration structure and values.

    Policy 10.2: Defense in Depth - Layer 3: Configuration validation
    Policy 3.6: Error handling - raise specific errors

    Args:
        workflow_config: Workflow configuration dictionary

    Raises:
        ValidationError: If configuration is invalid
    """
    # Check if config exists
    if workflow_config is None:
        raise ValidationError("Workflow config cannot be None")

    # Check required fields
    required_fields = ["fps", "agents", "focus"]
    for field in required_fields:
        if field not in workflow_config:
            raise ValidationError(f"Workflow config missing required field: {field}")

    # Validate FPS range
    fps = workflow_config["fps"]
    MIN_FPS = 0.1
    MAX_FPS = 10.0
    if not isinstance(fps, (int, float)):
        raise ValidationError(f"FPS must be numeric, got: {type(fps).__name__}")
    if fps < MIN_FPS or fps > MAX_FPS:
        raise ValidationError(
            f"FPS must be between {MIN_FPS} and {MAX_FPS}, got: {fps}"
        )

    # Validate agents count
    agents = workflow_config["agents"]
    MIN_AGENTS = 1
    MAX_AGENTS = 20
    if not isinstance(agents, int):
        raise ValidationError(f"Agents must be integer, got: {type(agents).__name__}")
    if agents < MIN_AGENTS or agents > MAX_AGENTS:
        raise ValidationError(
            f"Agents count must be between {MIN_AGENTS} and {MAX_AGENTS}, got: {agents}"
        )

    # Validate focus field
    focus = workflow_config["focus"]
    valid_focus_values = {"shapes", "ui_elements", "generic", "workflow", "code"}
    if not isinstance(focus, str):
        raise ValidationError(f"Focus must be string, got: {type(focus).__name__}")
    if focus not in valid_focus_values:
        raise ValidationError(
            f"Invalid focus value: {focus}. "
            f"Allowed: {', '.join(valid_focus_values)}"
        )


def validate_fps(fps: float) -> None:
    """
    Validate FPS value.

    Policy 10.2: Defense in Depth - Layer 4: Parameter validation
    Policy 3.6: Error handling - raise specific errors

    Args:
        fps: Frames per second value

    Raises:
        ValidationError: If FPS is invalid
    """
    # Check if numeric
    if not isinstance(fps, (int, float)):
        raise ValidationError(f"FPS must be numeric, got: {type(fps).__name__}")

    # Check if positive
    if fps <= 0:
        raise ValidationError(f"FPS must be positive, got: {fps}")

    # Check reasonable range
    MIN_FPS = 0.1
    MAX_FPS = 10.0
    if fps < MIN_FPS or fps > MAX_FPS:
        raise ValidationError(
            f"FPS must be between {MIN_FPS} and {MAX_FPS}, got: {fps}"
        )


def validate_audio_language(language: str) -> None:
    """
    Validate audio language code.

    Policy 10.2: Defense in Depth - Layer 5: Language validation
    Policy 3.6: Error handling - raise specific errors

    Args:
        language: ISO 639-1 language code

    Raises:
        ValidationError: If language code is invalid
    """
    # Check if provided
    if language is None:
        raise ValidationError("Language code cannot be None")

    # Check if empty
    if not language.strip():
        raise ValidationError("Language code cannot be empty")

    # Check length (ISO 639-1 codes are 2 characters)
    LANGUAGE_CODE_LENGTH = 2
    if len(language) != LANGUAGE_CODE_LENGTH:
        raise ValidationError(
            f"Language code must be {LANGUAGE_CODE_LENGTH} characters (ISO 639-1), "
            f"got: {len(language)}"
        )

    # Check if alphabetic
    if not language.isalpha():
        raise ValidationError(f"Language code must be alphabetic, got: {language}")

    # Check if lowercase (standard format)
    if not language.islower():
        raise ValidationError(f"Language code must be lowercase, got: {language}")

    # Validate against common language codes
    supported_languages = {
        "pt", "en", "es", "fr", "de", "it", "ja", "ko", "zh", "ru", "ar", "hi"
    }
    if language not in supported_languages:
        raise ValidationError(
            f"Unsupported language: {language}. "
            f"Supported: {', '.join(sorted(supported_languages))}"
        )
