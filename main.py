import argparse
import sys
from src.controller import DebuggingController

def main():
    parser = argparse.ArgumentParser(description="Local AI-Supervised Autonomous Debugging Sandbox")
    parser.add_argument("script", help="Path to the broken Python script")
    parser.add_argument("--iterations", type=int, default=3, help="Maximum number of debugging iterations")
    parser.add_argument("--model", type=str, default="llama3", help="Ollama model to use (default: llama3)")
    parser.add_argument("--description", type=str, default=None, help="User description of expected behavior for logic repair")
    
    args = parser.parse_args()
    
    controller = DebuggingController(args.script, args.iterations, args.model, args.description)
    controller.run()

if __name__ == "__main__":
    main()
