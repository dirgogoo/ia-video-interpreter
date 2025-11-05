"""
Policies Applied:
- Policy 3.2: DRY - Reuse existing modules
- Policy 3.3: SRP - Orchestrator coordinates, doesn't implement
- Policy 3.5: Meaningful names
- Policy 3.6: Error handling mandatory
- Policy 3.8: Composition over inheritance
- Policy 10.2: Defense in Depth - Validation at every layer

Video analysis orchestrator module.
Coordinates workflow detection, frame extraction, and audio processing.
"""
from pathlib import Path
from typing import Dict, Any

from workflow_loader import load_workflow, detect_workflow_from_keywords
from extract_frames import extract_frames_at_fps
from extract_audio import extract_audio_from_video, transcribe_audio_with_whisper
from agent_coordinator import AgentCoordinator
from validators import (
    validate_video_path,
    validate_task_description,
    validate_workflow_config,
    validate_audio_language
)


class VideoOrchestrator:
    """
    Orchestrates video analysis workflow.

    Policy 3.3: SRP - Delegates to specialized modules
    Policy 3.8: Composition - Uses functions rather than inheritance
    """

    def __init__(self):
        """
        Initialize orchestrator.

        Policy 3.7: No magic numbers - workflow dir is derived
        """
        self.workflows_dir = Path(__file__).parent.parent / "workflows"
        self.agent_coordinator = AgentCoordinator()

    def analyze_video(
        self,
        video_path: Path,
        task_description: str,
        skip_transcription: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze video using appropriate workflow.

        Policy 3.2: DRY - Reuse workflow_loader, extract_frames, extract_audio
        Policy 3.6: Error handling - validate inputs
        Policy 10.2: Defense in Depth - Validate at entry point

        Args:
            video_path: Path to video file
            task_description: User's description of analysis task
            skip_transcription: If True, skip audio extraction/transcription (useful when no API key)

        Returns:
            Dictionary containing:
                - workflow: Name of detected workflow
                - workflow_config: Full workflow configuration
                - frames: List of extracted frame paths
                - audio_path: Path to extracted audio file (None if skipped)
                - transcription: Whisper transcription result (None if skipped)

        Raises:
            ValidationError: If inputs are invalid
            FileNotFoundError: If video file doesn't exist
        """
        # Policy 10.2: Defense in Depth - Layer 1: Validate inputs at entry
        validate_video_path(video_path)
        validate_task_description(task_description)

        # Step 1: Detect appropriate workflow
        workflow_name = detect_workflow_from_keywords(task_description)

        # Step 2: Load workflow configuration
        workflow_path = self.workflows_dir / f"{workflow_name}.yml"
        workflow_config = load_workflow(workflow_path)

        # Policy 10.2: Layer 2: Validate workflow config
        validate_workflow_config(workflow_config["config"])

        # Step 3: Extract frames based on workflow FPS
        fps = workflow_config["config"]["fps"]
        frames_dir = video_path.parent / f"{video_path.stem}_frames"
        frames = extract_frames_at_fps(video_path, frames_dir, fps)

        # Step 4: Extract and transcribe audio (unless skipped)
        audio_path = None
        transcription = None

        if not skip_transcription:
            audio_path = video_path.parent / f"{video_path.stem}_audio.wav"
            audio_path = extract_audio_from_video(video_path, audio_path)

            # Get language from workflow config (default to 'pt')
            language = workflow_config["config"].get("language", "pt")
            # Policy 10.2: Layer 3: Validate language code
            validate_audio_language(language)
            transcription = transcribe_audio_with_whisper(audio_path, language=language)

        # Step 5: Dispatch agents for parallel frame analysis
        agent_results = self.agent_coordinator.dispatch_agents(
            frames=frames,
            transcription=transcription,
            workflow_config=workflow_config["config"],
            user_task=task_description,
            num_agents=workflow_config["config"].get("agents", 5),
            fps=fps
        )

        # Step 6: Aggregate agent results
        agent_analysis = self.agent_coordinator.aggregate_results(
            agent_results=agent_results,
            full_transcription=transcription,
            user_task=task_description
        )

        # Step 7: Return results
        return {
            "workflow": workflow_name,
            "workflow_config": workflow_config["config"],
            "frames": frames,
            "audio_path": audio_path,
            "transcription": transcription,
            "agent_analysis": agent_analysis
        }
