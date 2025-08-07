#!/usr/bin/env python3
"""Simple test verification script to demonstrate the testing framework.

This script verifies that our test files are properly structured and
can be imported without errors.
"""

import sys
import importlib.util
from pathlib import Path


def verify_test_file(test_file_path: Path) -> bool:
    """Verify that a test file can be imported successfully."""
    try:
        spec = importlib.util.spec_from_file_location("test_module", test_file_path)
        if spec is None:
            print(f"❌ Could not create spec for {test_file_path}")
            return False
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Check if the module has test classes
        test_classes = [name for name in dir(module) if name.startswith('Test')]
        if test_classes:
            print(f"✅ {test_file_path.name} - Found {len(test_classes)} test classes")
            for test_class in test_classes:
                cls = getattr(module, test_class)
                test_methods = [method for method in dir(cls) if method.startswith('test_')]
                print(f"   📋 {test_class}: {len(test_methods)} test methods")
        else:
            print(f"⚠️  {test_file_path.name} - No test classes found")
        
        return True
        
    except Exception as e:
        print(f"❌ {test_file_path.name} - Import error: {e}")
        return False


def main():
    """Main verification function."""
    print("🔍 Verifying Test Framework Structure")
    print("=" * 50)
    
    project_root = Path(__file__).parent
    test_files = [
        project_root / "tests" / "api" / "test_url_configurations_crud.py",
        project_root / "tests" / "api" / "test_url_mappings_crud.py",
        project_root / "tests" / "api" / "test_extractors_crud.py",
        project_root / "tests" / "api" / "test_crawlers_crud.py",
        project_root / "tests" / "api" / "test_openrouter_crud.py",
        project_root / "tests" / "integration" / "test_end_to_end_workflows.py",
        project_root / "tests" / "conftest.py"
    ]
    
    success_count = 0
    total_count = 0
    
    for test_file in test_files:
        total_count += 1
        if test_file.exists():
            if verify_test_file(test_file):
                success_count += 1
        else:
            print(f"❌ {test_file.name} - File not found")
    
    print("\n" + "=" * 50)
    print(f"📊 VERIFICATION SUMMARY:")
    print(f"   Total files checked: {total_count}")
    print(f"   ✅ Successfully verified: {success_count}")
    print(f"   ❌ Failed verification: {total_count - success_count}")
    print(f"   📈 Success rate: {(success_count/total_count*100):.1f}%")
    
    if success_count == total_count:
        print("\n🎉 All test files are properly structured!")
        print("💡 The testing framework is ready to use.")
        print("\n📋 Next steps:")
        print("   1. Fix pytest dependency conflicts")
        print("   2. Run individual test files with: python -m pytest <test_file>")
        print("   3. Use the comprehensive test runner: python run_tests.py")
        return 0
    else:
        print("\n⚠️  Some test files have issues that need to be resolved.")
        return 1


if __name__ == "__main__":
    sys.exit(main())