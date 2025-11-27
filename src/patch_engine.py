import re
import ast
import requests
import json
from typing import Optional, Tuple, List

class PatchEngine:
    def __init__(self, model: str = "llama3"):
        self.model = model

    def analyze_error(self, stderr: str) -> Tuple[Optional[str], Optional[int], Optional[str]]:
        """
        Analyzes stderr to find the error type, line number, and message.
        Returns (error_type, line_number, error_message).
        """
        if not stderr:
            return None, None, None

        # Common Python error pattern: "File "...", line N, in ..."
        # followed by "ErrorType: message"
        lines = stderr.strip().split('\n')
        
        error_type = None
        line_number = None
        message = None

        # Find the last error trace
        for i, line in enumerate(reversed(lines)):
            if "Error:" in line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    error_type = parts[0].strip()
                    message = parts[1].strip()
                    
                    # Look for line number in preceding lines
                    for j in range(i + 1, len(lines)):
                        prev_line = lines[len(lines) - 1 - j]
                        match = re.search(r'File ".*", line (\d+)', prev_line)
                        if match:
                            line_number = int(match.group(1))
                            break
                    break
        
        return error_type, line_number, message

    def generate_patch(self, code: str, error_type: str, line_number: Optional[int], message: str) -> Tuple[Optional[str], str]:
        """
        Generates a patched version of the code based on the error.
        Returns (patched_code, strategy_name).
        """
        lines = code.split('\n')
        
        # If we have a line number, try heuristics
        if line_number is not None and 1 <= line_number <= len(lines):
            # 0-indexed line
            idx = line_number - 1
            original_line = lines[idx]

            # Commented out: Try-except heuristic is not ideal for IndexError
            # Let Ollama provide the proper fix instead
            # if error_type == "IndexError":
            #     if "range" in original_line and ("+ 1" in original_line or "len(" in original_line):
            #          return code.replace(original_line, original_line.replace("+ 1", "").replace("len(", "len(")), "Heuristic: Range Fix"
            #     
            #     indent = original_line[:len(original_line) - len(original_line.lstrip())]
            #     patch = f"{indent}try:\n{indent}    {original_line.strip()}\n{indent}except IndexError:\n{indent}    pass"
            #     lines[idx] = patch
            #     return '\n'.join(lines), "Heuristic: Try-Except Wrap"

            if error_type == "RecursionError":
                if "sys.setrecursionlimit" not in code:
                    return "import sys\nsys.setrecursionlimit(5000)\n" + code, "Heuristic: Increase Recursion Limit"
                pass

            elif error_type == "NameError":
                match = re.search(r"name '(.*)' is not defined", message)
                if match:
                    missing_var = match.group(1)
                    indent = original_line[:len(original_line) - len(original_line.lstrip())]
                    lines.insert(idx, f"{indent}{missing_var} = None")
                    return '\n'.join(lines), "Heuristic: Define Missing Var"

        # Fallback: Call Ollama
        print(f"Heuristics failed (or not applicable). Asking Ollama ({self.model})...")
        ollama_patch = self.call_ollama(code, error_type, line_number, message)
        if ollama_patch:
            return ollama_patch, f"Ollama ({self.model})"
        
        return None, "None"

    def call_ollama(self, code: str, error_type: str, line_number: Optional[int], message: str) -> Optional[str]:
        line_info = f"at line {line_number}" if line_number else "location unknown"
        prompt = f"""
You are a Python debugging assistant. Fix the following code to resolve the error.
Error: {error_type}: {message} {line_info}.

Code:
```python
{code}
```

Instructions:
1. Fix the logic error (e.g., infinite loop, invalid index).
2. Ensure the fix prevents the crash/timeout.
3. Return ONLY the full fixed code in a Python code block.
"""
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            response_text = result.get("response", "")
            
            # Extract code block
            match = re.search(r"```python\n(.*?)```", response_text, re.DOTALL)
            if match:
                return match.group(1).strip()
            
            # Fallback if no code block found, maybe the whole response is code?
            # But usually models chat. Let's try to find any code block.
            match = re.search(r"```\n(.*?)```", response_text, re.DOTALL)
            if match:
                return match.group(1).strip()
                
            return None
            
        except Exception as e:
            print(f"Ollama API call failed: {e}")
            return None

    def apply_patch(self, code: str, patch: str) -> str:
        # In this simple engine, generate_patch returns the full code.
        # So we just return the patch.
        return patch
