#!/usr/bin/env python3
"""
Example script showing how to use display_dependencies.py to read dependency data.
"""

import subprocess
import sys
import os

def run_display_command(args):
    """Run the display_dependencies.py script with given arguments."""
    cmd = [sys.executable, "display_dependencies.py"] + args
    print(f"Running: {' '.join(cmd)}")
    print("=" * 60)
    result = subprocess.run(cmd, capture_output=False, text=True)
    return result.returncode

def main():
    """Example usage of the display_dependencies script."""
    
    # Example 1: Display from a JSON file
    print("\n" + "=" * 60)
    print("Example 1: Reading from JSON file")
    print("=" * 60)
    run_display_command(["dependencies_20251005_124044.json"])
    
    # Example 2: Display only current version from a file
    print("\n" + "=" * 60)
    print("Example 2: Display only current version")
    print("=" * 60)
    run_display_command(["dependencies_20251005_124044.json", "--version", "current"])
    
    # Example 3: Display from a session ID
    print("\n" + "=" * 60)
    print("Example 3: Reading from session ID")
    print("=" * 60)
    run_display_command(["devin-092bcaf1c5544fa59f99ec0095eac782"])
    
    # Example 4: Display from a session URL
    print("\n" + "=" * 60)
    print("Example 4: Reading from session URL")
    print("=" * 60)
    run_display_command(["https://app.devin.ai/sessions/113720c6f0ab4145bf172b8c940e230a"])
    
    # Example 5: List available files
    print("\n" + "=" * 60)
    print("Example 5: List available dependency files")
    print("=" * 60)
    run_display_command(["--list"])


if __name__ == "__main__":
    # Check if an argument was passed
    if len(sys.argv) > 1:
        # Pass through to display_dependencies.py
        args = sys.argv[1:]
        run_display_command(args)
    else:
        # Show usage
        print("""
Usage examples:
    # Display from a file:
    python read_session_example.py dependencies_20251005_124044.json
    
    # Display from a session:
    python read_session_example.py devin-092bcaf1c5544fa59f99ec0095eac782
    
    # Display with options:
    python read_session_example.py dependencies_20251005_124044.json --version current
    
    # List available files:
    python read_session_example.py --list
    
    # Run all examples:
    python read_session_example.py demo
        """)
        
        if input("\nRun demo examples? (y/n): ").lower() == 'y':
            main()
