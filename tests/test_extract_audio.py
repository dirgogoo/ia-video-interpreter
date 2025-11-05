"""
Policies Applied:
- Policy 6.1: Unit test coverage for business logic
- Policy 6.5: Test naming convention (should/when pattern)
- Policy 6.6: AAA Pattern (Arrange-Act-Assert)
- Policy 11.6: Memory-First Pattern (Whisper integration documented in memory)

Tests for audio extraction and Whisper transcription.
"""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from extract_audio import extract_audio_from_video, transcribe_audio_with_whisper


def test_extract_audio_from_video():
    """Should extract audio track from video file"""
    # Arrange
    video_path = Path("tests/fixtures/sample_10s_with_audio.mp4")
    output_path = Path("tests/temp/audio.mp3")

    # Act
    result = extract_audio_from_video(video_path, output_path)

    # Assert
    assert result.exists()
    assert result.suffix == ".mp3"
    assert result == output_path


def test_extract_audio_creates_output_dir():
    """Should create output directory if it doesn't exist"""
    # Arrange
    video_path = Path("tests/fixtures/sample_10s_with_audio.mp4")
    output_path = Path("tests/temp/audio_new/extracted.mp3")

    # Act
    result = extract_audio_from_video(video_path, output_path)

    # Assert
    assert output_path.parent.exists()
    assert result.exists()


def test_extract_audio_handles_missing_video():
    """Should raise error when video file doesn't exist"""
    # Arrange
    video_path = Path("nonexistent.mp4")
    output_path = Path("tests/temp/audio.mp3")

    # Act & Assert
    with pytest.raises(FileNotFoundError):
        extract_audio_from_video(video_path, output_path)


@pytest.mark.skip(reason="Requires OpenAI API key and network access")
def test_transcribe_audio_with_whisper():
    """Should transcribe audio using Whisper API with timestamps"""
    # Arrange
    audio_path = Path("tests/temp/audio.mp3")

    # Act
    transcript = transcribe_audio_with_whisper(
        audio_path,
        language="pt",
        granularity="segment"
    )

    # Assert
    assert "text" in transcript
    assert "segments" in transcript
    assert len(transcript["segments"]) > 0
    assert "start" in transcript["segments"][0]
    assert "end" in transcript["segments"][0]
    assert "text" in transcript["segments"][0]
