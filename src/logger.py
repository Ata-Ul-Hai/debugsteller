import json
import time
from typing import List, Dict, Any
from dataclasses import dataclass, asdict

@dataclass
class RepairTrace:
    iteration: int
    error_detected: str
    reasoning: str
    raw_patch: str
    success: bool

class DebugLogger:
    def __init__(self, log_file: str = "debug_report.json"):
        self.log_file = log_file
        self.report = {
            "original_code": "",
            "repaired_code": "",
            "traces": [],
            "best_attempt": "",
            "failure_explanation": "",
            "optimization_report": None
        }

    def log_original_code(self, code: str):
        self.report["original_code"] = code

    def log_repaired_code(self, code: str):
        self.report["repaired_code"] = code

    def log_optimization(self, original_complexity: str, optimized_complexity: str, changes: list, optimized_code: str):
        self.report["optimization_report"] = {
            "original_complexity": original_complexity,
            "optimized_complexity": optimized_complexity,
            "changes_summary": changes,
            "optimized_code": optimized_code
        }

    def add_trace(self, iteration: int, error_type: str, strategy: str, patch: str, success: bool, status: str = "Attempted"):
        trace = {
            "iteration": iteration,
            "error_type": error_type,
            "strategy": strategy,
            "patch": patch,
            "success": success,
            "status": status
        }
        self.report["traces"].append(trace)

    def set_best_attempt(self, code: str, explanation: str):
        self.report["best_attempt"] = code
        self.report["failure_explanation"] = explanation

    def save(self):
        self.report["timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "w") as f:
            json.dump(self.report, f, indent=4)
        print(f"Debug report saved to {self.log_file}")
