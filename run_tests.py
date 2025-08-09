#!/usr/bin/env python3
"""Test runner script for CRY-A-4MCP test suite."""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path
from typing import List, Dict, Optional
import json


class TestRunner:
    """Comprehensive test runner for CRY-A-4MCP."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.test_dir = project_root / "tests"
        self.coverage_dir = project_root / "coverage"
        self.reports_dir = project_root / "test_reports"
        
        # Ensure directories exist
        self.coverage_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
    
    def run_command(self, command: List[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
        """Run a command and return the result."""
        if cwd is None:
            cwd = self.project_root
        
        print(f"Running: {' '.join(command)}")
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        return result
    
    def install_dependencies(self) -> bool:
        """Install test dependencies."""
        print("Installing test dependencies...")
        
        dependencies = [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-xdist>=3.0.0",
            "pytest-html>=3.0.0",
            "pytest-json-report>=1.5.0",
            "pytest-mock>=3.10.0",
            "pytest-asyncio>=0.21.0",
            "factory-boy>=3.2.0",
            "faker>=18.0.0",
            "coverage>=7.0.0",
            "httpx>=0.24.0",
            "requests-mock>=1.10.0"
        ]
        
        for dep in dependencies:
            result = self.run_command([sys.executable, "-m", "pip", "install", dep])
            if result.returncode != 0:
                print(f"Failed to install {dep}")
                return False
        
        return True
    
    def run_unit_tests(self, verbose: bool = False, parallel: bool = False) -> bool:
        """Run unit tests."""
        print("\n" + "="*50)
        print("RUNNING UNIT TESTS")
        print("="*50)
        
        command = [
            sys.executable, "-m", "pytest",
            str(self.test_dir / "unit"),
            "--cov=src",
            f"--cov-report=html:{self.coverage_dir / 'unit'}",
            f"--cov-report=json:{self.coverage_dir / 'unit_coverage.json'}",
            "--cov-report=term-missing",
            f"--html={self.reports_dir / 'unit_tests.html'}",
            "--self-contained-html",
            f"--json-report={self.reports_dir / 'unit_tests.json'}"
        ]
        
        if verbose:
            command.append("-v")
        
        if parallel:
            command.extend(["-n", "auto"])
        
        result = self.run_command(command)
        return result.returncode == 0
    
    def run_integration_tests(self, verbose: bool = False) -> bool:
        """Run integration tests."""
        print("\n" + "="*50)
        print("RUNNING INTEGRATION TESTS")
        print("="*50)
        
        command = [
            sys.executable, "-m", "pytest",
            str(self.test_dir / "integration"),
            "--cov=src",
            "--cov-append",
            f"--cov-report=html:{self.coverage_dir / 'integration'}",
            f"--cov-report=json:{self.coverage_dir / 'integration_coverage.json'}",
            "--cov-report=term-missing",
            f"--html={self.reports_dir / 'integration_tests.html'}",
            "--self-contained-html",
            f"--json-report={self.reports_dir / 'integration_tests.json'}"
        ]
        
        if verbose:
            command.append("-v")
        
        result = self.run_command(command)
        return result.returncode == 0
    
    def run_e2e_tests(self, verbose: bool = False) -> bool:
        """Run end-to-end tests."""
        print("\n" + "="*50)
        print("RUNNING END-TO-END TESTS")
        print("="*50)
        
        command = [
            sys.executable, "-m", "pytest",
            str(self.test_dir / "e2e"),
            "--cov=src",
            "--cov-append",
            f"--cov-report=html:{self.coverage_dir / 'e2e'}",
            f"--cov-report=json:{self.coverage_dir / 'e2e_coverage.json'}",
            "--cov-report=term-missing",
            f"--html={self.reports_dir / 'e2e_tests.html'}",
            "--self-contained-html",
            f"--json-report={self.reports_dir / 'e2e_tests.json'}",
            "--tb=short"  # Shorter traceback for E2E tests
        ]
        
        if verbose:
            command.append("-v")
        
        result = self.run_command(command)
        return result.returncode == 0
    
    def run_performance_tests(self, verbose: bool = False) -> bool:
        """Run performance tests."""
        print("\n" + "="*50)
        print("RUNNING PERFORMANCE TESTS")
        print("="*50)
        
        command = [
            sys.executable, "-m", "pytest",
            str(self.test_dir / "performance"),
            "-m", "performance",
            f"--html={self.reports_dir / 'performance_tests.html'}",
            "--self-contained-html",
            f"--json-report={self.reports_dir / 'performance_tests.json'}",
            "--tb=short"
        ]
        
        if verbose:
            command.append("-v")
        
        result = self.run_command(command)
        return result.returncode == 0
    
    def run_security_tests(self, verbose: bool = False) -> bool:
        """Run security tests."""
        print("\n" + "="*50)
        print("RUNNING SECURITY TESTS")
        print("="*50)
        
        command = [
            sys.executable, "-m", "pytest",
            str(self.test_dir / "security"),
            "-m", "security",
            f"--html={self.reports_dir / 'security_tests.html'}",
            "--self-contained-html",
            f"--json-report={self.reports_dir / 'security_tests.json'}",
            "--tb=short"
        ]
        
        if verbose:
            command.append("-v")
        
        result = self.run_command(command)
        return result.returncode == 0
    
    def run_all_tests(self, verbose: bool = False, parallel: bool = False) -> bool:
        """Run all test suites."""
        print("\n" + "="*50)
        print("RUNNING ALL TESTS")
        print("="*50)
        
        command = [
            sys.executable, "-m", "pytest",
            str(self.test_dir),
            "--cov=src",
            f"--cov-report=html:{self.coverage_dir / 'all'}",
            f"--cov-report=json:{self.coverage_dir / 'all_coverage.json'}",
            "--cov-report=term-missing",
            f"--html={self.reports_dir / 'all_tests.html'}",
            "--self-contained-html",
            f"--json-report={self.reports_dir / 'all_tests.json'}"
        ]
        
        if verbose:
            command.append("-v")
        
        if parallel:
            command.extend(["-n", "auto"])
        
        result = self.run_command(command)
        return result.returncode == 0
    
    def generate_coverage_report(self) -> None:
        """Generate comprehensive coverage report."""
        print("\n" + "="*50)
        print("GENERATING COVERAGE REPORT")
        print("="*50)
        
        # Combine coverage data
        command = [
            sys.executable, "-m", "coverage",
            "combine"
        ]
        self.run_command(command)
        
        # Generate HTML report
        command = [
            sys.executable, "-m", "coverage",
            "html",
            "-d", str(self.coverage_dir / "combined")
        ]
        self.run_command(command)
        
        # Generate JSON report
        command = [
            sys.executable, "-m", "coverage",
            "json",
            "-o", str(self.coverage_dir / "combined_coverage.json")
        ]
        self.run_command(command)
        
        # Generate text report
        command = [
            sys.executable, "-m", "coverage",
            "report",
            "--show-missing"
        ]
        result = self.run_command(command)
        
        # Save text report
        with open(self.coverage_dir / "coverage_report.txt", "w") as f:
            f.write(result.stdout)
    
    def analyze_test_results(self) -> Dict:
        """Analyze test results and generate summary."""
        print("\n" + "="*50)
        print("ANALYZING TEST RESULTS")
        print("="*50)
        
        summary = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_suites": {},
            "coverage": {},
            "overall_status": "unknown"
        }
        
        # Analyze test reports
        test_files = {
            "unit": self.reports_dir / "unit_tests.json",
            "integration": self.reports_dir / "integration_tests.json",
            "e2e": self.reports_dir / "e2e_tests.json",
            "performance": self.reports_dir / "performance_tests.json",
            "security": self.reports_dir / "security_tests.json",
            "all": self.reports_dir / "all_tests.json"
        }
        
        for suite_name, report_file in test_files.items():
            if report_file.exists():
                try:
                    with open(report_file) as f:
                        data = json.load(f)
                    
                    summary["test_suites"][suite_name] = {
                        "total": data.get("summary", {}).get("total", 0),
                        "passed": data.get("summary", {}).get("passed", 0),
                        "failed": data.get("summary", {}).get("failed", 0),
                        "skipped": data.get("summary", {}).get("skipped", 0),
                        "duration": data.get("duration", 0)
                    }
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Error reading {report_file}: {e}")
        
        # Analyze coverage reports
        coverage_files = {
            "unit": self.coverage_dir / "unit_coverage.json",
            "integration": self.coverage_dir / "integration_coverage.json",
            "e2e": self.coverage_dir / "e2e_coverage.json",
            "combined": self.coverage_dir / "combined_coverage.json"
        }
        
        for suite_name, coverage_file in coverage_files.items():
            if coverage_file.exists():
                try:
                    with open(coverage_file) as f:
                        data = json.load(f)
                    
                    summary["coverage"][suite_name] = {
                        "line_coverage": data.get("totals", {}).get("percent_covered", 0),
                        "branch_coverage": data.get("totals", {}).get("percent_covered_display", "0%"),
                        "missing_lines": data.get("totals", {}).get("missing_lines", 0)
                    }
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Error reading {coverage_file}: {e}")
        
        # Determine overall status
        total_failed = sum(
            suite.get("failed", 0) 
            for suite in summary["test_suites"].values()
        )
        
        if total_failed == 0:
            summary["overall_status"] = "passed"
        else:
            summary["overall_status"] = "failed"
        
        # Save summary
        with open(self.reports_dir / "test_summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        return summary
    
    def print_summary(self, summary: Dict) -> None:
        """Print test summary to console."""
        print("\n" + "="*50)
        print("TEST EXECUTION SUMMARY")
        print("="*50)
        
        print(f"Timestamp: {summary['timestamp']}")
        print(f"Overall Status: {summary['overall_status'].upper()}")
        
        print("\nTest Suites:")
        for suite_name, suite_data in summary["test_suites"].items():
            print(f"  {suite_name.capitalize()}:")
            print(f"    Total: {suite_data['total']}")
            print(f"    Passed: {suite_data['passed']}")
            print(f"    Failed: {suite_data['failed']}")
            print(f"    Skipped: {suite_data['skipped']}")
            print(f"    Duration: {suite_data['duration']:.2f}s")
        
        print("\nCoverage:")
        for suite_name, coverage_data in summary["coverage"].items():
            print(f"  {suite_name.capitalize()}: {coverage_data['line_coverage']:.1f}%")
        
        print(f"\nReports saved to: {self.reports_dir}")
        print(f"Coverage reports saved to: {self.coverage_dir}")
    
    def run_linting(self) -> bool:
        """Run code linting checks."""
        print("\n" + "="*50)
        print("RUNNING LINTING CHECKS")
        print("="*50)
        
        # Run black
        print("Running black...")
        result = self.run_command([
            sys.executable, "-m", "black", 
            "--check", "--diff", "src", "tests"
        ])
        black_passed = result.returncode == 0
        
        # Run ruff
        print("Running ruff...")
        result = self.run_command([
            sys.executable, "-m", "ruff", 
            "check", "src", "tests"
        ])
        ruff_passed = result.returncode == 0
        
        # Run mypy
        print("Running mypy...")
        result = self.run_command([
            sys.executable, "-m", "mypy", 
            "src", "--ignore-missing-imports"
        ])
        mypy_passed = result.returncode == 0
        
        return black_passed and ruff_passed and mypy_passed


def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(description="CRY-A-4MCP Test Runner")
    parser.add_argument(
        "--suite", 
        choices=["unit", "integration", "e2e", "performance", "security", "all"],
        default="all",
        help="Test suite to run"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--parallel", "-p", 
        action="store_true",
        help="Run tests in parallel"
    )
    parser.add_argument(
        "--install-deps", 
        action="store_true",
        help="Install test dependencies"
    )
    parser.add_argument(
        "--lint", 
        action="store_true",
        help="Run linting checks"
    )
    parser.add_argument(
        "--no-coverage", 
        action="store_true",
        help="Skip coverage report generation"
    )
    
    args = parser.parse_args()
    
    # Initialize test runner
    project_root = Path(__file__).parent
    runner = TestRunner(project_root)
    
    # Install dependencies if requested
    if args.install_deps:
        if not runner.install_dependencies():
            print("Failed to install dependencies")
            sys.exit(1)
    
    # Run linting if requested
    if args.lint:
        if not runner.run_linting():
            print("Linting checks failed")
            sys.exit(1)
    
    # Run tests
    success = True
    
    if args.suite == "unit":
        success = runner.run_unit_tests(args.verbose, args.parallel)
    elif args.suite == "integration":
        success = runner.run_integration_tests(args.verbose)
    elif args.suite == "e2e":
        success = runner.run_e2e_tests(args.verbose)
    elif args.suite == "performance":
        success = runner.run_performance_tests(args.verbose)
    elif args.suite == "security":
        success = runner.run_security_tests(args.verbose)
    elif args.suite == "all":
        success = runner.run_all_tests(args.verbose, args.parallel)
    
    # Generate coverage report
    if not args.no_coverage:
        runner.generate_coverage_report()
    
    # Analyze and print results
    summary = runner.analyze_test_results()
    runner.print_summary(summary)
    
    # Exit with appropriate code
    if success and summary["overall_status"] == "passed":
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()