"""
Policies Applied:
- Policy 6.1: Unit test coverage for business logic
- Policy 6.5: Test naming convention (should/when pattern)
- Policy 6.6: AAA Pattern (Arrange-Act-Assert)
- Policy 6.7: Test isolation

Tests for video analysis orchestrator.
"""
import pytest
from pathlib import Path
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from orchestrator import VideoOrchestrator
from validators import ValidationError

# Get absolute path to test resources
TEST_DIR = Path(__file__).parent.parent
TEST_RESOURCES = TEST_DIR / "tests" / "resources"


# Mock Whisper transcription for all tests
@pytest.fixture(autouse=True)
def mock_whisper():
    """Mock Whisper API for all orchestrator tests"""
    with patch('orchestrator.transcribe_audio_with_whisper') as mock:
        mock.return_value = {
            "text": "Mock transcription text",
            "segments": [
                {"start": 0.0, "end": 1.0, "text": "Mock segment"}
            ]
        }
        yield mock


def test_orchestrator_basic_workflow():
    """Should orchestrate frame extraction, audio extraction, and workflow loading"""
    # Arrange
    TEST_RESOURCES.mkdir(parents=True, exist_ok=True)
    video_path = Path(__file__).parent / "fixtures" / "sample_10s_with_audio.mp4"

    task_description = "analyze geometric shapes with measurements"

    with patch('orchestrator.AgentCoordinator'):
        orchestrator = VideoOrchestrator()

        # Act
        result = orchestrator.analyze_video(video_path, task_description)

        # Assert
        assert result is not None
        assert "workflow" in result
        assert result["workflow"] == "geometric-reconstruction"
        assert "frames" in result
        assert isinstance(result["frames"], list)
        assert len(result["frames"]) > 0
        assert "audio_path" in result
        assert "transcription" in result
        assert "agent_analysis" in result


def test_orchestrator_detects_ui_workflow():
    """Should detect UI replication workflow from task description"""
    # Arrange
    TEST_RESOURCES.mkdir(parents=True, exist_ok=True)
    video_path = Path(__file__).parent / "fixtures" / "sample_10s_with_audio.mp4"

    task_description = "replicate the user interface from this video"

    with patch('orchestrator.AgentCoordinator'):
        orchestrator = VideoOrchestrator()

        # Act
        result = orchestrator.analyze_video(video_path, task_description)

        # Assert
        assert result["workflow"] == "ui-replication"


def test_orchestrator_fallback_to_generic():
    """Should fallback to generic workflow when no keywords match"""
    # Arrange
    TEST_RESOURCES.mkdir(parents=True, exist_ok=True)
    video_path = Path(__file__).parent / "fixtures" / "sample_10s_with_audio.mp4"

    task_description = "summarize this video"

    with patch('orchestrator.AgentCoordinator'):
        orchestrator = VideoOrchestrator()

        # Act
        result = orchestrator.analyze_video(video_path, task_description)

        # Assert
        assert result["workflow"] == "generic-analysis"


def test_orchestrator_missing_video_file():
    """Should raise error when video file doesn't exist"""
    # Arrange
    video_path = Path("nonexistent_video.mp4")
    task_description = "analyze this video"

    with patch('orchestrator.AgentCoordinator'):
        orchestrator = VideoOrchestrator()

        # Act & Assert (ValidationError after defense-in-depth integration)
        with pytest.raises(ValidationError, match="Video file not found"):
            orchestrator.analyze_video(video_path, task_description)


def test_orchestrator_respects_workflow_fps():
    """Should use FPS from detected workflow configuration"""
    # Arrange
    TEST_RESOURCES.mkdir(parents=True, exist_ok=True)
    video_path = Path(__file__).parent / "fixtures" / "sample_10s_with_audio.mp4"

    # Test with geometric workflow (0.5 fps)
    task_description = "analyze geometric shapes"

    with patch('orchestrator.AgentCoordinator'):
        orchestrator = VideoOrchestrator()

        # Act
        result = orchestrator.analyze_video(video_path, task_description)

        # Assert
        assert result["workflow"] == "geometric-reconstruction"
        assert "workflow_config" in result
        assert result["workflow_config"]["fps"] == 0.5


def test_orchestrator_uses_agent_coordinator():
    """Should call agent coordinator after frame extraction"""
    # Arrange
    from unittest.mock import Mock

    TEST_RESOURCES.mkdir(parents=True, exist_ok=True)
    # Use the real sample video with audio
    video_path = Path(__file__).parent / "fixtures" / "sample_10s_with_audio.mp4"

    # Mock the agent coordinator BEFORE instantiating orchestrator
    with patch('orchestrator.AgentCoordinator') as mock_coordinator_class:
        mock_coordinator = Mock()
        mock_coordinator.dispatch_agents.return_value = [
            {
                "batch_id": "batch_0",
                "time_range": {"start": 0.0, "end": 3.0},
                "frames_analyzed": 3,
                "visual_analysis": [{"frame_number": 0, "description": "Test"}],
                "audio_visual_correlations": [],
                "summary": "Test summary"
            }
        ]
        mock_coordinator.aggregate_results.return_value = {
            "executive_summary": "Test executive summary",
            "visual_timeline": [],
            "correlations": [],
            "full_transcription": "",
            "total_frames_analyzed": 3,
            "num_agents": 1
        }
        mock_coordinator_class.return_value = mock_coordinator

        # Now instantiate orchestrator (with mocked AgentCoordinator)
        orchestrator = VideoOrchestrator()

        # Act
        result = orchestrator.analyze_video(video_path, "analyze geometric shapes")

        # Assert
        assert mock_coordinator.dispatch_agents.called
        assert mock_coordinator.aggregate_results.called
        assert "agent_analysis" in result
        assert result["agent_analysis"]["total_frames_analyzed"] == 3
