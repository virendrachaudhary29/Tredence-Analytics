from typing import Dict, Callable, Any, Optional, List
import inspect


class ToolRegistry:
    
    
    def __init__(self):
        self._tools: Dict[str, Callable] = {}
    
    def register(self, name: str, func: Callable) -> None:
       
        self._tools[name] = func
    
    def register_many(self, tools: Dict[str, Callable]) -> None:
       
        self._tools.update(tools)
    
    def get(self, name: str) -> Optional[Callable]:
       
        return self._tools.get(name)
    
    def execute(self, name: str, state: Dict[str, Any]) -> Dict[str, Any]:
       
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' not found in registry")
        
        func = self._tools[name]
        
        # Check if function accepts state parameter
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        
        if 'state' in params:
            result = func(state=state)
        else:
            # Try to pass state as kwargs
            result = func(**state)
        
        return result
    
    def list_tools(self) -> List[str]:
       
        return list(self._tools.keys())


# Global tool registry instance
tool_registry = ToolRegistry()


# Pre-register some example tools
def extract_functions(state: Dict[str, Any]) -> Dict[str, Any]:
    
    return {
        "functions": ["main()", "calculate()", "validate()"],
        "function_count": 3,
        "message": "Functions extracted"
    }


def check_complexity(state: Dict[str, Any]) -> Dict[str, Any]:
    """Mock complexity analysis"""
    func_count = state.get("function_count", 0)
    complexity_score = func_count * 10  
    return {
        "complexity_score": complexity_score,
        "is_complex": complexity_score > 20
    }


def detect_issues(state: Dict[str, Any]) -> Dict[str, Any]:
    """Mock issue detection"""
    score = state.get("complexity_score", 0)
    issues = []
    
    if score > 30:
        issues.append("High complexity")
    if score < 10:
        issues.append("Too simple")
    
    return {
        "issues": issues,
        "issue_count": len(issues),
        "quality_score": 100 - (len(issues) * 20)
    }


def suggest_improvements(state: Dict[str, Any]) -> Dict[str, Any]:
    """Mock improvement suggestions"""
    issues = state.get("issues", [])
    suggestions = []
    
    if "High complexity" in issues:
        suggestions.append("Consider breaking down complex functions")
    if "Too simple" in issues:
        suggestions.append("Add more functionality or combine functions")
    
    return {
        "suggestions": suggestions,
        "improved": len(suggestions) > 0
    }


def check_quality_threshold(state: Dict[str, Any]) -> Dict[str, Any]:
    """Check if quality meets threshold"""
    quality_score = state.get("quality_score", 0)
    threshold = state.get("quality_threshold", 70)
    
    return {
        "meets_threshold": quality_score >= threshold,
        "threshold": threshold,
        "current_score": quality_score
    }


# Register all tools
tool_registry.register("extract_functions", extract_functions)
tool_registry.register("check_complexity", check_complexity)
tool_registry.register("detect_issues", detect_issues)
tool_registry.register("suggest_improvements", suggest_improvements)
tool_registry.register("check_quality_threshold", check_quality_threshold)