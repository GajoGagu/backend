#!/usr/bin/env python3
"""
Test runner script for the CRUD API.
This script provides convenient ways to run different types of tests.
"""

import subprocess
import sys
import argparse
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, check=True, capture_output=False)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Run tests for the CRUD API")
    parser.add_argument(
        "--type",
        choices=["all", "unit", "integration", "auth", "products", "cart", "orders", "wishlist", "health", "users", "categories"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run tests with coverage report"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Run tests in verbose mode"
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Skip slow tests"
    )
    
    args = parser.parse_args()
    
    # Base pytest command
    base_cmd = ["python", "-m", "pytest"]
    
    # Add verbosity
    if args.verbose:
        base_cmd.append("-v")
    
    # Add coverage
    if args.coverage:
        base_cmd.extend(["--cov=.", "--cov-report=term-missing", "--cov-report=html:htmlcov"])
    
    # Skip slow tests
    if args.fast:
        base_cmd.extend(["-m", "not slow"])
    
    # Determine test path based on type
    if args.type == "all":
        test_path = "tests/"
    elif args.type == "unit":
        test_path = "tests/"
        base_cmd.extend(["-m", "unit"])
    elif args.type == "integration":
        test_path = "tests/test_integration.py"
        base_cmd.extend(["-m", "integration"])
    else:
        test_path = f"tests/test_{args.type}.py"
    
    base_cmd.append(test_path)
    
    # Run the tests
    success = run_command(base_cmd, f"{args.type.title()} tests")
    
    if success:
        print(f"\n🎉 All {args.type} tests passed!")
        if args.coverage:
            print("📊 Coverage report generated in htmlcov/index.html")
    else:
        print(f"\n💥 {args.type.title()} tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
