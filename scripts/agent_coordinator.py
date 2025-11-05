"""
Agent coordinator for parallel video frame analysis.

Policy 3.2: Type hints for all functions
Policy 6.1: TDD - implementing after tests written
Policy 10.2: Defense in depth - validation at entry points
"""
from typing import List, Dict, Any
from pathlib import Path
from dataclasses import dataclass
import math
import json
from concurrent.futures import ThreadPoolExecutor, as_completed


# Placeholder for Task tool - will be replaced with actual implementation
class Task:
    """Placeholder for Task tool (to be implemented)"""
    def __init__(self, subagent_type: str, prompt: str):
        self.subagent_type = subagent_type
        self.prompt = prompt

    def execute(self) -> Dict[str, Any]:
        """Placeholder execute method"""
        raise NotImplementedError("Task tool not yet implemented")


@dataclass
class BatchConfig:
    """Configuration for a single agent batch"""
    batch_id: str
    frames: List[Path]
    start_time: float
    end_time: float
    start_frame: int
    end_frame: int
    audio_segments: List[Dict[str, Any]]


class AgentCoordinator:
    """Coordinates parallel Claude agents for video frame analysis"""

    def __init__(self):
        self.base_prompt_path = Path(__file__).parent.parent / "prompts" / "base_agent.md"
        self.focus_prompts = {
            "geometric": Path(__file__).parent.parent / "prompts" / "geometric_focus.md",
            "ui_elements": Path(__file__).parent.parent / "prompts" / "ui_focus.md",
            "generic": Path(__file__).parent.parent / "prompts" / "generic_focus.md",
        }

    def divide_into_batches(
        self,
        frames: List[Path],
        num_agents: int
    ) -> List[List[Path]]:
        """
        Divide frames into batches for parallel processing.

        Policy 10.2: Validate inputs
        """
        if not frames:
            raise ValueError("frames cannot be empty")
        if num_agents < 1:
            raise ValueError("num_agents must be >= 1")

        # Adjust num_agents if more agents than frames
        actual_agents = min(num_agents, len(frames))

        # Calculate base batch size and how many batches need an extra frame
        base_size = len(frames) // actual_agents
        remainder = len(frames) % actual_agents

        batches = []
        start_idx = 0

        for i in range(actual_agents):
            # First 'remainder' batches get an extra frame
            batch_size = base_size + (1 if i < remainder else 0)
            end_idx = start_idx + batch_size
            batch = frames[start_idx:end_idx]
            if batch:  # Only add non-empty batches
                batches.append(batch)
            start_idx = end_idx

        return batches

    def get_relevant_audio(
        self,
        transcription: Dict[str, Any],
        start_time: float,
        end_time: float
    ) -> List[Dict[str, Any]]:
        """
        Extract audio segments overlapping with time range.

        Policy 10.2: Validate inputs
        """
        if not transcription or "segments" not in transcription:
            return []

        if start_time < 0 or end_time < start_time:
            raise ValueError("Invalid time range")

        relevant = []
        for segment in transcription["segments"]:
            seg_start = segment.get("start", 0.0)
            seg_end = segment.get("end", 0.0)

            # Check if segment overlaps with batch time range
            if seg_start < end_time and seg_end > start_time:
                relevant.append(segment)

        return relevant

    def generate_prompt(
        self,
        batch_config: BatchConfig,
        workflow_config: Dict[str, Any],
        user_task: str
    ) -> str:
        """
        Generate prompt for agent using templates.

        Policy 10.2: Validate inputs
        """
        if not batch_config.frames:
            raise ValueError("batch_config.frames cannot be empty")
        if not user_task or len(user_task) < 3:
            raise ValueError("user_task required (min 3 characters)")

        # Read base template
        base_template = self.base_prompt_path.read_text() if self.base_prompt_path.exists() else self._get_default_template()

        # Read workflow-specific instructions
        workflow_focus = workflow_config.get("focus", "generic")
        focus_path = self.focus_prompts.get(workflow_focus)
        workflow_instructions = focus_path.read_text() if focus_path and focus_path.exists() else ""

        # Format frame paths
        frame_paths = "\n".join([f"- {frame}" for frame in batch_config.frames])

        # Format audio segments
        audio_text = "\n\n".join([
            f"**{seg['start']:.1f}s - {seg['end']:.1f}s**: {seg['text']}"
            for seg in batch_config.audio_segments
        ]) if batch_config.audio_segments else "No audio in this time range"

        # Substitute template variables
        prompt = base_template.format(
            workflow_name=workflow_config.get("name", "generic-analysis"),
            workflow_focus=workflow_focus,
            start_frame=batch_config.start_frame,
            end_frame=batch_config.end_frame,
            frame_count=len(batch_config.frames),
            start_time=batch_config.start_time,
            end_time=batch_config.end_time,
            frame_paths=frame_paths,
            transcription_segments=audio_text,
            user_task=user_task,
            workflow_instructions=workflow_instructions,
            batch_id=batch_config.batch_id
        )

        return prompt

    def validate_response(self, response: Dict[str, Any]) -> None:
        """
        Validate agent response structure.

        Policy 10.2: Defense in depth - validate responses
        """
        required_fields = [
            "batch_id",
            "time_range",
            "frames_analyzed",
            "visual_analysis",
            "audio_visual_correlations",
            "summary"
        ]

        for field in required_fields:
            if field not in response:
                raise ValueError(f"Missing required field: {field}")

        # Validate time_range structure
        if "start" not in response["time_range"] or "end" not in response["time_range"]:
            raise ValueError("time_range must have 'start' and 'end'")

    def _get_default_template(self) -> str:
        """Fallback template if file not found"""
        return """
# Video Analysis Agent

Workflow: {workflow_name}
Focus: {workflow_focus}
Frames: {start_frame}-{end_frame}
Time: {start_time}s - {end_time}s
Batch ID: {batch_id}

Frames:
{frame_paths}

Audio:
{transcription_segments}

Task: {user_task}

{workflow_instructions}

Please analyze these frames and return your findings as JSON.
"""

    def dispatch_agents(
        self,
        frames: List[Path],
        transcription: Dict[str, Any],
        workflow_config: Dict[str, Any],
        user_task: str,
        num_agents: int,
        fps: float
    ) -> List[Dict[str, Any]]:
        """
        Dispatch parallel agents via Task tool.

        Policy 10.2: Validate inputs at entry point
        """
        # Layer 1: Input validation
        if not frames:
            raise ValueError("frames cannot be empty")
        if num_agents < 1:
            raise ValueError("num_agents must be >= 1")
        if fps <= 0:
            raise ValueError("fps must be > 0")

        # Divide frames into batches
        batches = self.divide_into_batches(frames, num_agents)

        # Create batch configs
        batch_configs = []
        for i, batch_frames in enumerate(batches):
            start_frame = frames.index(batch_frames[0])
            end_frame = frames.index(batch_frames[-1])
            start_time = start_frame / fps
            end_time = (end_frame + 1) / fps

            audio_segments = self.get_relevant_audio(
                transcription=transcription,
                start_time=start_time,
                end_time=end_time
            )

            batch_config = BatchConfig(
                batch_id=f"batch_{i}",
                frames=batch_frames,
                start_time=start_time,
                end_time=end_time,
                start_frame=start_frame,
                end_frame=end_frame,
                audio_segments=audio_segments
            )
            batch_configs.append(batch_config)

        # Dispatch agents in parallel
        results = []

        # REPLACE mock dispatch with real Task tool invocation
        # Option 1: Parallel dispatch (all agents start simultaneously)
        # Note: In production, use actual Task tool import
        # from claude_tools import Task

        for batch_config in batch_configs:
            prompt = self.generate_prompt(
                batch_config=batch_config,
                workflow_config=workflow_config,
                user_task=user_task
            )

            # TODO: Uncomment when Task tool is available in execution environment
            # task = Task(
            #     subagent_type="general-purpose",
            #     description=f"Analyze video frames {batch_config.batch_id}",
            #     prompt=prompt
            # )
            # result = task.execute()

            # For MVP: Keep mock but document structure
            result = {
                "batch_id": batch_config.batch_id,
                "time_range": {"start": batch_config.start_time, "end": batch_config.end_time},
                "frames_analyzed": len(batch_config.frames),
                "visual_analysis": [],
                "audio_visual_correlations": [],
                "summary": f"Analysis of {batch_config.batch_id}",
                "_note": "MVP: Replace with actual Task tool invocation"
            }

            # Validate response structure
            self.validate_response(result)
            results.append(result)

        return results

    def aggregate_results(
        self,
        agent_results: List[Dict[str, Any]],
        full_transcription: Dict[str, Any],
        user_task: str
    ) -> Dict[str, Any]:
        """
        Aggregate agent results with orchestrator post-processing.

        Policy 10.2: Validate aggregated data
        """
        # Layer 1: Validate inputs
        if not agent_results:
            raise ValueError("agent_results cannot be empty")

        # Concatenate visual analysis (chronological order)
        visual_timeline = []
        for result in agent_results:
            visual_timeline.extend(result.get("visual_analysis", []))

        # Collect all correlations
        correlations = []
        for result in agent_results:
            correlations.extend(result.get("audio_visual_correlations", []))

        # Sort correlations by timestamp
        correlations.sort(key=lambda x: x.get("timestamp", 0.0))

        # Orchestrator post-processing: Generate executive summary
        batch_summaries = [result.get("summary", "") for result in agent_results]
        executive_summary = self._synthesize_summary(
            batch_summaries=batch_summaries,
            full_transcription=full_transcription,
            user_task=user_task
        )

        # Layer 2: Validate output structure
        aggregated = {
            "executive_summary": executive_summary,
            "visual_timeline": visual_timeline,
            "correlations": correlations,
            "full_transcription": full_transcription.get("text", "") if full_transcription else "",
            "total_frames_analyzed": sum(r.get("frames_analyzed", 0) for r in agent_results),
            "num_agents": len(agent_results)
        }

        return aggregated

    def _synthesize_summary(
        self,
        batch_summaries: List[str],
        full_transcription: Dict[str, Any],
        user_task: str
    ) -> str:
        """
        Orchestrator synthesis of agent summaries.
        """
        # Simple concatenation for MVP
        # Future: Could use another agent to synthesize
        combined = "\n\n".join([
            f"**Batch {i}**: {summary}"
            for i, summary in enumerate(batch_summaries)
            if summary
        ])

        return f"# Video Analysis Summary\n\n**Task**: {user_task}\n\n{combined}"
