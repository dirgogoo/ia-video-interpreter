# Agent Coordination System

This document explains how the video-interpreter skill uses parallel Claude agents to analyze video content.

## Architecture Overview

```
Video File
   ↓
Orchestrator (scripts/orchestrator.py)
   ↓
Frame Extraction (OpenCV) + Audio Extraction (moviepy) + Transcription (Whisper)
   ↓
Agent Coordinator (scripts/agent_coordinator.py)
   ├─→ Agent 1: Frames 0-N
   ├─→ Agent 2: Frames N-2N
   ├─→ Agent 3: Frames 2N-3N
   └─→ Agent N: Frames ...
   ↓
Result Aggregation + Post-Processing
   ↓
Final Report
```

## Components

### 1. Agent Coordinator (`scripts/agent_coordinator.py`)

**Responsibilities:**
- Divide frames into batches
- Generate specialized prompts
- Dispatch agents via Task tool
- Validate agent responses
- Aggregate results

**Key Methods:**
- `divide_into_batches()`: Split frames evenly across N agents
- `get_relevant_audio()`: Extract audio segments for time range
- `generate_prompt()`: Create agent-specific prompt from templates
- `dispatch_agents()`: Launch parallel agents via Task tool
- `aggregate_results()`: Combine agent outputs with orchestrator synthesis

### 2. Prompt Templates (`prompts/*.md`)

**Base Template** (`prompts/base_agent.md`):
- Generic structure for all agents
- Includes frame paths, audio segments, user task
- Defines expected JSON output format

**Workflow-Specific** (`prompts/{geometric|ui|generic}_focus.md`):
- Specialized instructions based on workflow
- Focus areas for analysis
- Audio priority level (HIGH/MEDIUM)

### 3. Orchestrator Integration (`scripts/orchestrator.py`)

The orchestrator calls agent coordination after extracting frames and audio:

```python
# After frame/audio extraction:
agent_results = self.agent_coordinator.dispatch_agents(
    frames=frames,
    transcription=transcription,
    workflow_config=workflow,
    user_task=task_description,
    num_agents=workflow.get("agents", 5),
    fps=fps
)

agent_analysis = self.agent_coordinator.aggregate_results(
    agent_results=agent_results,
    full_transcription=transcription,
    user_task=task_description
)
```

## Workflow-Specific Behavior

### Geometric Reconstruction
- **Agents**: 5
- **FPS**: 0.5 (slow, detailed capture)
- **Focus**: Shapes, measurements, dimensions, spatial relationships
- **Audio Priority**: HIGH (measurements often spoken)

### UI Replication
- **Agents**: 10
- **FPS**: 2.0 (fast, capture UI changes)
- **Focus**: Buttons, forms, layouts, colors, typography
- **Audio Priority**: MEDIUM (narrator guides interactions)

### Generic Analysis
- **Agents**: 5
- **FPS**: 1.0 (balanced)
- **Focus**: Main subject, actions, context
- **Audio Priority**: MEDIUM (balanced audio-visual)

## Agent Output Format

Each agent returns JSON:

```json
{
  "batch_id": "batch_0",
  "time_range": {"start": 0.0, "end": 5.0},
  "frames_analyzed": 5,
  "visual_analysis": [
    {
      "frame_number": 0,
      "timestamp": 0.0,
      "description": "...",
      "key_objects": ["..."],
      "text_detected": "...",
      "notable_changes": "..."
    }
  ],
  "audio_visual_correlations": [
    {
      "timestamp": 2.5,
      "audio": "what was said",
      "visual": "what was shown",
      "correlation": "how they relate"
    }
  ],
  "summary": "Batch summary"
}
```

## Aggregated Result Format

Orchestrator produces:

```json
{
  "executive_summary": "Overall video summary",
  "visual_timeline": [/* all frame analyses */],
  "correlations": [/* all audio-visual matches */],
  "full_transcription": "Complete audio text",
  "total_frames_analyzed": 30,
  "num_agents": 5
}
```

## Performance Characteristics

- **Parallelization**: All agents run simultaneously (O(n/k) where k = num_agents)
- **Cost**: Each agent is a separate API call (cost scales with num_agents)
- **Latency**: Dominated by slowest agent batch

**Example** (30-second video, 1 FPS, 5 agents):
- Frames: 30
- Frames per agent: 6
- Analysis time: ~same as analyzing 6 frames (vs 30 frames sequential)
- Cost: 5x agent API calls

## Testing

**Unit Tests** (`tests/test_agent_coordinator.py`):
- Batch division logic
- Audio correlation
- Prompt generation
- Response validation
- Aggregation logic

**Integration Tests** (`tests/integration/test_full_pipeline_with_agents.py`):
- End-to-end pipeline with real video
- Requires OPENAI_API_KEY for Whisper
- Verifies all components work together

**Run Tests**:
```bash
# Unit tests (no API key required)
python -m pytest tests/test_agent_coordinator.py -v

# Integration test (requires API key)
OPENAI_API_KEY="sk-..." python -m pytest tests/integration/ -v
```

## Current Status

✅ **Implemented**: Agent coordinator, prompts, orchestrator integration, tests

🚧 **Mock Mode**: Currently uses mock agent responses (for development without Task tool)

📝 **Production Ready**: Update `dispatch_agents()` to use Task tool import (see `scripts/TASK_TOOL_INTEGRATION.md`)

## Future Enhancements

1. **Dynamic Agent Count**: Adjust num_agents based on video length
2. **Smart Batching**: Group by scene changes instead of equal division
3. **Agent Specialization**: Different agent types per batch (e.g., OCR agent for text-heavy frames)
4. **Cost Optimization**: Use haiku model for simple batches, sonnet for complex
5. **Retry Logic**: Retry failed agents with adjusted prompts
