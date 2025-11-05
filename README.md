# Video-Interpreter Skill

Adaptive video analysis framework with specialized workflows.

## Workflows

- `geometric-reconstruction.yml` - Analyze shapes with audio measurements
- `ui-replication.yml` - Replicate user interfaces
- `generic-analysis.yml` - General video analysis

## Usage

```
/video-interpreter <video.mp4> <task description>
```

## Configuration

Each workflow defines:
- FPS (adaptive frame extraction rate)
- Agents (parallel processing count)
- Focus areas (specialized prompts)
- Audio priority (high/medium/low)

## Installation

```bash
cd .claude/skills/video-interpreter
pip install -r requirements.txt
```

Requires:
- Python 3.10+
- FFmpeg (system-level installation)
- OpenAI API key in environment

## Examples

```bash
# Geometric reconstruction
/video-interpreter geometry.mp4 "reconstruct 3D model with audio measurements"

# UI replication
/video-interpreter tutorial.mp4 "replicate the login form shown"

# Generic analysis
/video-interpreter demo.mp4 "summarize the key points"
```
