from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os
from fastapi.middleware.cors import CORSMiddleware

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
        # Create a temporary file with the Python code
        temp_file = "temp.py"
        with open(temp_file, "w") as f:
            f.write(request.code)

        try:
            # Execute the code using the custom Python interpreter
            result = subprocess.run(
                [PYTHON_PATH, temp_file],
                capture_output=True,
                text=True,
                timeout=30
            )

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
        raise HTTPException(status_code=408, detail="Code execution timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 