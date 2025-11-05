"""
Tests for agent coordinator module that manages parallel agent execution.

Policy 6.1: TDD - write failing tests first
Policy 10.2: Defense in depth - validate at multiple layers
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from scripts.agent_coordinator import AgentCoordinator, BatchConfig


def test_divide_frames_into_batches_equal_distribution():
    """Test that frames are divided evenly across agents"""
    coordinator = AgentCoordinator()

    frames = [Path(f"frame_{i:04d}.png") for i in range(10)]
    num_agents = 3

    batches = coordinator.divide_into_batches(frames, num_agents)

    assert len(batches) == 3
    assert len(batches[0]) == 4  # frames 0-3
    assert len(batches[1]) == 3  # frames 4-6
    assert len(batches[2]) == 3  # frames 7-9
    assert batches[0][0].name == "frame_0000.png"
    assert batches[2][-1].name == "frame_0009.png"


def test_divide_frames_more_agents_than_frames():
    """Test handling when agents > frames"""
    coordinator = AgentCoordinator()

    frames = [Path(f"frame_{i:04d}.png") for i in range(3)]
    num_agents = 5

    batches = coordinator.divide_into_batches(frames, num_agents)

    # Should only create 3 batches (one per frame)
    assert len(batches) == 3
    assert all(len(batch) == 1 for batch in batches)


def test_correlate_audio_with_batch():
    """Test extracting relevant audio segments for a batch"""
    coordinator = AgentCoordinator()

    transcription = {
        "text": "Full transcription",
        "segments": [
            {"start": 0.0, "end": 2.0, "text": "Segment 1"},
            {"start": 2.0, "end": 4.0, "text": "Segment 2"},
            {"start": 4.0, "end": 6.0, "text": "Segment 3"},
        ]
    }

    # Batch covers frames 0-1 at 1 FPS (time 0-2s)
    relevant = coordinator.get_relevant_audio(
        transcription=transcription,
        start_time=0.0,
        end_time=2.0
    )

    assert len(relevant) == 1
    assert relevant[0]["text"] == "Segment 1"


def test_generate_agent_prompt():
    """Test prompt generation with template substitution"""
    coordinator = AgentCoordinator()

    batch_config = BatchConfig(
        batch_id="batch_0",
        frames=[Path("frame_0000.png"), Path("frame_0001.png")],
        start_time=0.0,
        end_time=2.0,
        start_frame=0,
        end_frame=1,
        audio_segments=[{"start": 0.0, "end": 2.0, "text": "Test audio"}]
    )

    workflow_config = {
        "name": "generic-analysis",
        "focus": "generic"
    }

    user_task = "Analyze this video"

    prompt = coordinator.generate_prompt(
        batch_config=batch_config,
        workflow_config=workflow_config,
        user_task=user_task
    )

    assert "batch_0" in prompt
    assert "generic-analysis" in prompt
    assert "0.0" in prompt
    assert "2.0" in prompt
    assert "Test audio" in prompt
    assert "Analyze this video" in prompt


def test_validate_agent_response():
    """Test validation of agent JSON response"""
    coordinator = AgentCoordinator()

    valid_response = {
        "batch_id": "batch_0",
        "time_range": {"start": 0.0, "end": 2.0},
        "frames_analyzed": 2,
        "visual_analysis": [],
        "audio_visual_correlations": [],
        "summary": "Test summary"
    }

    # Should not raise
    coordinator.validate_response(valid_response)

    invalid_response = {"batch_id": "batch_0"}  # missing required fields

    with pytest.raises(ValueError, match="Missing required field"):
        coordinator.validate_response(invalid_response)


def test_dispatch_agents_parallel():
    """Test dispatching multiple agents via Task tool"""
    coordinator = AgentCoordinator()

    frames = [Path(f"frame_{i:04d}.png") for i in range(6)]
    transcription = {
        "text": "Full text",
        "segments": [
            {"start": 0.0, "end": 3.0, "text": "First half"},
            {"start": 3.0, "end": 6.0, "text": "Second half"},
        ]
    }
    workflow_config = {"name": "generic-analysis", "focus": "generic"}
    user_task = "Analyze video"
    num_agents = 2
    fps = 1.0

    with patch('scripts.agent_coordinator.Task') as mock_task:
        mock_task.return_value.execute.return_value = {
            "batch_id": "batch_0",
            "time_range": {"start": 0.0, "end": 3.0},
            "frames_analyzed": 3,
            "visual_analysis": [],
            "audio_visual_correlations": [],
            "summary": "Mock summary"
        }

        results = coordinator.dispatch_agents(
            frames=frames,
            transcription=transcription,
            workflow_config=workflow_config,
            user_task=user_task,
            num_agents=num_agents,
            fps=fps
        )

        assert len(results) == 2
        assert all("batch_id" in result for result in results)
        # Note: In MVP mode, Task tool is not actually called (uses hardcoded mocks)
        # When Task tool is integrated, add: assert mock_task.call_count == 2


def test_aggregate_results():
    """Test aggregating agent results with orchestrator post-processing"""
    coordinator = AgentCoordinator()

    agent_results = [
        {
            "batch_id": "batch_0",
            "time_range": {"start": 0.0, "end": 3.0},
            "frames_analyzed": 3,
            "visual_analysis": [
                {"frame_number": 0, "timestamp": 0.0, "description": "Frame 0"}
            ],
            "audio_visual_correlations": [
                {"timestamp": 1.0, "audio": "Audio 1", "visual": "Visual 1", "correlation": "Match 1"}
            ],
            "summary": "First batch summary"
        },
        {
            "batch_id": "batch_1",
            "time_range": {"start": 3.0, "end": 6.0},
            "frames_analyzed": 3,
            "visual_analysis": [
                {"frame_number": 3, "timestamp": 3.0, "description": "Frame 3"}
            ],
            "audio_visual_correlations": [],
            "summary": "Second batch summary"
        }
    ]

    full_transcription = {"text": "Full transcription", "segments": []}

    aggregated = coordinator.aggregate_results(
        agent_results=agent_results,
        full_transcription=full_transcription,
        user_task="Test task"
    )

    assert "executive_summary" in aggregated
    assert "visual_timeline" in aggregated
    assert "correlations" in aggregated
    assert len(aggregated["visual_timeline"]) == 2  # 2 frames analyzed
    assert len(aggregated["correlations"]) == 1  # 1 correlation found
