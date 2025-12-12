from app.models.schemas import WorkflowState
from typing import Dict, Any
import copy


class StateManager:
    """Manages workflow state during execution"""
    
    def __init__(self, initial_data: Dict[str, Any] = None):
        self.state = WorkflowState(
            data=initial_data or {},
            execution_path=[],
            metadata={}
        )
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update state data"""
        self.state.data.update(updates)
    
    def set_current_node(self, node_id: str) -> None:
        """Set current executing node"""
        self.state.current_node = node_id
    
    def add_to_path(self, node_id: str) -> None:
        """Add node to execution path"""
        self.state.execution_path.append(node_id)
    
    def get_state(self) -> Dict[str, Any]:
        """Get current state as dict"""
        return self.state.model_dump()
    
    def get_data(self) -> Dict[str, Any]:
        """Get just the data portion"""
        return copy.deepcopy(self.state.data)
    
    def evaluate_condition(self, condition: str) -> bool:
        """Evaluate a condition string against current state"""
        if not condition:
            return True
        
        # Simple condition evaluation
        # In production, use a safe eval or parsing library
        try:
            # Replace state references
            for key, value in self.state.data.items():
                if isinstance(value, (int, float, bool)):
                    condition = condition.replace(f"state.{key}", str(value))
            
            # Simple evaluation (for demo only)
            # WARNING: In production, use ast.literal_eval or a proper parser
            return eval(condition, {"__builtins__": {}}, {})
        except:
            return False