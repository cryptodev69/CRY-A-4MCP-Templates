#!/usr/bin/env python3
"""Comprehensive test runner for the API testing framework.

This script runs all tests and provides detailed reporting to ensure
all functionality works correctly before and after code changes.
"""

import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Tuple
import json


class TestRunner:
    """Comprehensive test runner with detailed reporting."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_results: Dict[str, Dict] = {}
        self.start_time = None
        self.end_time = None
    
    def run_test_suite(self, test_path: str, suite_name: str) -> Tuple[bool, Dict]:
        """Run a specific test suite and return results."""
        print(f"\n🧪 Running {suite_name}...")
        
        cmd = [
            sys.executable, "-m", "pytest", 
            test_path,
            "-v",
            "--tb=short",
            "--durations=10",
            "--cov=src",
            "--cov-report=term-missing",
            "--json-report",
            f"--json-report-file=test_results_{suite_name.lower().replace(' ', '_')}.json"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            success = result.returncode == 0
            
            # Parse JSON report if available
            json_file = self.project_root / f"test_results_{suite_name.lower().replace(' ', '_')}.json"
            test_data = {}
            if json_file.exists():
                try:
                    with open(json_file, 'r') as f:
                        test_data = json.load(f)
                except Exception as e:
                    print(f"⚠️  Could not parse JSON report: {e}")
            
            return success, {
                "success": success,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "test_data": test_data
            }
            
        except subprocess.TimeoutExpired:
            print(f"❌ {suite_name} timed out after 5 minutes")
            return False, {
                "success": False,
                "error": "Timeout",
                "returncode": -1
            }
        except Exception as e:
            print(f"❌ Error running {suite_name}: {e}")
            return False, {
                "success": False,
                "error": str(e),
                "returncode": -1
            }
    
    def run_all_tests(self) -> bool:
        """Run all test suites and return overall success."""
        self.start_time = time.time()
        
        print("🚀 Starting Comprehensive API Test Suite")
        print("=" * 50)
        
        # Define test suites
        test_suites = [
            ("tests/api/test_url_configurations_crud.py", "URL Configurations CRUD"),
            ("tests/api/test_url_mappings_crud.py", "URL Mappings CRUD"),
            ("tests/api/test_extractors_crud.py", "Extractors CRUD"),
            ("tests/api/test_crawlers_crud.py", "Crawlers CRUD"),
            ("tests/api/test_openrouter_crud.py", "OpenRouter API"),
            ("tests/integration/test_end_to_end_workflows.py", "End-to-End Integration"),
            ("tests/", "All Existing Tests")  # Run any other existing tests
        ]
        
        overall_success = True
        
        for test_path, suite_name in test_suites:
            full_path = self.project_root / test_path
            
            if not full_path.exists():
                print(f"⚠️  Skipping {suite_name} - path not found: {test_path}")
                continue
            
            success, results = self.run_test_suite(test_path, suite_name)
            self.test_results[suite_name] = results
            
            if success:
                print(f"✅ {suite_name} - PASSED")
            else:
                print(f"❌ {suite_name} - FAILED")
                overall_success = False
                
                # Print error details
                if results.get("stderr"):
                    print(f"   Error: {results['stderr'][:200]}...")
        
        self.end_time = time.time()
        return overall_success
    
    def generate_report(self) -> str:
        """Generate a comprehensive test report."""
        total_time = self.end_time - self.start_time if self.end_time and self.start_time else 0
        
        report = []
        report.append("\n" + "=" * 60)
        report.append("📊 COMPREHENSIVE TEST REPORT")
        report.append("=" * 60)
        report.append(f"⏱️  Total execution time: {total_time:.2f} seconds")
        report.append(f"📅 Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Summary
        total_suites = len(self.test_results)
        passed_suites = sum(1 for r in self.test_results.values() if r.get("success", False))
        failed_suites = total_suites - passed_suites
        
        report.append(f"\n📈 SUMMARY:")
        report.append(f"   Total test suites: {total_suites}")
        report.append(f"   ✅ Passed: {passed_suites}")
        report.append(f"   ❌ Failed: {failed_suites}")
        report.append(f"   📊 Success rate: {(passed_suites/total_suites*100):.1f}%" if total_suites > 0 else "   📊 Success rate: N/A")
        
        # Detailed results
        report.append(f"\n📋 DETAILED RESULTS:")
        for suite_name, results in self.test_results.items():
            status = "✅ PASSED" if results.get("success", False) else "❌ FAILED"
            report.append(f"   {suite_name}: {status}")
            
            # Add test statistics if available
            test_data = results.get("test_data", {})
            if test_data and "summary" in test_data:
                summary = test_data["summary"]
                total = summary.get("total", 0)
                passed = summary.get("passed", 0)
                failed = summary.get("failed", 0)
                skipped = summary.get("skipped", 0)
                
                if total > 0:
                    report.append(f"     Tests: {total} total, {passed} passed, {failed} failed, {skipped} skipped")
            
            # Add error details for failed suites
            if not results.get("success", False) and results.get("stderr"):
                error_lines = results["stderr"].split("\n")[:3]  # First 3 lines
                for line in error_lines:
                    if line.strip():
                        report.append(f"     Error: {line.strip()}")
        
        # Recommendations
        report.append(f"\n💡 RECOMMENDATIONS:")
        if failed_suites == 0:
            report.append("   🎉 All tests passed! Your API is working correctly.")
            report.append("   ✨ Safe to deploy or make changes.")
        else:
            report.append("   🔧 Fix failing tests before deploying.")
            report.append("   🔍 Review error messages above for specific issues.")
            report.append("   📝 Consider adding more tests for edge cases.")
        
        # Coverage information
        report.append(f"\n📊 COVERAGE INFORMATION:")
        report.append("   Run 'pytest --cov=src --cov-report=html' for detailed coverage report.")
        report.append("   Target: Maintain >80% code coverage.")
        
        return "\n".join(report)
    
    def cleanup(self):
        """Clean up temporary files."""
        # Remove JSON report files
        for json_file in self.project_root.glob("test_results_*.json"):
            try:
                json_file.unlink()
            except Exception:
                pass


def main():
    """Main entry point for the test runner."""
    runner = TestRunner()
    
    try:
        # Check if pytest is available
        try:
            subprocess.run([sys.executable, "-m", "pytest", "--version"], 
                         capture_output=True, check=True)
        except subprocess.CalledProcessError:
            print("❌ pytest is not installed. Please install it with: pip install pytest pytest-cov pytest-json-report")
            return 1
        
        # Run all tests
        success = runner.run_all_tests()
        
        # Generate and display report
        report = runner.generate_report()
        print(report)
        
        # Save report to file
        report_file = runner.project_root / "test_report.txt"
        with open(report_file, 'w') as f:
            f.write(report)
        print(f"\n📄 Full report saved to: {report_file}")
        
        # Return appropriate exit code
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⚠️  Test run interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return 1
    finally:
        runner.cleanup()


if __name__ == "__main__":
    sys.exit(main())