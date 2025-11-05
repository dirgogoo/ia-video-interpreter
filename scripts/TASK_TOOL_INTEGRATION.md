# Task Tool Integration Guide

## Current Status (MVP)

The agent coordinator is designed to use Claude's Task tool for parallel agent dispatch, but currently uses mock responses for testing.

## How to Enable Real Task Tool

When Task tool is available in the execution environment:

1. **Import Task tool**:
```python
from claude_tools import Task  # Or whatever the actual import path is
```

2. **Replace mock in dispatch_agents method** (line ~150 in agent_coordinator.py):

```python
# Replace this:
result = {
    "batch_id": batch_config.batch_id,
    # ... mock structure
}

# With this:
task = Task(
    subagent_type="general-purpose",
    description=f"Analyze video frames {batch_config.batch_id}",
    prompt=prompt,
    model="sonnet"  # Or "haiku" for faster, cheaper analysis
)
result_text = task.execute()

# Parse JSON response from agent
result = json.loads(result_text)
```

3. **Handle parse errors**:
```python
try:
    result = json.loads(result_text)
    self.validate_response(result)
except json.JSONDecodeError as e:
    # Agent didn't return valid JSON - retry or log error
    print(f"Agent {batch_config.batch_id} returned invalid JSON: {e}")
    result = self._create_fallback_response(batch_config)
```

4. **Test with real video**:
```bash
cd .claude/skills/video-interpreter
python -c "
from pathlib import Path
from scripts.orchestrator import VideoOrchestrator

video = Path('tests/fixtures/sample_10s.mp4')
orchestrator = VideoOrchestrator()
result = orchestrator.analyze_video(video, 'Describe this video')

print('Agent Analysis:')
print(result['agent_analysis']['executive_summary'])
"
```

## Expected Task Tool Interface

Based on Claude Code documentation, the Task tool should support:

```python
Task(
    subagent_type="general-purpose",  # or "Explore", "Plan", etc.
    description="Short description of task",
    prompt="Full prompt with instructions and data",
    model="sonnet" | "haiku" | "opus"  # optional
)
```

The Task tool returns a string response (the agent's output).
