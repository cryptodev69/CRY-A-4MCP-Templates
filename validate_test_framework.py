#!/usr/bin/env python3
"""
CRY-A-4MCP Test Framework Validation Script

This script validates the entire testing framework setup and ensures all components
are properly configured and functional.

Usage:
    python validate_test_framework.py [--verbose] [--fix-issues]

Features:
    - Validates test file structure
    - Checks pytest configuration
    - Verifies test dependencies
    - Validates test data factories
    - Checks CI/CD configuration
    - Generates validation report
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
import importlib.util
from datetime import datetime


class TestFrameworkValidator:
    """Validates the CRY-A-4MCP testing framework setup."""
    
    def __init__(self, project_root: Path, verbose: bool = False, fix_issues: bool = False):
        self.project_root = project_root
        self.verbose = verbose
        self.fix_issues = fix_issues
        self.issues = []
        self.warnings = []
        self.successes = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log a message with appropriate formatting."""
        if self.verbose or level in ["ERROR", "WARNING", "SUCCESS"]:
            prefix = {
                "INFO": "ℹ️",
                "SUCCESS": "✅",
                "WARNING": "⚠️",
                "ERROR": "❌",
                "DEBUG": "🔍"
            }.get(level, "📝")
            print(f"{prefix} {message}")
    
    def add_issue(self, message: str, fix_suggestion: str = None):
        """Add an issue to the validation report."""
        issue = {"message": message, "fix_suggestion": fix_suggestion}
        self.issues.append(issue)
        self.log(message, "ERROR")
        if fix_suggestion:
            self.log(f"   💡 Fix: {fix_suggestion}", "INFO")
    
    def add_warning(self, message: str, suggestion: str = None):
        """Add a warning to the validation report."""
        warning = {"message": message, "suggestion": suggestion}
        self.warnings.append(warning)
        self.log(message, "WARNING")
        if suggestion:
            self.log(f"   💡 Suggestion: {suggestion}", "INFO")
    
    def add_success(self, message: str):
        """Add a success to the validation report."""
        self.successes.append(message)
        self.log(message, "SUCCESS")
    
    def validate_directory_structure(self) -> bool:
        """Validate the test directory structure."""
        self.log("Validating test directory structure...", "INFO")
        
        required_dirs = [
            "tests",
            "tests/unit",
            "tests/integration",
            "tests/e2e",
            "tests/performance",
            "tests/security",
            "tests/fixtures"
        ]
        
        all_valid = True
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists():
                self.add_success(f"Directory exists: {dir_path}")
            else:
                self.add_issue(
                    f"Missing directory: {dir_path}",
                    f"Create directory: mkdir -p {full_path}"
                )
                all_valid = False
                
                if self.fix_issues:
                    full_path.mkdir(parents=True, exist_ok=True)
                    self.log(f"Created directory: {dir_path}", "INFO")
        
        return all_valid
    
    def validate_required_files(self) -> bool:
        """Validate required test framework files."""
        self.log("Validating required files...", "INFO")
        
        required_files = {
            "tests/conftest.py": "Pytest configuration and fixtures",
            "tests/factories.py": "Test data factories",
            "pytest.ini": "Pytest configuration",
            "run_tests.py": "Test runner script",
            "Makefile": "Build and test commands",
            "TESTING_README.md": "Testing documentation",
            "tests/TEST_INDEX.md": "Test suite index"
        }
        
        all_valid = True
        for file_path, description in required_files.items():
            full_path = self.project_root / file_path
            if full_path.exists():
                self.add_success(f"File exists: {file_path} ({description})")
            else:
                self.add_issue(
                    f"Missing file: {file_path} ({description})",
                    f"Create the required file: {file_path}"
                )
                all_valid = False
        
        return all_valid
    
    def validate_pytest_configuration(self) -> bool:
        """Validate pytest configuration."""
        self.log("Validating pytest configuration...", "INFO")
        
        pytest_ini = self.project_root / "pytest.ini"
        if not pytest_ini.exists():
            self.add_issue("pytest.ini not found", "Create pytest.ini configuration file")
            return False
        
        try:
            content = pytest_ini.read_text()
            
            # Check for required sections
            required_sections = [
                "[tool:pytest]",
                "testpaths",
                "python_files",
                "markers"
            ]
            
            for section in required_sections:
                if section in content:
                    self.add_success(f"pytest.ini contains: {section}")
                else:
                    self.add_warning(
                        f"pytest.ini missing: {section}",
                        f"Add {section} to pytest.ini"
                    )
            
            # Check for test markers
            expected_markers = [
                "unit", "integration", "e2e", "performance", "security",
                "fast", "slow", "smoke", "regression", "critical"
            ]
            
            for marker in expected_markers:
                if marker in content:
                    self.log(f"Found marker: {marker}", "DEBUG")
                else:
                    self.add_warning(
                        f"Missing test marker: {marker}",
                        f"Add marker definition for {marker}"
                    )
            
            return True
            
        except Exception as e:
            self.add_issue(f"Error reading pytest.ini: {e}", "Check file permissions and format")
            return False
    
    def validate_test_dependencies(self) -> bool:
        """Validate test dependencies are installed."""
        self.log("Validating test dependencies...", "INFO")
        
        required_packages = [
            "pytest",
            "pytest-cov",
            "pytest-xdist",
            "pytest-asyncio",
            "factory-boy",
            "faker",
            "httpx",
            "fastapi",
            "pydantic"
        ]
        
        all_installed = True
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                self.add_success(f"Package installed: {package}")
            except ImportError:
                self.add_issue(
                    f"Missing package: {package}",
                    f"Install with: pip install {package}"
                )
                all_installed = False
        
        return all_installed
    
    def validate_test_factories(self) -> bool:
        """Validate test data factories."""
        self.log("Validating test factories...", "INFO")
        
        factories_file = self.project_root / "tests" / "factories.py"
        if not factories_file.exists():
            self.add_issue("factories.py not found", "Create test data factories file")
            return False
        
        try:
            # Try to import the factories module
            spec = importlib.util.spec_from_file_location("factories", factories_file)
            factories_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(factories_module)
            
            # Check for expected factories
            expected_factories = [
                "URLConfigurationFactory",
                "StrategyFactory",
                "CrawlerDataFactory",
                "UserFactory",
                "APIKeyFactory",
                "WebhookFactory",
                "AlertFactory",
                "PerformanceMetricFactory"
            ]
            
            for factory_name in expected_factories:
                if hasattr(factories_module, factory_name):
                    self.add_success(f"Factory available: {factory_name}")
                else:
                    self.add_warning(
                        f"Missing factory: {factory_name}",
                        f"Implement {factory_name} in factories.py"
                    )
            
            return True
            
        except Exception as e:
            self.add_issue(f"Error importing factories: {e}", "Check factories.py syntax")
            return False
    
    def validate_test_files(self) -> bool:
        """Validate existing test files."""
        self.log("Validating test files...", "INFO")
        
        test_dirs = ["unit", "integration", "e2e", "performance", "security"]
        total_tests = 0
        
        for test_dir in test_dirs:
            test_path = self.project_root / "tests" / test_dir
            if test_path.exists():
                test_files = list(test_path.glob("test_*.py"))
                total_tests += len(test_files)
                
                if test_files:
                    self.add_success(f"Found {len(test_files)} test files in {test_dir}/")
                    for test_file in test_files:
                        self.log(f"  - {test_file.name}", "DEBUG")
                else:
                    self.add_warning(
                        f"No test files in {test_dir}/",
                        f"Add test files to tests/{test_dir}/"
                    )
        
        if total_tests > 0:
            self.add_success(f"Total test files found: {total_tests}")
        else:
            self.add_issue("No test files found", "Create test files in appropriate directories")
        
        return total_tests > 0
    
    def validate_ci_configuration(self) -> bool:
        """Validate CI/CD configuration."""
        self.log("Validating CI/CD configuration...", "INFO")
        
        ci_file = self.project_root / ".github" / "workflows" / "ci.yml"
        if ci_file.exists():
            self.add_success("GitHub Actions CI configuration found")
            
            try:
                content = ci_file.read_text()
                
                # Check for test jobs
                expected_jobs = ["unit-tests", "integration-tests", "security-tests"]
                for job in expected_jobs:
                    if job in content:
                        self.add_success(f"CI job configured: {job}")
                    else:
                        self.add_warning(
                            f"Missing CI job: {job}",
                            f"Add {job} job to CI configuration"
                        )
                
                return True
                
            except Exception as e:
                self.add_issue(f"Error reading CI configuration: {e}")
                return False
        else:
            self.add_warning(
                "No GitHub Actions CI configuration found",
                "Create .github/workflows/ci.yml"
            )
            return False
    
    def run_test_discovery(self) -> bool:
        """Run pytest test discovery to validate test structure."""
        self.log("Running test discovery...", "INFO")
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "--collect-only", "-q"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Count discovered tests
                lines = result.stdout.strip().split('\n')
                test_count = 0
                for line in lines:
                    if "test session starts" in line or "collected" in line:
                        continue
                    if line.strip() and not line.startswith("="):
                        test_count += 1
                
                self.add_success(f"Test discovery successful - {test_count} tests found")
                return True
            else:
                self.add_issue(
                    f"Test discovery failed: {result.stderr}",
                    "Check test file syntax and imports"
                )
                return False
                
        except subprocess.TimeoutExpired:
            self.add_issue("Test discovery timed out", "Check for infinite loops in test imports")
            return False
        except Exception as e:
            self.add_issue(f"Error running test discovery: {e}")
            return False
    
    def validate_makefile_targets(self) -> bool:
        """Validate Makefile test targets."""
        self.log("Validating Makefile targets...", "INFO")
        
        makefile = self.project_root / "Makefile"
        if not makefile.exists():
            self.add_warning("Makefile not found", "Create Makefile with test targets")
            return False
        
        try:
            content = makefile.read_text()
            
            expected_targets = [
                "test", "test-unit", "test-integration", "test-e2e",
                "test-performance", "test-security", "coverage"
            ]
            
            for target in expected_targets:
                if f"{target}:" in content:
                    self.add_success(f"Makefile target found: {target}")
                else:
                    self.add_warning(
                        f"Missing Makefile target: {target}",
                        f"Add {target} target to Makefile"
                    )
            
            return True
            
        except Exception as e:
            self.add_issue(f"Error reading Makefile: {e}")
            return False
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive validation report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "summary": {
                "total_checks": len(self.successes) + len(self.warnings) + len(self.issues),
                "successes": len(self.successes),
                "warnings": len(self.warnings),
                "issues": len(self.issues),
                "overall_status": "PASS" if len(self.issues) == 0 else "FAIL"
            },
            "successes": self.successes,
            "warnings": self.warnings,
            "issues": self.issues,
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        if len(self.issues) > 0:
            recommendations.append("Fix all critical issues before proceeding with testing")
        
        if len(self.warnings) > 5:
            recommendations.append("Address warnings to improve test framework completeness")
        
        # Specific recommendations based on issues
        issue_messages = [issue["message"] for issue in self.issues]
        
        if any("Missing directory" in msg for msg in issue_messages):
            recommendations.append("Run with --fix-issues to automatically create missing directories")
        
        if any("Missing package" in msg for msg in issue_messages):
            recommendations.append("Install missing dependencies: pip install -e '.[dev,test]'")
        
        if any("test files" in msg for msg in issue_messages):
            recommendations.append("Create test files for core functionality")
        
        if not recommendations:
            recommendations.append("Test framework validation passed - ready for testing!")
        
        return recommendations
    
    def validate_all(self) -> bool:
        """Run all validation checks."""
        self.log("🚀 Starting CRY-A-4MCP Test Framework Validation", "INFO")
        self.log(f"Project root: {self.project_root}", "INFO")
        
        validation_steps = [
            ("Directory Structure", self.validate_directory_structure),
            ("Required Files", self.validate_required_files),
            ("Pytest Configuration", self.validate_pytest_configuration),
            ("Test Dependencies", self.validate_test_dependencies),
            ("Test Factories", self.validate_test_factories),
            ("Test Files", self.validate_test_files),
            ("CI Configuration", self.validate_ci_configuration),
            ("Test Discovery", self.run_test_discovery),
            ("Makefile Targets", self.validate_makefile_targets)
        ]
        
        all_passed = True
        for step_name, step_func in validation_steps:
            self.log(f"\n--- {step_name} ---", "INFO")
            try:
                result = step_func()
                if not result:
                    all_passed = False
            except Exception as e:
                self.add_issue(f"Validation step '{step_name}' failed: {e}")
                all_passed = False
        
        return all_passed


def main():
    """Main entry point for the validation script."""
    parser = argparse.ArgumentParser(
        description="Validate CRY-A-4MCP Test Framework Setup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate_test_framework.py
  python validate_test_framework.py --verbose
  python validate_test_framework.py --fix-issues
  python validate_test_framework.py --verbose --fix-issues
        """
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--fix-issues",
        action="store_true",
        help="Automatically fix issues where possible"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output validation report to file (JSON format)"
    )
    
    args = parser.parse_args()
    
    # Determine project root
    project_root = Path.cwd()
    if not (project_root / "tests").exists() and (project_root.parent / "tests").exists():
        project_root = project_root.parent
    
    # Run validation
    validator = TestFrameworkValidator(
        project_root=project_root,
        verbose=args.verbose,
        fix_issues=args.fix_issues
    )
    
    success = validator.validate_all()
    
    # Generate and display report
    report = validator.generate_report()
    
    print("\n" + "="*60)
    print("📊 VALIDATION REPORT")
    print("="*60)
    print(f"Overall Status: {'✅ PASS' if success else '❌ FAIL'}")
    print(f"Total Checks: {report['summary']['total_checks']}")
    print(f"Successes: {report['summary']['successes']}")
    print(f"Warnings: {report['summary']['warnings']}")
    print(f"Issues: {report['summary']['issues']}")
    
    if report['recommendations']:
        print("\n📋 RECOMMENDATIONS:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"  {i}. {rec}")
    
    # Save report if requested
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(json.dumps(report, indent=2))
        print(f"\n📄 Report saved to: {output_path}")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()