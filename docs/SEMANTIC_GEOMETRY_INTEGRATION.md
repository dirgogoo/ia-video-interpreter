# Semantic Geometry Integration Guide

## Overview

This guide explains how the **video-interpreter** skill integrates with the **semantic-geometry** library to convert video analysis into construction-based CAD representations.

**Location**: `~/semantic-geometry`
**GitHub**: https://github.com/dirgogoo/semantic-geometry

---

## Integration Architecture

```
Video Input
    ↓
Frame Extraction (0.5 fps)
    ↓
Audio Transcription (Whisper API)
    ↓
Parallel Agent Analysis (5 agents)
    ↓
Agent Results Aggregation
    ↓
Semantic Geometry JSON Generation ← YOU ARE HERE
    ↓
JSON Schema Validation
    ↓
Output: semantic_geometry.json
```

---

## Agent Output Format

Each agent analyzes a batch of frames and returns:

```json
{
  "batch_id": "batch_0",
  "time_range": {"start": 0.0, "end": 5.0},
  "frames_analyzed": 10,
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
            "source": "audio",
            "timestamp": 7.5
          },
          "direction": "normal",
          "operation": "new_body"
        },
        "detection": {
          "visual_confidence": 0.95,
          "audio_correlation": "strong",
          "frame_number": 12
        }
      }
    ]
  },
  "audio_visual_correlations": [
    {
      "timestamp": 5.2,
      "audio": "O diâmetro externo é 50 milímetros",
      "visual": "Circular shape detected in frame 10",
      "correlation": "Audio measurement matches visual geometry"
    }
  ],
  "summary": "Detected cylindrical extrusion with measurements from audio"
}
```

---

## Aggregation Strategy

### Step 1: Collect Features from All Batches

```python
all_features = []
for agent_result in agent_results:
    if "semantic_geometry" in agent_result and "features" in agent_result["semantic_geometry"]:
        features = agent_result["semantic_geometry"]["features"]
        all_features.extend(features)
```

### Step 2: Deduplicate Features

Features detected in multiple batches should be deduplicated:

```python
def deduplicate_features(features):
    """Remove duplicate features based on timestamp and geometry."""
    seen = {}
    unique_features = []

    for feature in features:
        # Create a key based on feature characteristics
        key = (
            feature["type"],
            feature.get("sketch", {}).get("geometry", [{}])[0].get("type"),
            feature.get("detection", {}).get("frame_number")
        )

        if key not in seen:
            seen[key] = True
            unique_features.append(feature)

    return unique_features
```

### Step 3: Order Features Chronologically

Features should be ordered by their detection frame/timestamp:

```python
def order_features(features):
    """Order features by detection frame number."""
    return sorted(
        features,
        key=lambda f: f.get("detection", {}).get("frame_number", 0)
    )
```

### Step 4: Determine Work Plane

Extract work plane from first feature or audio cues:

```python
def determine_work_plane(features, transcription):
    """Determine initial work plane from context."""
    # Check if mentioned in audio
    text = transcription.get("text", "").lower()

    if "frontal" in text or "frente" in text:
        return {"type": "primitive", "face": "frontal"}
    elif "superior" in text or "cima" in text:
        return {"type": "primitive", "face": "superior"}
    elif "lateral" in text:
        if "direita" in text or "right" in text:
            return {"type": "primitive", "face": "lateral_direita"}
        elif "esquerda" in text or "left" in text:
            return {"type": "primitive", "face": "lateral_esquerda"}
        return {"type": "primitive", "face": "lateral_direita"}

    # Default: frontal
    return {"type": "primitive", "face": "frontal"}
```

### Step 5: Build Final JSON

```python
def build_semantic_geometry_json(agent_results, transcription, video_path):
    """Build final Semantic Geometry JSON from agent results."""

    # Collect all features
    all_features = []
    for result in agent_results:
        if "semantic_geometry" in result:
            all_features.extend(result["semantic_geometry"].get("features", []))

    # Deduplicate and order
    unique_features = deduplicate_features(all_features)
    ordered_features = order_features(unique_features)

    # Determine work plane
    work_plane = determine_work_plane(ordered_features, transcription)

    # Determine part name from context
    part_name = extract_part_name(transcription) or "Reconstructed Part"

    # Build final JSON
    semantic_geometry = {
        "part": {
            "name": part_name,
            "units": "mm",
            "work_plane": work_plane,
            "features": ordered_features,
            "metadata": {
                "source": "video-interpreter",
                "workflow": "geometric-reconstruction",
                "video_file": str(video_path),
                "total_frames": sum(r.get("frames_analyzed", 0) for r in agent_results),
                "agents_used": len(agent_results)
            }
        }
    }

    return semantic_geometry
```

---

## Validation

After building the JSON, validate using semantic-geometry library:

```python
from semantic_geometry.schema import validate_part

validation_result = validate_part(semantic_geometry_json)

if not validation_result.is_valid:
    print("❌ Validation Errors:")
    for error in validation_result.errors:
        print(f"   - {error}")

    # Try to fix common issues
    semantic_geometry_json = fix_common_validation_errors(semantic_geometry_json)

    # Re-validate
    validation_result = validate_part(semantic_geometry_json)
```

### Common Validation Fixes

```python
def fix_common_validation_errors(json_data):
    """Fix common validation errors automatically."""

    # Ensure all measurements have required fields
    for feature in json_data.get("part", {}).get("features", []):
        for geom in feature.get("sketch", {}).get("geometry", []):
            # Add missing "source" field
            for key in ["diameter", "width", "height", "radius"]:
                if key in geom and isinstance(geom[key], dict):
                    if "source" not in geom[key]:
                        geom[key]["source"] = "audio"

        # Add missing direction
        if "parameters" in feature and "direction" not in feature["parameters"]:
            feature["parameters"]["direction"] = "normal"

    return json_data
```

---

## Example: Complete Aggregation

```python
# After all agents finish
agent_results = [
    # Results from batch_0, batch_1, batch_2, batch_3, batch_4
]

# Build semantic geometry JSON
semantic_geometry_json = build_semantic_geometry_json(
    agent_results=agent_results,
    transcription=result['transcription'],
    video_path=video_path
)

# Validate
validation_result = validate_part(semantic_geometry_json)

if validation_result.is_valid:
    # Save to file
    output_path = video_path.parent / f"{video_path.stem}_semantic_geometry.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(semantic_geometry_json, f, indent=2, ensure_ascii=False)

    print(f"✅ Semantic Geometry JSON validated and saved to: {output_path}")

    # Print summary
    features = semantic_geometry_json["part"]["features"]
    print(f"\n📊 Summary:")
    print(f"   - Part Name: {semantic_geometry_json['part']['name']}")
    print(f"   - Features: {len(features)}")
    print(f"   - Work Plane: {semantic_geometry_json['part']['work_plane']['face']}")

    for i, feature in enumerate(features, 1):
        geom_type = feature["sketch"]["geometry"][0]["type"]
        op_type = feature["type"]
        print(f"   - Feature {i}: {op_type} ({geom_type})")
else:
    print("❌ Validation failed:")
    for error in validation_result.errors:
        print(f"   - {error}")
```

---

## Measurement Extraction from Audio

Helper function to extract measurements from transcription:

```python
import re

def extract_measurements(transcription_text):
    """Extract measurements from audio transcription."""
    measurements = []

    # Patterns for Portuguese
    patterns = [
        r"diâmetro\s+(?:de\s+)?(\d+(?:\.\d+)?)\s*(mm|milímetros|cm|centímetros)",
        r"largura\s+(?:de\s+)?(\d+(?:\.\d+)?)\s*(mm|milímetros|cm|centímetros)",
        r"altura\s+(?:de\s+)?(\d+(?:\.\d+)?)\s*(mm|milímetros|cm|centímetros)",
        r"comprimento\s+(?:de\s+)?(\d+(?:\.\d+)?)\s*(mm|milímetros|cm|centímetros)",
        r"raio\s+(?:de\s+)?(\d+(?:\.\d+)?)\s*(mm|milímetros|cm|centímetros)",
    ]

    for pattern in patterns:
        matches = re.finditer(pattern, transcription_text.lower())
        for match in matches:
            value = float(match.group(1))
            unit = match.group(2)

            # Convert to mm
            if unit in ["cm", "centímetros"]:
                value *= 10

            measurements.append({
                "value": value,
                "unit": "mm",
                "source": "audio",
                "original_text": match.group(0)
            })

    return measurements
```

---

## Next Steps

After generating the Semantic Geometry JSON:

1. **Manual Review**: User reviews the JSON for accuracy
2. **CLI Validation**: `semantic-geometry validate output.json`
3. **CAD Export**: Convert to STEP AP242 (future feature)
4. **Refinement**: User can manually edit JSON before export

---

## References

- **Semantic Geometry Library**: https://github.com/dirgogoo/semantic-geometry
- **JSON Schema**: `/schemas/semantic-geometry-schema.json`
- **Video Interpreter Skill**: `C:\Users\conta\.claude\skills\video-interpreter\skill.md`
- **Workflow Config**: `/workflows/geometric-reconstruction.yml`
