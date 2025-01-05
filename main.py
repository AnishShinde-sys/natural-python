from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os
import logging
from fastapi.middleware.cors import CORSMiddleware
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")
openai.api_key = api_key

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

class CodeRequest(BaseModel):
    input: str
    is_natural_language: bool = False

class CodeResponse(BaseModel):
    output: str
    generated_code: str = None

def process_natural_language(input_text: str) -> str:
    """Convert natural language to Python code using OpenAI."""
    try:
        logging.info(f"Processing natural language input: {input_text}")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": """You are a Python code generator that converts natural language instructions into executable Python code. Convert simple instructions into Python code.

Examples:

Input: "make a variable called hi and set it equal to 10"
Output: hi = 10

Input: "create a variable message with Hello World"
Output: message = "Hello World"

Input: "make a list called numbers with 1,2,3,4,5"
Output: numbers = [1, 2, 3, 4, 5]

Input: "print hello world 3 times"
Output: for i in range(3):
    print("hello world")

Guidelines:
- Only output the exact Python code needed
- No comments or explanations
- Create variables with exactly the names specified
- Keep code extremely simple
- Focus on basic operations: variables, printing, lists, simple loops"""},
                {"role": "user", "content": input_text}
            ],
            temperature=0.1,  # Lower temperature for more consistent output
            max_tokens=150
        )
        generated_code = response.choices[0].message.content.strip()
        logging.info(f"Generated code: {generated_code}")
        return generated_code
    except Exception as e:
        logging.error(f"OpenAI API error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating code: {str(e)}")

@app.post("/api/execute")
async def execute_code(request: CodeRequest) -> CodeResponse:
    try:
        # Process natural language if needed
        code_to_execute = process_natural_language(request.input) if request.is_natural_language else request.input
        
        # Log the code being executed
        logging.info(f"Executing code:\n{code_to_execute}")
        
        # Create a temporary file with the Python code
        temp_file = "temp.py"
        with open(temp_file, "w") as f:
            f.write(code_to_execute)

        try:
            # Execute the code
            result = subprocess.run(
                ["python3", temp_file],
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

            return CodeResponse(
                output=output,
                generated_code=code_to_execute if request.is_natural_language else None
            )

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
    """Health check endpoint that also verifies OpenAI API key"""
    try:
        # Test OpenAI API key
        openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        return {
            "status": "healthy",
            "openai_api": "configured"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "openai_api_error": str(e)
        }