from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add after creating the FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to your custom Python interpreter
PYTHON_PATH = os.path.join(os.path.dirname(__file__), "../../../cpython-main 2/python")

class CodeRequest(BaseModel):
    code: str

class CodeResponse(BaseModel):
    output: str

@app.post("/api/execute")
async def execute_code(request: CodeRequest) -> CodeResponse:
    try:
        # Create a temporary file to store the code
        with open("temp.py", "w") as f:
            f.write(request.code)

        # Execute the code using the custom Python interpreter
        result = subprocess.run(
            [PYTHON_PATH, "temp.py"],
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )

        # Clean up the temporary file
        os.remove("temp.py")

        # Return both stdout and stderr
        output = result.stdout
        if result.stderr:
            output += "\nErrors:\n" + result.stderr

        return CodeResponse(output=output)

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Code execution timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 