# Example: Geometric Reconstruction End-to-End

This document shows a complete example of processing a video to generate Semantic Geometry JSON.

---

## Input Video

**File**: `hollow_cylinder_tutorial.mp4`
**Duration**: 25 seconds
**Content**: Someone showing and measuring a hollow cylinder part

**Audio Transcript**:
```
0.0s: "Olá, hoje vou mostrar como medir esta peça"
2.5s: "Esta é uma peça cilíndrica oca"
5.2s: "O diâmetro externo é 50 milímetros"
8.7s: "O diâmetro interno é 30 milímetros"
12.3s: "E a altura total é 10 centímetros"
15.8s: "Vamos ver de perto os detalhes"
20.1s: "Como podem ver, é um cilindro simples"
```

**Visual Content**:
- Frames 0-10: Person holding the part
- Frames 10-15: Close-up of the cylinder (circular shape visible)
- Frames 15-20: Side view showing height
- Frames 20-25: Rotating the part

---

## Processing Steps

### Step 1: Orchestrator Execution

```python
from pathlib import Path
from scripts.orchestrator import VideoOrchestrator

orchestrator = VideoOrchestrator()
video_path = Path("tests/fixtures/hollow_cylinder_tutorial.mp4")

result = orchestrator.analyze_video(
    video_path=video_path,
    task_description="Analisar geometria da peça e extrair medidas"
)
```

**Output**:
```python
{
    'workflow': 'geometric-reconstruction',
    'workflow_config': {
        'fps': 0.5,
        'agents': 5,
        'focus': 'shapes',
        'audio_priority': 'high'
    },
    'frames': [
        'temp/frame_0000.png',
        'temp/frame_0001.png',
        # ... 25 frames total (0.5 fps × 25 seconds)
    ],
    'audio_path': 'temp/audio.wav',
    'transcription': {
        'text': 'Olá, hoje vou mostrar...',
        'segments': [
            {'start': 0.0, 'end': 2.5, 'text': 'Olá, hoje vou mostrar como medir esta peça'},
            {'start': 2.5, 'end': 5.2, 'text': 'Esta é uma peça cilíndrica oca'},
            {'start': 5.2, 'end': 8.7, 'text': 'O diâmetro externo é 50 milímetros'},
            {'start': 8.7, 'end': 12.3, 'text': 'O diâmetro interno é 30 milímetros'},
            {'start': 12.3, 'end': 15.8, 'text': 'E a altura total é 10 centímetros'},
            # ...
        ]
    }
}
```

### Step 2: Agent Coordination

Frames divided into 5 batches (5 agents):
- **Batch 0**: Frames 0-4 (0.0s - 5.0s)
- **Batch 1**: Frames 5-9 (5.0s - 10.0s)
- **Batch 2**: Frames 10-14 (10.0s - 15.0s)
- **Batch 3**: Frames 15-19 (15.0s - 20.0s)
- **Batch 4**: Frames 20-24 (20.0s - 25.0s)

### Step 3: Agent 0 Analysis (Batch 0: 0-5s)

**Frames**: 0-4
**Audio**: "Olá, hoje vou mostrar...", "Esta é uma peça cilíndrica oca"
**Visual**: Person holding part, cylindrical shape visible

**Agent 0 Output**:
```json
{
  "batch_id": "batch_0",
  "time_range": {"start": 0.0, "end": 5.0},
  "frames_analyzed": 5,
  "semantic_geometry": {
    "features": []
  },
  "audio_visual_correlations": [
    {
      "timestamp": 2.5,
      "audio": "Esta é uma peça cilíndrica oca",
      "visual": "Cylindrical shape visible in frames 3-4",
      "correlation": "Audio describes hollow cylinder, visual confirms cylindrical geometry"
    }
  ],
  "summary": "Identified cylindrical geometry, no measurements yet in this time range"
}
```

### Step 4: Agent 1 Analysis (Batch 1: 5-10s)

**Frames**: 5-9
**Audio**: "O diâmetro externo é 50 milímetros", "O diâmetro interno é 30 milímetros"
**Visual**: Close-up of circular cross-section

**Agent 1 Output**:
```json
{
  "batch_id": "batch_1",
  "time_range": {"start": 5.0, "end": 10.0},
  "frames_analyzed": 5,
  "semantic_geometry": {
    "features": [
      {
        "id": "feature_1",
        "type": "Extrude",
        "sketch": {
          "plane": {"type": "work_plane"},
          "geometry": [
            {
              "type": "Circle",
              "center": {"x": 0, "y": 0},
              "diameter": {
                "value": 50,
                "unit": "mm",
                "source": "audio",
                "timestamp": 5.2
              }
            }
          ]
        },
        "parameters": {
          "distance": {
            "value": 100,
            "unit": "mm",
            "source": "inferred",
            "note": "Height mentioned later, will be updated"
          },
          "direction": "normal",
          "operation": "new_body"
        },
        "detection": {
          "visual_confidence": 0.95,
          "audio_correlation": "strong",
          "frame_number": 7
        }
      },
      {
        "id": "feature_2",
        "type": "Cut",
        "sketch": {
          "plane": {"type": "work_plane"},
          "geometry": [
            {
              "type": "Circle",
              "center": {"x": 0, "y": 0},
              "diameter": {
                "value": 30,
                "unit": "mm",
                "source": "audio",
                "timestamp": 8.7
              }
            }
          ]
        },
        "parameters": {
          "distance": {
            "value": 100,
            "unit": "mm",
            "source": "inferred"
          },
          "direction": "normal",
          "cut_type": "through_all"
        },
        "detection": {
          "visual_confidence": 0.90,
          "audio_correlation": "strong",
          "frame_number": 9
        }
      }
    ]
  },
  "audio_visual_correlations": [
    {
      "timestamp": 5.2,
      "audio": "O diâmetro externo é 50 milímetros",
      "visual": "Circular cross-section visible in frame 7",
      "correlation": "Outer diameter measurement matches visual circle geometry"
    },
    {
      "timestamp": 8.7,
      "audio": "O diâmetro interno é 30 milímetros",
      "visual": "Inner hole visible in frame 9",
      "correlation": "Inner diameter measurement identifies cut operation"
    }
  ],
  "summary": "Detected hollow cylinder: outer Ø50mm, inner Ø30mm. Height pending."
}
```

### Step 5: Agent 2 Analysis (Batch 2: 10-15s)

**Frames**: 10-14
**Audio**: "E a altura total é 10 centímetros"
**Visual**: Side view showing cylinder height

**Agent 2 Output**:
```json
{
  "batch_id": "batch_2",
  "time_range": {"start": 10.0, "end": 15.0},
  "frames_analyzed": 5,
  "semantic_geometry": {
    "features": [
      {
        "id": "feature_1_update",
        "type": "Extrude",
        "sketch": {
          "plane": {"type": "work_plane"},
          "geometry": [
            {
              "type": "Circle",
              "center": {"x": 0, "y": 0},
              "diameter": {
                "value": 50,
                "unit": "mm",
                "source": "audio",
                "timestamp": 5.2
              }
            }
          ]
        },
        "parameters": {
          "distance": {
            "value": 100,
            "unit": "mm",
            "source": "audio",
            "timestamp": 12.3
          },
          "direction": "normal",
          "operation": "new_body"
        },
        "detection": {
          "visual_confidence": 0.98,
          "audio_correlation": "strong",
          "frame_number": 12
        }
      }
    ]
  },
  "audio_visual_correlations": [
    {
      "timestamp": 12.3,
      "audio": "E a altura total é 10 centímetros",
      "visual": "Side view in frame 12 shows cylinder height",
      "correlation": "Height measurement (100mm) confirmed by visual side view"
    }
  ],
  "summary": "Height measurement obtained: 100mm (10cm). Updated extrude distance."
}
```

### Step 6: Agents 3-4 Analysis

**Batches 3-4**: No new features detected, just rotating views

**Output**: No new features, confirmation of existing geometry

---

## Step 7: Aggregation

```python
from scripts.agent_coordinator import AgentCoordinator

coordinator = AgentCoordinator()

# All agent results
agent_results = [batch_0_result, batch_1_result, batch_2_result, batch_3_result, batch_4_result]

# Aggregate
aggregated = coordinator.aggregate_results(
    agent_results=agent_results,
    full_transcription=result['transcription'],
    user_task="Analisar geometria da peça e extrair medidas"
)
```

**Aggregated Output**:
```json
{
  "part_name": "Hollow Cylinder",
  "work_plane": {"type": "primitive", "face": "frontal"},
  "features": [
    {
      "id": "feature_1",
      "type": "Extrude",
      "sketch": {
        "plane": {"type": "work_plane"},
        "geometry": [
          {
            "type": "Circle",
            "center": {"x": 0, "y": 0},
            "diameter": {"value": 50, "unit": "mm", "source": "audio", "timestamp": 5.2}
          }
        ]
      },
      "parameters": {
        "distance": {"value": 100, "unit": "mm", "source": "audio", "timestamp": 12.3},
        "direction": "normal",
        "operation": "new_body"
      },
      "detection": {
        "visual_confidence": 0.98,
        "audio_correlation": "strong",
        "frame_number": 12
      }
    },
    {
      "id": "feature_2",
      "type": "Cut",
      "sketch": {
        "plane": {"type": "work_plane"},
        "geometry": [
          {
            "type": "Circle",
            "center": {"x": 0, "y": 0},
            "diameter": {"value": 30, "unit": "mm", "source": "audio", "timestamp": 8.7}
          }
        ]
      },
      "parameters": {
        "distance": {"value": 100, "unit": "mm", "source": "inferred"},
        "direction": "normal",
        "cut_type": "through_all"
      },
      "detection": {
        "visual_confidence": 0.90,
        "audio_correlation": "strong",
        "frame_number": 9
      }
    }
  ]
}
```

---

## Step 8: Final Semantic Geometry JSON

```json
{
  "part": {
    "name": "Hollow Cylinder",
    "units": "mm",
    "work_plane": {
      "type": "primitive",
      "face": "frontal"
    },
    "features": [
      {
        "id": "feature_1",
        "type": "Extrude",
        "sketch": {
          "plane": {
            "type": "work_plane"
          },
          "geometry": [
            {
              "type": "Circle",
              "center": {"x": 0, "y": 0},
              "diameter": {
                "value": 50,
                "unit": "mm",
                "source": "audio",
                "timestamp": 5.2
              }
            }
          ]
        },
        "parameters": {
          "distance": {
            "value": 100,
            "unit": "mm",
            "source": "audio",
            "timestamp": 12.3
          },
          "direction": "normal",
          "operation": "new_body"
        },
        "detection": {
          "visual_confidence": 0.98,
          "audio_correlation": "strong",
          "frame_number": 12
        }
      },
      {
        "id": "feature_2",
        "type": "Cut",
        "sketch": {
          "plane": {
            "type": "work_plane"
          },
          "geometry": [
            {
              "type": "Circle",
              "center": {"x": 0, "y": 0},
              "diameter": {
                "value": 30,
                "unit": "mm",
                "source": "audio",
                "timestamp": 8.7
              }
            }
          ]
        },
        "parameters": {
          "distance": {
            "value": 100,
            "unit": "mm",
            "source": "inferred"
          },
          "direction": "normal",
          "cut_type": "through_all"
        },
        "detection": {
          "visual_confidence": 0.90,
          "audio_correlation": "strong",
          "frame_number": 9
        }
      }
    ],
    "metadata": {
      "source": "video-interpreter",
      "workflow": "geometric-reconstruction",
      "video_file": "hollow_cylinder_tutorial.mp4",
      "total_frames": 25,
      "agents_used": 5,
      "timestamp": "2025-11-05T16:15:00Z"
    }
  }
}
```

---

## Step 9: Validation

```bash
$ semantic-geometry validate hollow_cylinder_tutorial_semantic_geometry.json
✅ Valid semantic geometry part: Hollow Cylinder
   - 2 features
   - All measurements validated
   - JSON Schema: PASS
   - Semantic validation: PASS
```

---

## Step 10: User Output

```
✅ Video Analysis Complete - Semantic Geometry Generated

**Workflow**: Geometric Reconstruction
**Configuration**:
- FPS: 0.5
- Agents: 5
- Focus: Geometric shapes and measurements

**Results**:
- Frames Analyzed: 25 frames
- Features Detected: 2 operations
- Measurements Extracted: 3 dimensions from audio
- Output: hollow_cylinder_tutorial_semantic_geometry.json (validated ✅)

**Semantic Geometry Summary**:
{
  "part_name": "Hollow Cylinder",
  "features": [
    "Extrude: Circle (Ø50mm) × 100mm",
    "Cut: Circle (Ø30mm) through-all"
  ],
  "work_plane": "frontal"
}

**Audio-Visual Correlations**:
- 5.2s: "diâmetro externo 50 milímetros" → Circle Ø50mm (frame 7, confidence: 0.95)
- 8.7s: "diâmetro interno 30 milímetros" → Circle Ø30mm cut (frame 9, confidence: 0.90)
- 12.3s: "altura 10 centímetros" → Extrude distance 100mm (frame 12, confidence: 0.98)

**Next Steps**:
1. Review: hollow_cylinder_tutorial_semantic_geometry.json
2. Validate: semantic-geometry validate <file>
3. Export to CAD: Coming soon (STEP AP242)
```

---

## Summary

This example demonstrates the complete pipeline:

1. **Video Input** → 25-second tutorial video
2. **Frame Extraction** → 25 frames at 0.5 fps
3. **Audio Transcription** → Whisper API with timestamps
4. **Parallel Analysis** → 5 agents analyze batches
5. **Feature Detection** → 2 features (Extrude + Cut)
6. **Measurement Extraction** → 3 audio measurements
7. **Aggregation** → Combine agent results
8. **Validation** → JSON Schema + semantic validation
9. **Output** → Valid Semantic Geometry JSON

**Key Success Factors**:
- Audio provides ALL measurements with timestamps
- Vision detects geometry types (circles)
- Operations inferred from context (hollow = extrude + cut)
- Deduplication prevents duplicate features
- Validation ensures correctness
