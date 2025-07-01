#!/usr/bin/env python3
"""
Test runner script for OpenAlex MCP Server.

This script provides a convenient way to run tests with different configurations.
"""

import argparse
import os
import subprocess
import sys


def run_command(cmd, description=""):
    """Run a command and return its exit code."""
    if description:
        print(f"\n🔄 {description}")
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode == 0:
        print(f"✅ Success: {description or 'Command completed'}")
    else:
        print(f"❌ Failed: {description or 'Command failed'}")
    
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="Run tests for OpenAlex MCP Server")
    parser.add_argument(
        "--type", 
        choices=["all", "unit", "integration", "coverage"],
        default="unit",
        help="Type of tests to run (default: unit)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Run tests in verbose mode"
    )
    parser.add_argument(
        "--install-deps",
        action="store_true",
        help="Install test dependencies before running tests"
    )
    parser.add_argument(
        "--lint",
        action="store_true",
        help="Run linting checks before tests"
    )
    parser.add_argument(
        "--format",
        action="store_true",
        help="Format code before running tests"
    )
    
    args = parser.parse_args()
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    exit_code = 0
    
    # Install dependencies if requested
    if args.install_deps:
        exit_code = run_command(
            [sys.executable, "-m", "pip", "install", "-e", ".[dev,test]"],
            "Installing development dependencies"
        )
        if exit_code != 0:
            return exit_code
    
    # Format code if requested
    if args.format:
        run_command(
            [sys.executable, "-m", "black", "src/", "tests/"],
            "Formatting code with black"
        )
        run_command(
            [sys.executable, "-m", "ruff", "check", "--fix", "src/", "tests/"],
            "Fixing code with ruff"
        )
    
    # Run linting if requested
    if args.lint:
        exit_code = run_command(
            [sys.executable, "-m", "ruff", "check", "src/", "tests/"],
            "Running ruff linting"
        )
        if exit_code != 0:
            return exit_code
        
        exit_code = run_command(
            [sys.executable, "-m", "black", "--check", "src/", "tests/"],
            "Checking code formatting"
        )
        if exit_code != 0:
            return exit_code
    
    # Build pytest command
    pytest_cmd = [sys.executable, "-m", "pytest"]
    
    if args.verbose:
        pytest_cmd.append("-v")
    
    # Set test type
    if args.type == "unit":
        pytest_cmd.extend(["-m", "not integration and not slow"])
        description = "Running unit tests"
    elif args.type == "integration":
        pytest_cmd.extend(["-m", "integration or slow"])
        description = "Running integration tests"
    elif args.type == "coverage":
        pytest_cmd.extend([
            "--cov=src/openalex_mcp",
            "--cov-report=term-missing",
            "--cov-report=html",
            "-m", "not integration and not slow"
        ])
        description = "Running tests with coverage"
    else:  # all
        description = "Running all tests"
    
    # Run tests
    exit_code = run_command(pytest_cmd, description)
    
    if args.type == "coverage" and exit_code == 0:
        print("\n📊 Coverage report generated in htmlcov/index.html")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())