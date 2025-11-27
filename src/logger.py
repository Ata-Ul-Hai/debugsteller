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
        self.original_code: str = ""
        self.repaired_code: str = ""
        self.traces: List[RepairTrace] = []
        self.best_attempt: str = ""
        self.failure_explanation: str = ""

    def log_original_code(self, code: str):
        self.original_code = code

    def log_repaired_code(self, code: str):
        self.repaired_code = code

    def add_trace(self, iteration: int, error: str, reasoning: str, patch: str, success: bool):
        trace = RepairTrace(
            iteration=iteration,
            error_detected=error,
            reasoning=reasoning,
            raw_patch=patch,
            success=success
        )
        self.traces.append(trace)

    def set_best_attempt(self, code: str, explanation: str):
        self.best_attempt = code
        self.failure_explanation = explanation

    def save(self):
        data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "original_code": self.original_code,
            "repaired_code": self.repaired_code,
            "traces": [asdict(t) for t in self.traces],
            "best_attempt": self.best_attempt,
            "failure_explanation": self.failure_explanation
        }
        with open(self.log_file, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Debug report saved to {self.log_file}")
