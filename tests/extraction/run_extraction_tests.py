#!/usr/bin/env python3
"""
Test runner for extraction UI tests.

This script runs all the test suites related to the extraction UI functionality.
"""

import os
import sys
import unittest
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the test modules
from tests.test_ui_extraction import TestUIExtraction
from tests.test_extraction_button import TestExtractionButton
from tests.test_extraction_process import TestExtractionProcess


def run_tests():
    """Run all the extraction UI tests."""
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add the test cases
    test_suite.addTest(unittest.makeSuite(TestUIExtraction))
    test_suite.addTest(unittest.makeSuite(TestExtractionButton))
    test_suite.addTest(unittest.makeSuite(TestExtractionProcess))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Return the result
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)