import subprocess
import sys
import tempfile
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class ExecutionResult:
    stdout: str
    stderr: str
    return_code: int
    timed_out: bool = False

class Sandbox:
    def __init__(self, timeout: int = 2):
        self.timeout = timeout

    def run(self, code: str) -> ExecutionResult:
        # Create a temporary file to run the code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp_file:
            tmp_file.write(code)
            tmp_path = tmp_file.name

        try:
            # Run the code in a subprocess
            result = subprocess.run(
                [sys.executable, tmp_path],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            return ExecutionResult(
                stdout=result.stdout,
                stderr=result.stderr,
                return_code=result.returncode
            )
        except subprocess.TimeoutExpired as e:
            return ExecutionResult(
                stdout=e.stdout if e.stdout else "",
                stderr=e.stderr if e.stderr else "Execution timed out.",
                return_code=-1,
                timed_out=True
            )
        except Exception as e:
            return ExecutionResult(
                stdout="",
                stderr=str(e),
                return_code=-1
            )
        finally:
            # Clean up the temporary file
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
