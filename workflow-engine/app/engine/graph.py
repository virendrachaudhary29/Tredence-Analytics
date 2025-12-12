from app.models.schemas import GraphDefinition, Node, Edge, RunStatus
from app.engine.registry import tool_registry
from app.engine.state import StateManager
from typing import Dict, List, Any, Optional, Tuple
import uuid
import time


class WorkflowGraph:
    """Core workflow/graph engine"""
    
    def __init__(self, graph_id: str, graph_def: GraphDefinition):
        self.graph_id = graph_id
        self.graph_def = graph_def
        self.nodes = graph_def.nodes
        self.edges = graph_def.edges
        
        # Build adjacency list for quick traversal
        self.adjacency = self._build_adjacency_list()
    
    def _build_adjacency_list(self) -> Dict[str, List[Edge]]:
        """Build adjacency list from edges"""
        adjacency = {node_id: [] for node_id in self.nodes.keys()}
        
        for edge in self.edges:
            if edge.source in adjacency:
                adjacency[edge.source].append(edge)
        
        return adjacency
    
    def get_next_node(self, current_node: str, state: StateManager) -> Optional[str]:
        """Determine next node based on edges and conditions"""
        if current_node not in self.adjacency:
            return None
        
        edges = self.adjacency[current_node]
        
        if not edges:
            return None
        
        # If multiple edges, check conditions
        for edge in edges:
            if edge.condition:
                if state.evaluate_condition(edge.condition):
                    return edge.target
            else:
                # Default edge (no condition)
                return edge.target
        
        # If no conditions match, return first edge
        return edges[0].target if edges else None
    
    def execute_node(self, node_id: str, state: StateManager) -> Dict[str, Any]:
        """Execute a single node"""
        if node_id not in self.nodes:
            raise ValueError(f"Node '{node_id}' not found in graph")
        
        node = self.nodes[node_id]
        state.set_current_node(node_id)
        state.add_to_path(node_id)
        
        # Execute the node's function
        try:
            result = tool_registry.execute(node.function_name, state.get_data())
            state.update(result)
            
            # Add node execution to result
            result["_node_executed"] = node_id
            result["_success"] = True
            
            return result
        except Exception as e:
            return {
                "_node_executed": node_id,
                "_success": False,
                "_error": str(e)
            }
    
    def execute(self, initial_state: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute the entire workflow"""
        state_manager = StateManager(initial_state or {})
        execution_log = []
        visited_nodes = set()
        
        current_node = self.graph_def.entry_point
        
        # Loop control
        max_iterations = 100  # Safety limit
        iteration = 0
        
        while current_node and iteration < max_iterations:
            iteration += 1
            
            # Check for loops
            if current_node in visited_nodes:
                # Handle potential infinite loop
                execution_log.append({
                    "node": current_node,
                    "message": "Loop detected, stopping execution",
                    "state": state_manager.get_data()
                })
                break
            
            visited_nodes.add(current_node)
            
            # Execute current node
            start_time = time.time()
            result = self.execute_node(current_node, state_manager)
            execution_time = time.time() - start_time
            
            # Log execution
            log_entry = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "node": current_node,
                "execution_time": execution_time,
                "result": result.get("_success", False),
                "state_snapshot": state_manager.get_data()
            }
            
            if not result.get("_success", False):
                log_entry["error"] = result.get("_error", "Unknown error")
            
            execution_log.append(log_entry)
            
            # Stop if node failed
            if not result.get("_success", True):
                break
            
            # Get next node
            next_node = self.get_next_node(current_node, state_manager)
            
            # Handle loops (simple loop detection)
            if next_node == current_node:
                # Self-loop, check for exit condition
                if state_manager.evaluate_condition("state.loop_count > 5"):
                    break
            
            current_node = next_node
        
        return {
            "final_state": state_manager.get_state(),
            "execution_log": execution_log,
            "iterations": iteration,
            "status": "completed" if iteration < max_iterations else "stopped"
        }


class GraphManager:
    """Manages multiple workflow graphs and runs"""
    
    def __init__(self):
        self.graphs: Dict[str, WorkflowGraph] = {}
        self.runs: Dict[str, Dict[str, Any]] = {}
    
    def create_graph(self, graph_def: GraphDefinition) -> str:
        """Create a new workflow graph"""
        graph_id = str(uuid.uuid4())[:8]
        graph = WorkflowGraph(graph_id, graph_def)
        self.graphs[graph_id] = graph
        return graph_id
    
    def get_graph(self, graph_id: str) -> Optional[WorkflowGraph]:
        """Get a graph by ID"""
        return self.graphs.get(graph_id)
    
    def run_graph(self, graph_id: str, initial_state: Dict[str, Any]) -> str:
        """Execute a graph and track the run"""
        graph = self.get_graph(graph_id)
        if not graph:
            raise ValueError(f"Graph '{graph_id}' not found")
        
        run_id = str(uuid.uuid4())[:8]
        
        # Execute synchronously (could be async)
        result = graph.execute(initial_state)
        
        # Store run result
        self.runs[run_id] = {
            "run_id": run_id,
            "graph_id": graph_id,
            "status": result["status"],
            "final_state": result["final_state"],
            "execution_log": result["execution_log"],
            "iterations": result["iterations"],
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return run_id
    
    def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get run result by ID"""
        return self.runs.get(run_id)


# Global graph manager instance
graph_manager = GraphManager()