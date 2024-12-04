import subprocess
import os
import tempfile
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class CodeExecutor:
    def __init__(self, python_path: str = 'python3'):
        self.python_path = python_path
        self.timeout = 5  # Maximum execution time in seconds

    def execute_code(self, code: str) -> Tuple[str, str, int]:
        """
        Execute Python code in a sandboxed environment.
        Returns: (stdout, stderr, return_code)
        """
        try:
            # Create a temporary file to store the code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name

            # Execute the code in a separate process
            process = subprocess.run(
                [self.python_path, temp_file_path],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            return process.stdout, process.stderr, process.returncode

        except subprocess.TimeoutExpired:
            return "", "Code execution timed out", 1
        except Exception as e:
            logger.error(f"Error executing code: {str(e)}")
            return "", f"Error executing code: {str(e)}", 1
        finally:
            # Clean up temporary file
            if 'temp_file_path' in locals():
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    logger.error(f"Error cleaning up temporary file: {str(e)}") 