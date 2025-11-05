"""
Policies Applied:
- Policy 6.1: Unit test coverage for business logic
- Policy 6.5: Test naming convention (should/when pattern)
- Policy 6.6: AAA Pattern (Arrange-Act-Assert)
- Policy 6.7: Test isolation

Tests for workflow loading and detection.
"""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from workflow_loader import load_workflow, detect_workflow_from_keywords

# Get absolute path to workflows directory
TEST_DIR = Path(__file__).parent.parent
WORKFLOWS_DIR = TEST_DIR / "workflows"


def test_load_workflow_geometric():
    """Should load geometric reconstruction workflow configuration"""
    # Arrange
    workflow_path = WORKFLOWS_DIR / "geometric-reconstruction.yml"

    # Act
    workflow = load_workflow(workflow_path)

    # Assert
    assert workflow["name"] == "Geometric Reconstruction"
    assert workflow["config"]["fps"] == 0.5
    assert workflow["config"]["agents"] == 5
    assert workflow["config"]["focus"] == "shapes"
    assert "phases" in workflow
    assert len(workflow["phases"]) > 0


def test_load_workflow_ui():
    """Should load UI replication workflow configuration"""
    # Arrange
    workflow_path = WORKFLOWS_DIR / "ui-replication.yml"

    # Act
    workflow = load_workflow(workflow_path)

    # Assert
    assert workflow["name"] == "UI Replication"
    assert workflow["config"]["fps"] == 2
    assert workflow["config"]["agents"] == 10


def test_load_workflow_missing_file():
    """Should raise error when workflow file doesn't exist"""
    # Arrange
    workflow_path = Path("nonexistent.yml")

    # Act & Assert
    with pytest.raises(FileNotFoundError):
        load_workflow(workflow_path)


def test_detect_workflow_geometric_keywords():
    """Should detect geometric workflow from user input with shape keywords"""
    # Arrange
    user_input = "analyze geometric shapes with measurements"

    # Act
    workflow_name = detect_workflow_from_keywords(user_input)

    # Assert
    assert workflow_name == "geometric-reconstruction"


def test_detect_workflow_ui_keywords():
    """Should detect UI workflow from user input with interface keywords"""
    # Arrange
    user_input = "replicate the user interface from this video"

    # Act
    workflow_name = detect_workflow_from_keywords(user_input)

    # Assert
    assert workflow_name == "ui-replication"


def test_detect_workflow_fallback_to_generic():
    """Should fallback to generic workflow when no keywords match"""
    # Arrange
    user_input = "summarize this video"

    # Act
    workflow_name = detect_workflow_from_keywords(user_input)

    # Assert
    assert workflow_name == "generic-analysis"


def test_detect_workflow_portuguese_keywords():
    """Should detect workflow with Portuguese keywords"""
    # Arrange
    user_input = "reconstruir formas geometricas"

    # Act
    workflow_name = detect_workflow_from_keywords(user_input)

    # Assert
    assert workflow_name == "geometric-reconstruction"
