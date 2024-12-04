from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os
import logging
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('python_execution.log'),
        logging.StreamHandler()
    ]
)

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to custom Python interpreter
PYTHON_PATH = os.path.join(os.path.dirname(__file__), "../../../cpython-main 2/python")

class CodeRequest(BaseModel):
    code: str

class CodeResponse(BaseModel):
    output: str

@app.post("/api/execute")
async def execute_code(request: CodeRequest) -> CodeResponse:
    try:
        # Log the incoming code
        logging.info(f"Executing code:\n{request.code}")
        
        # Create a temporary file with the Python code
        temp_file = "temp.py"
        with open(temp_file, "w") as f:
            f.write(request.code)

        try:
            # Log the Python interpreter being used
            logging.info(f"Using Python interpreter: {PYTHON_PATH}")
            
            # Execute the code using the custom Python interpreter
            result = subprocess.run(
                [PYTHON_PATH, temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )

            # Log the execution result
            logging.info(f"Execution completed with return code: {result.returncode}")
            if result.stdout:
                logging.info(f"stdout:\n{result.stdout}")
            if result.stderr:
                logging.error(f"stderr:\n{result.stderr}")

            # Combine stdout and stderr for output
            output = result.stdout
            if result.stderr:
                output += f"\nErrors:\n{result.stderr}"

            return CodeResponse(output=output)

        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file):
                os.remove(temp_file)

    except subprocess.TimeoutExpired:
        logging.error("Code execution timed out")
        raise HTTPException(status_code=408, detail="Code execution timed out")
    except Exception as e:
        logging.error(f"Error executing code: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/test")
async def test_python():
    """Test the Python interpreter setup"""
    try:
        result = subprocess.run(
            [PYTHON_PATH, "-c", "print('Python test successful')"],
            capture_output=True,
            text=True
        )
        return {
            "python_path": PYTHON_PATH,
            "version": subprocess.check_output([PYTHON_PATH, "--version"]).decode(),
            "test_output": result.stdout,
            "working_directory": os.getcwd(),
        }
    except Exception as e:
        return {"error": str(e)} 