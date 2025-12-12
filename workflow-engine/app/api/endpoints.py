from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from app.models.schemas import (
    CreateGraphRequest, RunGraphRequest, GraphDefinition,
    WorkflowState, ExecutionLog
)
from app.engine.graph import graph_manager
from app.engine.registry import tool_registry
import json
import asyncio

router = APIRouter(prefix="/graph", tags=["workflow"])


@router.post("/create")
async def create_graph(request: CreateGraphRequest):
    """Create a new workflow graph"""
    try:
        graph_id = graph_manager.create_graph(request.graph_def)
        return {
            "graph_id": graph_id,
            "name": request.name,
            "message": f"Graph created with {len(request.graph_def.nodes)} nodes",
            "entry_point": request.graph_def.entry_point
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/run")
async def run_graph(request: RunGraphRequest):
    """Execute a workflow graph"""
    try:
        run_id = graph_manager.run_graph(
            request.graph_id, 
            request.initial_state
        )
        
        run_result = graph_manager.get_run(run_id)
        
        return {
            "run_id": run_id,
            "graph_id": request.graph_id,
            "status": run_result["status"],
            "final_state": run_result["final_state"],
            "execution_log": run_result["execution_log"][-10:],  # Last 10 entries
            "iterations": run_result["iterations"]
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/state/{run_id}")
async def get_run_state(run_id: str):
    """Get the state of a specific run"""
    run_result = graph_manager.get_run(run_id)
    
    if not run_result:
        raise HTTPException(status_code=404, detail=f"Run '{run_id}' not found")
    
    return {
        "run_id": run_id,
        "status": run_result["status"],
        "state": run_result["final_state"],
        "created_at": run_result["created_at"],
        "iterations": run_result["iterations"]
    }


@router.get("/tools")
async def list_tools():
    """List all available tools"""
    return {
        "tools": tool_registry.list_tools(),
        "count": len(tool_registry.list_tools())
    }


@router.get("/graphs")
async def list_graphs():
    """List all created graphs"""
    graphs = []
    for graph_id, graph in graph_manager.graphs.items():
        graphs.append({
            "graph_id": graph_id,
            "node_count": len(graph.nodes),
            "entry_point": graph.graph_def.entry_point
        })
    
    return {"graphs": graphs, "count": len(graphs)}


# Optional WebSocket endpoint for real-time updates
@router.websocket("/ws/{run_id}")
async def websocket_endpoint(websocket: WebSocket, run_id: str):
    """WebSocket for real-time execution updates"""
    await websocket.accept()
    
    try:
        # In a real implementation, you'd stream execution updates
        # For demo, we'll just send periodic updates
        run_result = graph_manager.get_run(run_id)
        
        if run_result:
            await websocket.send_json({
                "type": "status",
                "message": f"Run {run_id} found",
                "status": run_result["status"]
            })
            
            # Send execution log entries
            for log_entry in run_result["execution_log"]:
                await websocket.send_json({
                    "type": "log",
                    "data": log_entry
                })
                await asyncio.sleep(0.1)  # Simulate streaming
        else:
            await websocket.send_json({
                "type": "error",
                "message": f"Run {run_id} not found"
            })
    
    except WebSocketDisconnect:
        print(f"Client disconnected from run {run_id}")
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })