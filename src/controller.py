from .sandbox import Sandbox
from .patch_engine import PatchEngine
from .logger import DebugLogger
import os
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel

class DebuggingController:
    def __init__(self, script_path: str, max_iterations: int = 3, model: str = "llama3", description: str = None):
        self.script_path = script_path
        self.max_iterations = max_iterations
        self.description = description
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
        
        success_code = None
        
        for i in range(1, self.max_iterations + 1):
            self.console.print(f"\n[bold yellow]--- Iteration {i} ---[/bold yellow]")
            
            # 1. Run
            result = self.sandbox.run(current_code)
            
            if result.return_code == 0:
                self.console.print(Panel("[bold green]Success! Code executed without errors.[/bold green]", title="Execution Result"))
                
                # Log success
                self.logger.log_repaired_code(current_code)
                self.logger.set_best_attempt(current_code, "Success")
                self.logger.add_trace(i, "None", "Code ran successfully", "None", True)
                success_code = current_code
                break # Exit loop to proceed to optimization
            
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
            new_code = patch
            self.logger.add_trace(i, f"{error_type}: {message}", strategy, patch, False)
            current_code = new_code
            
        else:
            # Loop finished without break (max iterations reached)
            self.console.print("\n[bold orange3]Max iterations reached. Running final verification...[/bold orange3]")
            result = self.sandbox.run(current_code)
            if result.return_code == 0:
                self.console.print(Panel("[bold green]Success! Final patch worked.[/bold green]", title="Final Verification"))
                self.logger.log_repaired_code(current_code)
                self.logger.set_best_attempt(current_code, "Success (Final)")
                success_code = current_code
            else:
                self.console.print(f"[bold red]Final run failed (Return Code: {result.return_code}).[/bold red]")
                self.logger.set_best_attempt(current_code, "Max iterations reached & Final run failed")
                self.logger.save()
                return

        # --- Logic Repair or Optimization Phase ---
        if success_code:
            # Check if user provided a description (Logic Repair Mode)
            if self.description:
                self.console.print("\n[bold cyan]--- Logic Repair Mode ---[/bold cyan]")
                self.console.print(f"User Description: {self.description}")
                
                repaired_code = self.patch_engine.get_logic_repair_prompt(success_code, self.description)
                
                if repaired_code:
                    self.console.print("Logic repair proposed. Testing...")
                    
                    # Test the repaired code
                    result = self.sandbox.run(repaired_code)
                    
                    if result.return_code == 0:
                        self.console.print(Panel("[bold green]Logic Repair Successful![/bold green]", title="Repair Success"))
                        self.logger.log_repaired_code(repaired_code)
                        self.logger.add_trace(self.max_iterations + 1, "Logic Repair", f"LLM Logic Repair: {self.description}", repaired_code, True, "Accepted")
                        self.save_fixed_code(repaired_code)
                    else:
                        self.console.print(Panel("[bold red]Logic Repair Failed.[/bold red]", title="Repair Failed"))
                        self.console.print(f"[red]Repaired code failed execution.[/red]")
                        self.logger.add_trace(self.max_iterations + 1, "Logic Repair", f"LLM Logic Repair: {self.description}", repaired_code, False, "Failed: Code did not execute")
                        self.logger.log_repaired_code(success_code)
                        self.save_fixed_code(success_code)
                else:
                    self.console.print("[yellow]Logic repair failed to generate valid output.[/yellow]")
                    self.save_fixed_code(success_code)
            else:
                # No description provided, proceed with Optimization Mode (existing logic)
                self.console.print("\n[bold magenta]--- Optimization Pass ---[/bold magenta]")
                opt_data = self.patch_engine.optimize_code(success_code)
                
                if opt_data and "optimized_code" in opt_data:
                    optimized_code = opt_data["optimized_code"]
                    self.console.print(f"Optimization proposed. Verifying...")
                    
                    # Verify Optimization
                    verified, reason = self.patch_engine.verify_optimization(success_code, optimized_code, self.sandbox)
                    
                    if verified:
                        self.console.print(Panel("[bold green]Optimization Verified![/bold green]", title="Optimization Success"))
                        self.console.print(f"Complexity: {opt_data.get('original_complexity')} -> {opt_data.get('optimized_complexity')}")
                        self.console.print(f"Changes: {', '.join(opt_data.get('changes_summary', []))}")
                        
                        # Save optimized code
                        self.logger.log_optimization(
                            opt_data.get('original_complexity'),
                            opt_data.get('optimized_complexity'),
                            opt_data.get('changes_summary'),
                            optimized_code
                        )
                        self.logger.log_repaired_code(optimized_code) # Update main repaired code to optimized version
                        self.logger.add_trace(self.max_iterations + 1, "Optimization", "LLM Optimization", optimized_code, True, "Accepted")
                        self.save_fixed_code(optimized_code)
                    else:
                        self.console.print(Panel("[bold red]Optimization Rejected.[/bold red]", title="Optimization Failed"))
                        self.console.print(f"[red]Reason: {reason}[/red]")
                        self.logger.add_trace(self.max_iterations + 1, "Optimization", "LLM Optimization", optimized_code, False, f"Rejected: {reason}")
                        self.logger.log_repaired_code(success_code)
                        self.save_fixed_code(success_code)
                else:
                    self.console.print("[yellow]Optimization failed to generate valid output.[/yellow]")
                    self.save_fixed_code(success_code)
        
        self.logger.save()
