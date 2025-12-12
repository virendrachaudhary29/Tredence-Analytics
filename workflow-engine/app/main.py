from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as graph_router
from app.engine.graph import graph_manager
from app.workflows.code_review import create_code_review_workflow
import uvicorn

app = FastAPI(
    title="Workflow Engine API",
    description="A simplified workflow/graph engine similar to LangGraph",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(graph_router)


@app.on_event("startup")
async def startup_event():
    """Initialize the application with example workflows"""
    # Create example code review workflow
    code_review_graph = create_code_review_workflow()
    graph_id = graph_manager.create_graph(code_review_graph)
    
    print(f"🚀 Workflow Engine started!")
    print(f"📝 Example workflow created with ID: {graph_id}")
    print(f"🔧 Available tools: {graph_manager.graphs[graph_id].graph_def.nodes.keys()}")


@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "message": "Workflow Engine API",
        "version": "1.0.0",
        "endpoints": {
            "create_graph": "POST /graph/create",
            "run_graph": "POST /graph/run",
            "get_state": "GET /graph/state/{run_id}",
            "list_tools": "GET /graph/tools",
            "list_graphs": "GET /graph/graphs"
        },
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "workflow-engine"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)