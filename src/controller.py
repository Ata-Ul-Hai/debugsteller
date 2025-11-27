from .sandbox import Sandbox
from .patch_engine import PatchEngine
from .logger import DebugLogger
import os
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel

class DebuggingController:
    def __init__(self, script_path: str, max_iterations: int = 3, model: str = "llama3"):
        self.script_path = script_path
        self.max_iterations = max_iterations
        self.sandbox = Sandbox()
        self.patch_engine = PatchEngine(model=model)
        self.logger = DebugLogger()
        self.console = Console()

    def save_fixed_code(self, code: str):
        # Create fixed_tests directory if it doesn't exist
        fixed_dir = "fixed_tests"
        if not os.path.exists(fixed_dir):
            os.makedirs(fixed_dir)
            
        base = os.path.basename(self.script_path)
        name, ext = os.path.splitext(base)
        fixed_path = os.path.join(fixed_dir, f"{name}_fixed{ext}")
        
        try:
            with open(fixed_path, 'w') as f:
                f.write(code)
            
            self.console.print(Panel(f"[bold green]Success! Fixed code saved to {fixed_path}[/bold green]", title="File Saved"))
        except Exception as e:
            self.console.print(f"[bold red]Failed to save fixed code: {e}[/bold red]")

    def run(self):
        self.console.print(f"[bold blue]Starting debugging session for {self.script_path}...[/bold blue]")
        
        try:
            with open(self.script_path, 'r') as f:
                current_code = f.read()
        except FileNotFoundError:
            self.console.print(f"[bold red]Error: File {self.script_path} not found.[/bold red]")
            return

        self.logger.log_original_code(current_code)
        
        for i in range(1, self.max_iterations + 1):
            self.console.print(f"\n[bold yellow]--- Iteration {i} ---[/bold yellow]")
            
            # 1. Run
            result = self.sandbox.run(current_code)
            
            if result.return_code == 0:
                self.console.print(Panel("[bold green]Success! Code executed without errors.[/bold green]", title="Execution Result"))
                
                # Print the fixed code with syntax highlighting
                syntax = Syntax(current_code, "python", theme="monokai", line_numbers=True)
                self.console.print(syntax)
                
                self.logger.log_repaired_code(current_code)
                self.logger.set_best_attempt(current_code, "Success")
                self.logger.add_trace(i, "None", "Code ran successfully", "None", True)
                self.logger.save()
                self.save_fixed_code(current_code)
                return
            
            self.console.print(f"[red]Error detected (Return Code: {result.return_code})[/red]")
            
            if result.timed_out:
                self.console.print("[red]Execution timed out.[/red]")
                error_type = "TimeoutError"
                message = "Execution timed out (possible infinite loop)"
                line_number = None
            else:
                # 2. Observe & Analyze
                error_type, line_number, message = self.patch_engine.analyze_error(result.stderr)
            
            if not error_type:
                self.console.print("[red]Could not analyze error type from stderr.[/red]")
                self.logger.add_trace(i, "Unknown", "Could not parse stderr", "None", False)
                break
                
            self.console.print(f"Analyzed: [bold]{error_type}[/bold] at line {line_number}: {message}")
            
            # 3. Generate Patch
            patch, strategy = self.patch_engine.generate_patch(current_code, error_type, line_number, message)
            
            if not patch:
                self.console.print("[red]No patch generated.[/red]")
                self.logger.add_trace(i, f"{error_type}: {message}", "No patch strategy found", "None", False)
                break
            
            # 4. Apply Patch
            # In our simple engine, generate_patch returns the full new code
            new_code = patch
            
            # Log trace
            self.logger.add_trace(i, f"{error_type}: {message}", strategy, patch, False)
            
            # Update code for next iteration
            current_code = new_code
            
        self.console.print("\n[bold orange3]Max iterations reached. Running final verification...[/bold orange3]")
        # Final Run
        result = self.sandbox.run(current_code)
        if result.return_code == 0:
            self.console.print(Panel("[bold green]Success! Final patch worked.[/bold green]", title="Final Verification"))
            
            # Print the fixed code with syntax highlighting
            syntax = Syntax(current_code, "python", theme="monokai", line_numbers=True)
            self.console.print(syntax)
            
            self.logger.log_repaired_code(current_code)
            self.logger.set_best_attempt(current_code, "Success (Final)")
            self.logger.save()
            self.save_fixed_code(current_code)
            return

        self.console.print(f"[bold red]Final run failed (Return Code: {result.return_code}).[/bold red]")
        self.logger.set_best_attempt(current_code, "Max iterations reached & Final run failed")
        self.logger.save()
