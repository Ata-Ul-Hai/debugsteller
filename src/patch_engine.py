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
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            response_json = response.json()
            
            # Extract the code block from the response
            full_response = response_json.get('response', '')
            match = re.search(r"```python\n(.*?)```", full_response, re.DOTALL)
            if match:
                return match.group(1).strip()
            else:
                # Fallback: if no code block, maybe the whole response is code?
                # But usually models chat. Let's return None if strict parsing fails.
                return None
                
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return None

    def get_logic_repair_prompt(self, code: str, user_description: str) -> Optional[str]:
        """
        Generates a logic repair for code that runs but produces wrong output.
        Uses user description to guide the fix.
        """
        prompt = f"""
You are a Python debugging assistant. The code runs successfully (exit code 0), but the user reports a logic error.

User Description: {user_description}

Code:
```python
{code}
```

Instructions:
1. Analyze the logic error based on the user's description.
2. Fix the logic to satisfy the user's requirement.
3. Preserve all functional code structure.
4. Return ONLY the full fixed code in a Python code block.
"""
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            response_json = response.json()
            
            # Extract the code block from the response
            full_response = response_json.get('response', '')
            match = re.search(r"```python\n(.*?)```", full_response, re.DOTALL)
            if match:
                return match.group(1).strip()
            else:
                return None
                
        except Exception as e:
            print(f"Error calling Ollama for logic repair: {e}")
            return None

    def verify_optimization(self, original_code: str, optimized_code: str, sandbox) -> Tuple[bool, str]:
        """
        Verifies that the optimized code produces the exact same stdout as the original code.
        Returns (success, reason).
        """
        print("Verifying optimization consistency...")
        
        # Run original
        orig_result = sandbox.run(original_code)
        if orig_result.return_code != 0:
            return False, f"Original code failed during verification: {orig_result.stderr}"
            
        # Run optimized
        opt_result = sandbox.run(optimized_code)
        if opt_result.return_code != 0:
            return False, f"Optimized code failed execution: {opt_result.stderr}"
            
        # Compare stdout
        if orig_result.stdout != opt_result.stdout:
            return False, "Output mismatch: Optimized code produced different stdout."
            
        return True, "Verification successful."

    def optimize_code(self, code: str) -> Optional[dict]:
        """
        Analyzes and optimizes the code. Returns a dict with:
        - optimized_code
        - original_complexity
        - optimized_complexity
        - changes_summary (list)
        """
        prompt = f"""
TASK: **CODE OPTIMIZATION AND DOCUMENTATION**
ROLE: You are a Senior Python Architect specializing in performance and code quality.
GOAL: Optimize the provided Python code for efficiency (Time/Memory), readability, and compliance with PEP 8 standards.

CONSTRAINTS:
1.  **CRITICAL LOGIC:** The functional behavior and console output must remain EXACTLY the same.
2.  **Optimization:** Focus on improving algorithmic complexity (e.g., O(N^2) -> O(N)).
3.  **Documentation:** Add a descriptive **docstring** (Google style) to every function.
4.  **EDUCATIONAL COMMENTING:** Add comments starting with `## EDUCATIONAL:` specifically explaining the Big O complexity change (e.g., `# ## EDUCATIONAL: Replaced list loop (O(n)) with set lookup (O(1)) for speed.`).
5.  **Output Format:** Return the response in the specified JSON format below.

Code:
```python
{code}
```

Return your response in this EXACT JSON format (no markdown around the JSON):
{{
    "original_complexity": "Estimated Big O",
    "optimized_complexity": "Estimated Big O",
    "changes_summary": ["Change 1", "Change 2"],
    "optimized_code": "FULL PYTHON CODE HERE"
}}
"""
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        
        try:
            print(f"Running optimization pass with {self.model}...")
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            response_json = response.json()
            full_response = response_json.get('response', '')
            
            # Parse JSON from response
            try:
                data = json.loads(full_response)
                return data
            except json.JSONDecodeError:
                # Try to find JSON block
                match = re.search(r"\{.*\}", full_response, re.DOTALL)
                if match:
                    return json.loads(match.group(0))
                print("Failed to parse JSON from optimization response.")
                return None
                
        except Exception as e:
            print(f"Error during optimization: {e}")
            return None

    def apply_patch(self, code: str, patch: str) -> str:
        # In this simple engine, generate_patch returns the full code.
        # So we just return the patch.
        return patch
