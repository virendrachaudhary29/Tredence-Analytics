from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
from enum import Enum


class NodeType(str, Enum):
    FUNCTION = "function"
    CONDITION = "condition"
    LOOP_START = "loop_start"
    LOOP_END = "loop_end"


class Node(BaseModel):
    name: str
    function_name: str  #registered tool
    config: Dict[str, Any] = Field(default_factory=dict)
    node_type: NodeType = NodeType.FUNCTION


class Edge(BaseModel):
    source: str
    target: str
    condition: Optional[str] = None  


class GraphDefinition(BaseModel):
    nodes: Dict[str, Node]  
    edges: List[Edge]
    entry_point: str 


class WorkflowState(BaseModel):
    data: Dict[str, Any] = Field(default_factory=dict)
    current_node: Optional[str] = None
    execution_path: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True


class CreateGraphRequest(BaseModel):
    graph_def: GraphDefinition
    name: Optional[str] = None


class RunGraphRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any] = Field(default_factory=dict)


class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ExecutionLog(BaseModel):
    timestamp: str
    node_id: str
    message: str
    state_snapshot: Dict[str, Any]