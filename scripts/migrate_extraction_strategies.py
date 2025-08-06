#!/usr/bin/env python3
"""
Migration script for transitioning from the old extraction strategy structure to the new one.

This script helps users migrate their code from using the old extraction strategy
structure to the new modular structure with registry and factory patterns.
"""

import os
import sys
import re
import argparse
from typing import List, Dict, Any, Optional

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Migrate extraction strategies to the new structure")
    parser.add_argument(
        "--scan-dir",
        type=str,
        default=".",
        help="Directory to scan for Python files using the old extraction strategy structure"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't modify files, just show what would be changed"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed information about the migration process"
    )
    return parser.parse_args()

def find_python_files(directory: str) -> List[str]:
    """Find all Python files in the given directory and its subdirectories."""
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files

def check_file_for_old_imports(file_path: str) -> bool:
    """Check if a file contains imports from the old extraction strategy structure."""
    with open(file_path, "r") as f:
        content = f.read()
    
    # Check for imports from the old structure
    old_import_patterns = [
        r"from\s+(?:src\.)?cry_a_4mcp\.crawl4ai\.extraction_strategy\s+import",
        r"from\s+(?:src\.)?cry_a_4mcp\.crawl4ai\.crypto_extraction_strategy\s+import",
        r"import\s+(?:src\.)?cry_a_4mcp\.crawl4ai\.extraction_strategy",
        r"import\s+(?:src\.)?cry_a_4mcp\.crawl4ai\.crypto_extraction_strategy"
    ]
    
    for pattern in old_import_patterns:
        if re.search(pattern, content):
            return True
    
    return False

def migrate_imports(content: str) -> str:
    """Migrate imports from the old structure to the new one."""
    # Replace imports from extraction_strategy
    content = re.sub(
        r"from\s+(?:src\.)?cry_a_4mcp\.crawl4ai\.extraction_strategy\s+import\s+LLMExtractionStrategy",
        "from src.cry_a_4mcp.crawl4ai.extraction_strategies import LLMExtractionStrategy",
        content
    )
    
    # Replace imports from crypto_extraction_strategy
    content = re.sub(
        r"from\s+(?:src\.)?cry_a_4mcp\.crawl4ai\.crypto_extraction_strategy\s+import\s+CryptoLLMExtractionStrategy",
        "from src.cry_a_4mcp.crawl4ai.extraction_strategies import CryptoLLMExtractionStrategy",
        content
    )
    
    # Replace module imports
    content = re.sub(
        r"import\s+(?:src\.)?cry_a_4mcp\.crawl4ai\.extraction_strategy",
        "import src.cry_a_4mcp.crawl4ai.extraction_strategies",
        content
    )
    
    content = re.sub(
        r"import\s+(?:src\.)?cry_a_4mcp\.crawl4ai\.crypto_extraction_strategy",
        "import src.cry_a_4mcp.crawl4ai.extraction_strategies",
        content
    )
    
    # Replace usage of module attributes
    content = re.sub(
        r"(?:src\.)?cry_a_4mcp\.crawl4ai\.extraction_strategy\.LLMExtractionStrategy",
        "src.cry_a_4mcp.crawl4ai.extraction_strategies.LLMExtractionStrategy",
        content
    )
    
    content = re.sub(
        r"(?:src\.)?cry_a_4mcp\.crawl4ai\.crypto_extraction_strategy\.CryptoLLMExtractionStrategy",
        "src.cry_a_4mcp.crawl4ai.extraction_strategies.CryptoLLMExtractionStrategy",
        content
    )
    
    return content

def migrate_file(file_path: str, dry_run: bool = False, verbose: bool = False) -> bool:
    """Migrate a file from the old extraction strategy structure to the new one."""
    with open(file_path, "r") as f:
        content = f.read()
    
    # Migrate imports
    new_content = migrate_imports(content)
    
    # Check if anything changed
    if new_content == content:
        if verbose:
            print(f"No changes needed for {file_path}")
        return False
    
    if verbose:
        print(f"Migrating {file_path}")
    
    if not dry_run:
        with open(file_path, "w") as f:
            f.write(new_content)
    
    return True

def main():
    """Main function."""
    args = parse_args()
    
    print(f"Scanning directory: {args.scan_dir}")
    python_files = find_python_files(args.scan_dir)
    print(f"Found {len(python_files)} Python files")
    
    files_to_migrate = []
    for file_path in python_files:
        if check_file_for_old_imports(file_path):
            files_to_migrate.append(file_path)
    
    print(f"Found {len(files_to_migrate)} files to migrate")
    
    if args.dry_run:
        print("Dry run mode - no files will be modified")
    
    migrated_files = 0
    for file_path in files_to_migrate:
        if migrate_file(file_path, args.dry_run, args.verbose):
            migrated_files += 1
    
    print(f"Migration complete. {migrated_files} files {'would be' if args.dry_run else 'were'} migrated.")
    
    if not args.dry_run and migrated_files > 0:
        print("\nMigration Notes:")
        print("1. The new structure uses a registry and factory pattern for creating strategies.")
        print("2. Consider using StrategyFactory.create() instead of direct instantiation.")
        print("3. Check the examples directory for examples of using the new structure.")
        print("4. Run tests to ensure everything still works as expected.")

if __name__ == "__main__":
    main()