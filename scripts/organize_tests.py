#!/usr/bin/env python3
"""
Test organization script.

This script organizes test files by moving them from the root directory to appropriate test directories.
It categorizes tests into unit, integration, e2e, ui, extraction, strategy, and utils categories.
"""

import os
import sys
import shutil
import re
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('organize_tests')

# Project root directory
ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test directories
UNIT_TEST_DIR = ROOT_DIR / 'tests' / 'unit'
INTEGRATION_TEST_DIR = ROOT_DIR / 'tests' / 'integration'
E2E_TEST_DIR = ROOT_DIR / 'tests' / 'e2e'
UI_TEST_DIR = ROOT_DIR / 'tests' / 'ui'
EXTRACTION_TEST_DIR = ROOT_DIR / 'tests' / 'extraction'
STRATEGY_TEST_DIR = ROOT_DIR / 'tests' / 'strategy'
UTILS_TEST_DIR = ROOT_DIR / 'tests' / 'utils'

# Files to exclude from moving (keep in root)
EXCLUDE_FILES = [
    # Add any files you want to keep in the root directory
]

# Mapping of test types to directories
TEST_TYPE_MAPPING = {
    # Unit tests - focused on testing individual components
    'unit': [
        r'test_class_attrs',
        r'test_default_model',
        r'test_extract_params',
        r'test_factory',
        r'test_import',
        r'test_register',
        r'test_strategy\.py$',  # Only exact match for test_strategy.py
        r'test_sync_wrapper',
        r'test_metrics_exporter',
    ],
    
    # Integration tests - testing interaction between components
    'integration': [
        r'test_strategy_extraction',
        r'test_strategy_workflow',
        r'test_template_generation',
        r'test_openrouter',
        r'test_improved_crypto',
        r'test_xcrypto',
    ],
    
    # End-to-end tests - testing complete workflows
    'e2e': [
        r'test_all_categories',
        r'test_db_ui_navigation',
        r'test_universal_news_crawler',
        r'direct_test_',
    ],
    
    # UI tests - testing user interface components
    'ui': [
        r'test_strategy_ui',
        r'test_db_ui',
        r'test_ui_extraction',
        r'test_extraction_button',
    ],
    
    # Extraction tests - testing extraction functionality
    'extraction': [
        r'test_extraction\.py$',  # Only exact match for test_extraction.py
        r'test_extraction_process',
        r'run_extraction_tests',
        r'test_new_extraction_strategies',
        r'test_nft_extraction_strategy',
    ],
    
    # Strategy tests - testing strategy functionality
    'strategy': [
        r'test_extraction_strategies',
        r'test_extraction_strategy_comprehensive',
    ],
    
    # Utils tests - testing utility functions
    'utils': [
        r'test_utils',
        r'test_helpers',
    ]
}

def determine_test_type(filename):
    """Determine the type of test based on filename patterns.
    
    Args:
        filename: The name of the test file
        
    Returns:
        str: The test type ('unit', 'integration', 'e2e', 'ui', 'extraction', 'strategy', 'utils', or None if not determined)
    """
    for test_type, patterns in TEST_TYPE_MAPPING.items():
        for pattern in patterns:
            if re.search(pattern, filename):
                return test_type
    
    # Default categorization based on content if pattern matching fails
    if 'ui' in filename.lower():
        return 'ui'
    elif 'extraction' in filename.lower():
        return 'extraction'
    elif 'strategy' in filename.lower():
        return 'strategy'
    
    # If no category is determined, default to unit tests
    return 'unit'

def move_test_files(delete_originals=False):
    """Move test files from root directory and tests directory to appropriate test subdirectories.
    
    Args:
        delete_originals: Whether to delete the original files after copying
    """
    # Get all Python files in the root directory that start with 'test_' or 'direct_test_'
    root_test_files = [(ROOT_DIR, f) for f in os.listdir(ROOT_DIR) 
                      if (f.startswith('test_') or f.startswith('direct_test_')) 
                      and f.endswith('.py') 
                      and f not in EXCLUDE_FILES]
    
    # Get all Python files in the tests directory that start with 'test_' or 'direct_test_'
    tests_dir = ROOT_DIR / 'tests'
    tests_test_files = []
    if tests_dir.exists():
        tests_test_files = [(tests_dir, f) for f in os.listdir(tests_dir) 
                           if (f.startswith('test_') or f.startswith('direct_test_') or f.startswith('run_')) 
                           and f.endswith('.py') 
                           and f not in EXCLUDE_FILES]
    
    # Combine the lists
    test_files = root_test_files + tests_test_files
    
    # Count of moved files by category
    moved_counts = {
        'unit': 0, 
        'integration': 0, 
        'e2e': 0, 
        'ui': 0, 
        'extraction': 0, 
        'strategy': 0, 
        'utils': 0, 
        'skipped': 0
    }
    
    for source_dir, filename in test_files:
        source_path = source_dir / filename
        
        # Skip if the file is already in a proper test subdirectory
        if str(source_dir).endswith(('unit', 'integration', 'e2e', 'ui', 'extraction', 'strategy', 'utils')):
            logger.debug(f"Skipping {filename} as it's already in a proper test directory")
            continue
        
        # Determine test type
        test_type = determine_test_type(filename)
        
        # Map test type to target directory
        if test_type == 'unit':
            target_dir = UNIT_TEST_DIR
        elif test_type == 'integration':
            target_dir = INTEGRATION_TEST_DIR
        elif test_type == 'e2e':
            target_dir = E2E_TEST_DIR
        elif test_type == 'ui':
            target_dir = UI_TEST_DIR
        elif test_type == 'extraction':
            target_dir = EXTRACTION_TEST_DIR
        elif test_type == 'strategy':
            target_dir = STRATEGY_TEST_DIR
        elif test_type == 'utils':
            target_dir = UTILS_TEST_DIR
        else:
            logger.warning(f"Could not determine test type for {filename}, categorizing as unit test")
            target_dir = UNIT_TEST_DIR
        
        # Update count
        if test_type in moved_counts:
            moved_counts[test_type] += 1
        
        target_path = target_dir / filename
        
        # Skip if source and target are the same
        if source_path == target_path:
            logger.debug(f"Skipping {filename} as it's already in the correct directory")
            continue
        
        # Check if target file already exists
        if target_path.exists():
            logger.warning(f"Target file {target_path} already exists, skipping")
            moved_counts['skipped'] += 1
            continue
        
        # Move the file
        try:
            # Ensure target directory exists
            os.makedirs(target_dir, exist_ok=True)
            
            # Copy the file
            shutil.copy2(source_path, target_path)
            logger.info(f"Copied {filename} to {target_dir}")
            
            # Delete original if requested
            if delete_originals:
                os.remove(source_path)
                logger.info(f"Removed original file {source_path}")
        except Exception as e:
            logger.error(f"Error moving {filename}: {e}")
    
    # Log summary
    logger.info(f"Test organization complete.")
    logger.info(f"Files copied:")
    logger.info(f"  Unit: {moved_counts['unit']}")
    logger.info(f"  Integration: {moved_counts['integration']}")
    logger.info(f"  E2E: {moved_counts['e2e']}")
    logger.info(f"  UI: {moved_counts['ui']}")
    logger.info(f"  Extraction: {moved_counts['extraction']}")
    logger.info(f"  Strategy: {moved_counts['strategy']}")
    logger.info(f"  Utils: {moved_counts['utils']}")
    logger.info(f"Files skipped: {moved_counts['skipped']}")
    
    if not delete_originals:
        logger.info(f"Note: Original files were not deleted. Review the copied files and delete originals manually.")
    else:
        logger.info(f"Note: Original files were deleted.")
        
    return moved_counts

def create_readme_files():
    """Create README.md files in each test directory explaining its purpose."""
    readme_content = {
        UNIT_TEST_DIR: """
# Unit Tests

This directory contains unit tests for individual components of the system.

Unit tests focus on testing small, isolated pieces of code to ensure they work correctly in isolation.

## Running Unit Tests

```bash
python -m pytest tests/unit
```
""",
        INTEGRATION_TEST_DIR: """
# Integration Tests

This directory contains integration tests that verify different components work together correctly.

Integration tests focus on testing the interaction between components.

## Running Integration Tests

```bash
python -m pytest tests/integration
```
""",
        E2E_TEST_DIR: """
# End-to-End Tests

This directory contains end-to-end tests that verify complete workflows.

E2E tests focus on testing the system as a whole from a user's perspective.

## Running E2E Tests

```bash
python -m pytest tests/e2e
```
""",
        UI_TEST_DIR: """
# UI Tests

This directory contains tests for user interface components.

UI tests focus on testing the user interface and user interactions.

## Running UI Tests

```bash
python -m pytest tests/ui
```
""",
        EXTRACTION_TEST_DIR: """
# Extraction Tests

This directory contains tests for extraction functionality.

Extraction tests focus on testing the extraction of data from various sources.

## Running Extraction Tests

```bash
python -m pytest tests/extraction
```
""",
        STRATEGY_TEST_DIR: """
# Strategy Tests

This directory contains tests for strategy functionality.

Strategy tests focus on testing the implementation of various extraction strategies.

## Running Strategy Tests

```bash
python -m pytest tests/strategy
```
""",
        UTILS_TEST_DIR: """
# Utils Tests

This directory contains tests for utility functions.

Utils tests focus on testing helper functions and utilities used throughout the codebase.

## Running Utils Tests

```bash
python -m pytest tests/utils
```
"""
    }
    
    for dir_path, content in readme_content.items():
        readme_path = dir_path / "README.md"
        if not readme_path.exists():
            with open(readme_path, 'w') as f:
                f.write(content.strip())
            logger.info(f"Created README.md in {dir_path}")

def update_main_readme():
    """Update the main README.md in the tests directory."""
    main_readme_path = ROOT_DIR / "tests" / "README.md"
    
    # Check if the file exists and read its content
    if main_readme_path.exists():
        with open(main_readme_path, 'r') as f:
            current_content = f.read()
    else:
        current_content = "# Tests\n\nThis directory contains tests for the project.\n"
    
    # Add information about the new test directories if not already present
    new_content = """
## Test Directory Structure

- `unit/`: Unit tests for individual components
- `integration/`: Tests for component interactions
- `e2e/`: End-to-end tests for complete workflows
- `ui/`: Tests for user interface components
- `extraction/`: Tests for extraction functionality
- `strategy/`: Tests for strategy functionality
- `utils/`: Tests for utility functions
- `benchmarks/`: Performance benchmarks
- `comparison/`: Comparison tests
- `samples/`: Sample data for tests

## Running Tests

To run all tests:

```bash
python -m pytest
```

To run tests in a specific directory:

```bash
python -m pytest tests/unit
```
"""
    
    # Only add the new content if it's not already there
    if "Test Directory Structure" not in current_content:
        with open(main_readme_path, 'w') as f:
            f.write(current_content + new_content)
        logger.info(f"Updated main README.md in tests directory")

def clean_tests_directory(delete_originals=False):
    """Clean up test files in the tests directory root by moving them to appropriate subdirectories."""
    tests_dir = ROOT_DIR / 'tests'
    if not tests_dir.exists():
        logger.warning(f"Tests directory {tests_dir} does not exist")
        return {}
    
    # Get all Python files in the tests directory root that start with 'test_' or 'direct_test_' or 'run_'
    test_files = []
    for f in os.listdir(tests_dir):
        if ((f.startswith('test_') or f.startswith('direct_test_') or f.startswith('run_')) 
            and f.endswith('.py') 
            and f not in EXCLUDE_FILES):
            file_path = tests_dir / f
            if file_path.is_file():
                test_files.append(f)
    
    logger.info(f"Found {len(test_files)} test files in tests directory root: {test_files}")
    
    # Count of moved files by category
    moved_counts = {
        'unit': 0, 
        'integration': 0, 
        'e2e': 0, 
        'ui': 0, 
        'extraction': 0, 
        'strategy': 0, 
        'utils': 0, 
        'skipped': 0,
        'deleted': 0
    }
    
    for filename in test_files:
        source_path = tests_dir / filename
        
        # Double check if the file is in a subdirectory
        if not source_path.is_file():
            logger.debug(f"Skipping {filename} as it's not a file")
            continue
            
        # Determine test type
        test_type = determine_test_type(filename)
        logger.info(f"Determined test type for {filename}: {test_type}")
        
        # Map test type to target directory
        if test_type == 'unit':
            target_dir = UNIT_TEST_DIR
        elif test_type == 'integration':
            target_dir = INTEGRATION_TEST_DIR
        elif test_type == 'e2e':
            target_dir = E2E_TEST_DIR
        elif test_type == 'ui':
            target_dir = UI_TEST_DIR
        elif test_type == 'extraction':
            target_dir = EXTRACTION_TEST_DIR
        elif test_type == 'strategy':
            target_dir = STRATEGY_TEST_DIR
        elif test_type == 'utils':
            target_dir = UTILS_TEST_DIR
        else:
            logger.warning(f"Could not determine test type for {filename}, categorizing as unit test")
            target_dir = UNIT_TEST_DIR
        
        # Update count
        if test_type in moved_counts:
            moved_counts[test_type] += 1
        
        target_path = target_dir / filename
        
        # Skip if source and target are the same
        if source_path == target_path:
            logger.debug(f"Skipping {filename} as it's already in the correct directory")
            continue
        
        # Check if target file already exists
        if target_path.exists():
            logger.warning(f"Target file {target_path} already exists, skipping")
            moved_counts['skipped'] += 1
            # If delete_originals is True, delete the original even if we skipped copying
            if delete_originals:
                try:
                    os.remove(source_path)
                    logger.info(f"Removed original file {source_path} (target already existed)")
                    moved_counts['deleted'] += 1
                except Exception as e:
                    logger.error(f"Error removing {source_path}: {e}")
            continue
        
        # Move the file
        try:
            # Ensure target directory exists
            os.makedirs(target_dir, exist_ok=True)
            
            # Copy the file
            shutil.copy2(source_path, target_path)
            logger.info(f"Copied {filename} to {target_dir}")
            
            # Delete original if requested
            if delete_originals:
                try:
                    os.remove(source_path)
                    logger.info(f"Removed original file {source_path}")
                    moved_counts['deleted'] += 1
                except Exception as e:
                    logger.error(f"Error removing {source_path}: {e}")
        except Exception as e:
            logger.error(f"Error moving {filename}: {e}")
    
    return moved_counts

if __name__ == "__main__":
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Organize test files into appropriate directories.')
    parser.add_argument('--delete-originals', action='store_true', help='Delete original files after copying')
    parser.add_argument('--create-readmes', action='store_true', help='Create README.md files in test directories')
    parser.add_argument('--update-main-readme', action='store_true', help='Update the main README.md in tests directory')
    parser.add_argument('--clean-tests-dir', action='store_true', help='Clean up test files in the tests directory root')
    parser.add_argument('--include-starter-mcp', action='store_true', help='Also organize tests in starter-mcp-server directory')
    args = parser.parse_args()
    
    # Ensure all test directories exist
    os.makedirs(UNIT_TEST_DIR, exist_ok=True)
    os.makedirs(INTEGRATION_TEST_DIR, exist_ok=True)
    os.makedirs(E2E_TEST_DIR, exist_ok=True)
    os.makedirs(UI_TEST_DIR, exist_ok=True)
    os.makedirs(EXTRACTION_TEST_DIR, exist_ok=True)
    os.makedirs(STRATEGY_TEST_DIR, exist_ok=True)
    os.makedirs(UTILS_TEST_DIR, exist_ok=True)
    
    # Move test files from root directory
    moved_counts = move_test_files(delete_originals=args.delete_originals)
    
    # Clean up tests directory if requested
    if args.clean_tests_dir:
        tests_moved_counts = clean_tests_directory(delete_originals=args.delete_originals)
        # Merge the counts
        for key in moved_counts:
            if key in tests_moved_counts:
                moved_counts[key] += tests_moved_counts[key]
    
    # Create README files if requested
    if args.create_readmes:
        create_readme_files()
    
    # Update main README if requested
    if args.update_main_readme:
        update_main_readme()
    
    # Print summary
    total_moved = sum(moved_counts.values()) - moved_counts['skipped']
    logger.info(f"Total files moved: {total_moved}")
    logger.info(f"Run with --delete-originals to delete original files after copying")
    logger.info(f"Run with --create-readmes to create README.md files in test directories")
    logger.info(f"Run with --update-main-readme to update the main README.md in tests directory")
    logger.info(f"Run with --clean-tests-dir to clean up test files in the tests directory root")
    
    # Handle starter-mcp-server directory if requested
    if args.include_starter_mcp:
        logger.info("\nOrganizing tests in starter-mcp-server directory...")
        # Instead of importing the module, run the script directly
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'organize_starter_mcp_tests.py')
        logger.info(f"Running script: {script_path}")
        
        # Check if the script exists
        if not os.path.exists(script_path):
            logger.error(f"Script not found: {script_path}")
        else:
            # Build the command to run the script
            cmd = [sys.executable, script_path]
            if args.delete_originals:
                cmd.append('--delete-originals')
            if args.create_readmes:
                cmd.append('--create-readmes')
            
            # Run the script as a subprocess
            import subprocess
            try:
                logger.info(f"Executing: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                logger.info(result.stdout)
                if result.stderr:
                    logger.warning(result.stderr)
            except subprocess.CalledProcessError as e:
                logger.error(f"Error running organize_starter_mcp_tests.py: {e}")
                logger.error(e.stderr)
            except Exception as e:
                logger.error(f"Error organizing tests in starter-mcp-server: {e}")
                import traceback
                logger.error(traceback.format_exc())