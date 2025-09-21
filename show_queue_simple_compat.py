#!/usr/bin/env python3
"""
Backward compatibility wrapper for show_queue_simple.py
This file maintains compatibility while redirecting to the new queue_manager.py
"""
import sys
import subprocess

if __name__ == "__main__":
    print("📢 This script has been consolidated into queue_manager.py")
    print("   Running: python queue_manager.py simple")
    print("   For more options: python queue_manager.py --help")
    print()
    
    # Run the new consolidated command
    sys.exit(subprocess.call([sys.executable, "queue_manager.py", "simple"]))