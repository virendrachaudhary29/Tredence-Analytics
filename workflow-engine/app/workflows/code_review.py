"""
Example workflow: Code Review Mini-Agent
Implements Option A from the assignment
"""

from app.models.schemas import GraphDefinition, Node, Edge, NodeType


def create_code_review_workflow() -> GraphDefinition:
    """Create the code review workflow graph"""
    
    nodes = {
        "extract": Node(
            name="Extract Functions",
            function_name="extract_functions",
            node_type=NodeType.FUNCTION
        ),
        "analyze": Node(
            name="Analyze Complexity",
            function_name="check_complexity",
            node_type=NodeType.FUNCTION
        ),
        "detect": Node(
            name="Detect Issues",
            function_name="detect_issues",
            node_type=NodeType.FUNCTION
        ),
        "suggest": Node(
            name="Suggest Improvements",
            function_name="suggest_improvements",
            node_type=NodeType.FUNCTION
        ),
        "check_quality": Node(
            name="Check Quality Threshold",
            function_name="check_quality_threshold",
            node_type=NodeType.CONDITION
        )
    }
    
    edges = [
        Edge(source="extract", target="analyze"),
        Edge(source="analyze", target="detect"),
        Edge(source="detect", target="suggest"),
        Edge(source="suggest", target="check_quality"),
        Edge(
            source="check_quality",
            target="suggest",
            condition="not state.meets_threshold"
        )
    ]
    
    return GraphDefinition(
        nodes=nodes,
        edges=edges,
        entry_point="extract"
    )


# Example initial state for testing
def get_initial_state() -> dict:
    return {
        "code_snippet": "def example(): pass",
        "quality_threshold": 70,
        "max_iterations": 3
    }