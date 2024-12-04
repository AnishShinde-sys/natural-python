from typing import Dict, Any

class WebPythonExecutor:
    """
    Interface for executing Python code in the browser using Pyodide.
    This class defines the Python-side interface that will interact with
    the JavaScript Pyodide implementation.
    """
    def __init__(self):
        self.variables: Dict[str, Any] = {}
        
    def prepare_code(self, code: str) -> str:
        """
        Prepare Python code for browser execution by wrapping it
        with necessary context and safety measures.
        """
        # Wrap code in try-except for better error handling
        wrapped_code = f"""
try:
    {code}
except Exception as e:
    print(f"Error: {{str(e)}}")
"""
        return wrapped_code 