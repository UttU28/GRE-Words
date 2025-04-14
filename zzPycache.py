#!/usr/bin/env python3
import os
import shutil
import sys
from pathlib import Path

def clean_pycache(root_dir="."):
    """Remove all __pycache__ directories and .pyc files from the project"""
    root_path = Path(root_dir).resolve()
    print(f"Cleaning pycache files from: {root_path}")
    
    # Counter for deleted items
    dirs_removed = 0
    files_removed = 0
    
    # Find and delete __pycache__ directories
    for path in root_path.glob("**/__pycache__"):
        if path.is_dir():
            print(f"Removing directory: {path}")
            shutil.rmtree(path)
            dirs_removed += 1
    
    # Find and delete .pyc files
    for path in root_path.glob("**/*.pyc"):
        if path.is_file():
            print(f"Removing file: {path}")
            path.unlink()
            files_removed += 1
    
    print(f"Cleanup complete: {dirs_removed} __pycache__ directories and {files_removed} .pyc files removed")

if __name__ == "__main__":
    # Use command line argument as root directory if provided, otherwise use current directory
    root_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    clean_pycache(root_dir) 