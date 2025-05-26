#!/usr/bin/env python3
"""
Utility functions shared across multiple modules
"""
import os
import sys
import importlib.util
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Color formatting functions
def success(text): return f"{Fore.GREEN}{text}{Style.RESET_ALL}"
def error(text): return f"{Fore.RED}{text}{Style.RESET_ALL}"
def info(text): return f"{Fore.CYAN}{text}{Style.RESET_ALL}"
def warning(text): return f"{Fore.YELLOW}{text}{Style.RESET_ALL}"
def highlight(text): return f"{Fore.MAGENTA}{Style.BRIGHT}{text}{Style.RESET_ALL}"

def importFromFile(moduleName, filePath):
    """Import a module from a file path"""
    spec = importlib.util.spec_from_file_location(moduleName, filePath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module 