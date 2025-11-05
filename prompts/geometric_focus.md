# Geometric Reconstruction Focus

## Output Format: Semantic Geometry JSON

Your goal is to generate a **Semantic Geometry JSON** representation following the construction-based CAD format.

Pay special attention to:

- **2D Sketches**: Identify geometric primitives (circles, rectangles, polygons, lines, arcs)
- **3D Operations**: Detect construction operations (extrude, cut, revolve, fillet, chamfer)
- **Measurements from Audio**: Extract ALL dimensions, diameters, distances from spoken audio
- **Work Plane**: Identify initial face (frontal, superior, lateral_direita, lateral_esquerda, inferior, posterior)
- **Operation Sequence**: Document the order of features/operations
- **Local Coordinates**: All geometry centered at (0,0) relative to current plane/face

**Audio Priority: HIGH** - ALL measurements come from audio, vision only detects geometry types.

## Semantic Geometry Structure

```json
{
  "part": {
    "name": "Part name from context",
    "units": "mm",
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
          "distance": {"value": 100, "unit": "mm", "source": "audio", "timestamp": 7.5},
          "direction": "normal",
          "operation": "new_body"
        },
        "detection": {
          "visual_confidence": 0.95,
          "audio_correlation": "strong",
          "frame_number": 12
        }
      }
    ],
    "metadata": {
      "source": "video-interpreter",
      "workflow": "geometric-reconstruction"
    }
  }
}
```

## Analysis Guidelines

1. **Detect Geometry Type Visually**:
   - Circle/Cylinder: Round shapes
   - Rectangle: 4 corners, right angles
   - Polygon: Regular shapes (hexagons, octagons)

2. **Extract Measurements from Audio**:
   - "diâmetro de 50 milímetros" → `{"value": 50, "unit": "mm"}`
   - "altura de 10 centímetros" → `{"value": 100, "unit": "mm"}` (convert to mm)
   - "raio de 25" → `{"value": 50, "unit": "mm"}` (diameter = 2*radius)

3. **Identify Operations**:
   - **Extrude**: Pushing 2D sketch into 3D (most common)
   - **Cut**: Removing material (holes, pockets)
   - **Revolve**: Rotating sketch around axis
   - **Fillet**: Rounded edges (chamfer for angled)

4. **Correlate Audio Timestamps**:
   - Match spoken measurements with visual frames
   - Add `timestamp` field to all measurements
   - Note confidence level in `detection` object

## Example Correlations

### Example 1: Simple Cylinder
- **Visual (frame 5)**: Round shape, cylindrical
- **Audio (5.2s)**: "O diâmetro externo é 50 milímetros"
- **Audio (7.5s)**: "E a altura é 10 centímetros"
- **Output**:
```json
{
  "type": "Extrude",
  "sketch": {
    "geometry": [{"type": "Circle", "diameter": {"value": 50, "unit": "mm", "timestamp": 5.2}}]
  },
  "parameters": {
    "distance": {"value": 100, "unit": "mm", "timestamp": 7.5}
  }
}
```

### Example 2: Hollow Cylinder (Extrude + Cut)
- **Visual (frame 10)**: Cylinder with hole through center
- **Audio (10.5s)**: "Diâmetro externo 50, interno 30"
- **Audio (12.0s)**: "Altura total 10 centímetros"
- **Output**: Two features:
  1. Extrude circle (outer diameter 50mm, height 100mm)
  2. Cut circle through-all (inner diameter 30mm)

## Important Notes

- **ALL measurements MUST come from audio** (vision only detects shapes)
- Use `"source": "audio"` with `"timestamp"` for all dimensions
- Center all geometry at `(0, 0)` in local coordinates
- Default to `"mm"` as base unit (convert from cm/m if needed)
- Include `detection` metadata with visual confidence and audio correlation
