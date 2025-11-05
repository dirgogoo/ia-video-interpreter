"""
Policies Applied:
- Policy 3.2: DRY - Extract workflow detection logic
- Policy 3.3: SRP - Single responsibility per function
- Policy 3.5: Meaningful names
- Policy 3.6: Error handling mandatory
- Policy 3.7: No magic numbers

Workflow loading and detection module.
"""
import yaml
from pathlib import Path
from typing import Dict, Any


def load_workflow(workflow_path: Path) -> Dict[str, Any]:
    """
    Load workflow configuration from YAML file.

    Policy 3.6: Error handling - validate file exists
    Policy 3.5: Meaningful name - clear what it returns

    Args:
        workflow_path: Path to workflow YAML file

    Returns:
        Dictionary containing workflow configuration

    Raises:
        FileNotFoundError: If workflow file doesn't exist
        yaml.YAMLError: If YAML is malformed
    """
    # Policy 3.6: Error handling mandatory
    if not workflow_path.exists():
        raise FileNotFoundError(f"Workflow file not found: {workflow_path}")

    try:
        with open(workflow_path, 'r', encoding='utf-8') as f:
            workflow_config = yaml.safe_load(f)

        # Validate required fields
        if not workflow_config:
            raise ValueError(f"Empty workflow file: {workflow_path}")

        if "name" not in workflow_config:
            raise ValueError(f"Workflow missing 'name' field: {workflow_path}")

        return workflow_config

    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in workflow file: {e}")


def detect_workflow_from_keywords(user_input: str) -> str:
    """
    Detect appropriate workflow based on user input keywords.

    Policy 3.2: DRY - Centralized workflow detection logic
    Policy 3.3: SRP - Single responsibility: keyword matching

    Args:
        user_input: User's task description

    Returns:
        Workflow name (e.g., 'geometric-reconstruction', 'ui-replication')
        Falls back to 'generic-analysis' if no match
    """
    # Policy 3.7: No magic numbers - named constant
    # Get absolute path relative to this script
    SCRIPT_DIR = Path(__file__).parent.parent
    WORKFLOWS_DIR = SCRIPT_DIR / "workflows"

    user_input_lower = user_input.lower()

    # Load all workflows and check trigger keywords
    for workflow_file in WORKFLOWS_DIR.glob("*.yml"):
        # Skip generic (it's the fallback)
        if workflow_file.stem == "generic-analysis":
            continue

        try:
            workflow = load_workflow(workflow_file)

            # Check trigger keywords
            triggers = workflow.get("triggers", {})
            keywords = triggers.get("keywords", [])

            # Match if any keyword found in user input
            if any(keyword.lower() in user_input_lower for keyword in keywords):
                return workflow_file.stem

        except (FileNotFoundError, ValueError):
            # Skip malformed workflows
            continue

    # Default fallback
    return "generic-analysis"
