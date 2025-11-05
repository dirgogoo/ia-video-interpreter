# Video-Interpreter Skill

🎬 AI Video Interpreter - Adaptive video analysis framework with parallel Claude agents

  Analyze videos through specialized workflows (UI replication, geometric reconstruction, workflow documentation) using 5-10 parallel Claude agents
  coordinated with audio transcription.

  Features:
  • 🤖 Parallel agent coordination via Claude Task tool
  • 🎯 Adaptive FPS extraction based on workflow intent (0.5-2 fps)
  • 🎤 Whisper API integration for audio-visual correlation
  • 📊 3 specialized workflows: geometric, UI, generic analysis
  • ✅ 59/61 tests passing (96.7%) with TDD approach
  • 🛡️ Defense-in-depth validation (5 layers)
  • 📖 Complete documentation and integration guides

  Hybrid architecture: Python handles frame/audio extraction, Claude coordinates intelligent analysis across multiple agents with timestamp
  synchronization.

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
