#!/usr/bin/env python3
"""
Test organization script for starter-mcp-server.

This script organizes test files by moving them from the starter-mcp-server root directory 
to appropriate test subdirectories within starter-mcp-server/tests.
It categorizes tests into unit, integration, e2e categories.
"""

import os
import shutil
import re
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('organize_starter_mcp_tests')

# Project root directory
ROOT_DIR = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Starter MCP Server directory
STARTER_MCP_DIR = ROOT_DIR / 'starter-mcp-server'

# Test directories within starter-mcp-server
UNIT_TEST_DIR = STARTER_MCP_DIR / 'tests' / 'unit'
INTEGRATION_TEST_DIR = STARTER_MCP_DIR / 'tests' / 'integration'
E2E_TEST_DIR = STARTER_MCP_DIR / 'tests' / 'e2e'

# Files to exclude from moving (keep in root)
EXCLUDE_FILES = [
    # Add any files you want to keep in the root directory
]

# Mapping of test types to directories
TEST_TYPE_MAPPING = {
    # Unit tests - focused on testing individual components
    'unit': [
        r'test_import',
        r'direct_test_base_tool',
        r'direct_test_import',
        r'direct_test_hybrid',
    ],
    
    # Integration tests - testing interactions between components
    'integration': [
        r'test_mcp_server_integration',
        r'test_crypto_crawler',
        r'test_crawl_website_tool',
        r'test_altcoin_season_index',
        r'test_coinmarketcap',
        r'direct_test_crawler',
        r'direct_test_crypto_analyzer',
        r'direct_test_hybrid_search',
        r'direct_test_knowledge_graph',
        r'direct_test_tools_integration',
        r'direct_test_image_extraction',
    ],
    
    # End-to-end tests - testing complete workflows
    'e2e': [
        r'test_crypto_crawler_with_config',
        r'test_crypto_crawler_with_llm',
        r'direct_test_async_webcrawler',
        r'direct_test_full_workflow',
    ],
}

def determine_test_type(filename):
    """Determine the type of test based on the filename.
    
    Args:
        filename: The name of the test file
        
    Returns:
        The test type (unit, integration, e2e)
    """
    # Check if the filename matches any of the patterns in TEST_TYPE_MAPPING
    for test_type, patterns in TEST_TYPE_MAPPING.items():
        for pattern in patterns:
            if re.search(pattern, filename):
                return test_type
    
    # If no category is determined, default to unit tests
    return 'unit'

def move_test_files(delete_originals=False):
    """Move test files from starter-mcp-server root directory to appropriate test subdirectories.
    
    Args:
        delete_originals: Whether to delete the original files after copying
    """
    # Get all Python files in the starter-mcp-server directory that start with 'test_' or 'direct_test_'
    root_test_files = [(STARTER_MCP_DIR, f) for f in os.listdir(STARTER_MCP_DIR) 
                      if (f.startswith('test_') or f.startswith('direct_test_')) 
                      and f.endswith('.py') 
                      and f not in EXCLUDE_FILES]
    
    # Count of moved files by category
    moved_counts = {
        'unit': 0, 
        'integration': 0, 
        'e2e': 0, 
        'skipped': 0
    }
    
    for source_dir, filename in root_test_files:
        source_path = source_dir / filename
        
        # Skip if the file is already in a proper test subdirectory
        if str(source_dir).endswith(('unit', 'integration', 'e2e')):
            logger.debug(f"Skipping {filename} as it's already in a proper test directory")
            continue
        
        # Determine the test type
        test_type = determine_test_type(filename)
        
        # Map the test type to the target directory
        if test_type == 'unit':
            target_dir = UNIT_TEST_DIR
        elif test_type == 'integration':
            target_dir = INTEGRATION_TEST_DIR
        elif test_type == 'e2e':
            target_dir = E2E_TEST_DIR
        else:
            # This should not happen, but just in case
            logger.warning(f"Unknown test type {test_type} for {filename}")
            continue
        
        # Create the target directory if it doesn't exist
        os.makedirs(target_dir, exist_ok=True)
        
        # Construct the target path
        target_path = target_dir / filename
        
        # Skip if the target file already exists
        if target_path.exists():
            logger.info(f"Skipping {filename} as it already exists in {target_dir}")
            moved_counts['skipped'] += 1
            continue
        
        # Copy the file to the target directory
        logger.info(f"Moving {filename} to {target_dir}")
        shutil.copy2(source_path, target_path)
        
        # Delete the original file if requested
        if delete_originals:
            logger.info(f"Deleting original file {source_path}")
            os.remove(source_path)
        
        # Increment the count for this test type
        moved_counts[test_type] += 1
    
    return moved_counts

def create_readme_files():
    """Create README.md files for each test directory."""
    # Unit tests README
    unit_readme = UNIT_TEST_DIR / 'README.md'
    if not unit_readme.exists():
        with open(unit_readme, 'w') as f:
            f.write("# Unit Tests\n\n")
            f.write("This directory contains unit tests for the starter-mcp-server.\n\n")
            f.write("## Running the tests\n\n")
            f.write("```bash\n")
            f.write("cd starter-mcp-server\n")
            f.write("python -m pytest tests/unit\n")
            f.write("```\n")
    
    # Integration tests README
    integration_readme = INTEGRATION_TEST_DIR / 'README.md'
    if not integration_readme.exists():
        with open(integration_readme, 'w') as f:
            f.write("# Integration Tests\n\n")
            f.write("This directory contains integration tests for the starter-mcp-server.\n\n")
            f.write("## Running the tests\n\n")
            f.write("```bash\n")
            f.write("cd starter-mcp-server\n")
            f.write("python -m pytest tests/integration\n")
            f.write("```\n")
    
    # E2E tests README
    e2e_readme = E2E_TEST_DIR / 'README.md'
    if not e2e_readme.exists():
        with open(e2e_readme, 'w') as f:
            f.write("# End-to-End Tests\n\n")
            f.write("This directory contains end-to-end tests for the starter-mcp-server.\n\n")
            f.write("## Running the tests\n\n")
            f.write("```bash\n")
            f.write("cd starter-mcp-server\n")
            f.write("python -m pytest tests/e2e\n")
            f.write("```\n")

def main():
    """Main function to organize tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Organize test files in starter-mcp-server')
    parser.add_argument('--delete-originals', action='store_true', help='Delete original files after moving')
    parser.add_argument('--create-readmes', action='store_true', help='Create README.md files for test directories')
    
    args = parser.parse_args()
    
    # Ensure test directories exist
    os.makedirs(UNIT_TEST_DIR, exist_ok=True)
    os.makedirs(INTEGRATION_TEST_DIR, exist_ok=True)
    os.makedirs(E2E_TEST_DIR, exist_ok=True)
    
    # Move test files
    moved_counts = move_test_files(delete_originals=args.delete_originals)
    
    # Create README files if requested
    if args.create_readmes:
        create_readme_files()
    
    # Log summary
    logger.info(f"Moved {sum(moved_counts.values()) - moved_counts['skipped']} files:")
    logger.info(f"  Unit tests: {moved_counts['unit']}")
    logger.info(f"  Integration tests: {moved_counts['integration']}")
    logger.info(f"  E2E tests: {moved_counts['e2e']}")
    logger.info(f"  Skipped: {moved_counts['skipped']}")

if __name__ == '__main__':
    main()