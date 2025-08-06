import os
import importlib
import inspect
import sqlite3
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Function to check database entries
def check_database_strategies():
    print("\n=== CHECKING DATABASE STRATEGIES ===")
    try:
        # Connect to the database
        db_path = os.path.join(project_root, 'src/cry_a_4mcp/crawl4ai/extraction_strategies/ui/config/strategies.db')
        print(f"Connecting to database: {db_path}")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all strategies from the database
        cursor.execute("SELECT id, name, category, file_path FROM strategies")
        strategies = cursor.fetchall()
        
        print(f"Found {len(strategies)} strategies in the database")
        
        for strategy in strategies:
            strategy_id, name, category, file_path = strategy
            print(f"\nStrategy ID: {strategy_id}")
            print(f"Name: {name}")
            print(f"Category: {category}")
            print(f"File Path: {file_path}")
            
            # Check if the file exists
            if not os.path.exists(file_path):
                print(f"  WARNING: File does not exist: {file_path}")
                continue
                
        conn.close()
    except Exception as e:
        print(f"Error checking database: {e}")

# Function to find all strategy files
def find_strategy_files():
    print("\n=== FINDING STRATEGY FILES ===")
    strategy_files = []
    strategy_dir = os.path.join(project_root, 'src/cry_a_4mcp/crawl4ai/extraction_strategies')
    
    print(f"Searching in: {strategy_dir}")
    
    for root, dirs, files in os.walk(strategy_dir):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                file_path = os.path.join(root, file)
                strategy_files.append(file_path)
    
    print(f"Found {len(strategy_files)} potential strategy files")
    return strategy_files

# Function to check strategy classes in files
def check_strategy_classes(strategy_files):
    print("\n=== CHECKING STRATEGY CLASSES ===")
    strategy_classes = []
    
    for file_path in strategy_files:
        try:
            # Convert file path to module path
            rel_path = os.path.relpath(file_path, project_root)
            module_path = rel_path.replace('/', '.').replace('.py', '')
            
            print(f"\nChecking file: {file_path}")
            print(f"Module path: {module_path}")
            
            # Try to import the module
            try:
                module = importlib.import_module(module_path)
                
                # Find all classes in the module
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if 'ExtractionStrategy' in name and obj.__module__ == module_path:
                        print(f"  Found strategy class: {name}")
                        strategy_classes.append((name, file_path, module_path))
            except Exception as e:
                print(f"  ERROR importing module: {e}")
        except Exception as e:
            print(f"  ERROR processing file {file_path}: {e}")
    
    return strategy_classes

# Main function
def main():
    print("Starting strategy check...")
    
    # Check database entries
    check_database_strategies()
    
    # Find all strategy files
    strategy_files = find_strategy_files()
    
    # Check strategy classes in files
    strategy_classes = check_strategy_classes(strategy_files)
    
    print("\n=== SUMMARY ===")
    print(f"Found {len(strategy_classes)} strategy classes in code files")
    
    # Print all strategy classes found
    print("\nStrategy Classes Found:")
    for name, file_path, module_path in strategy_classes:
        print(f"  {name} in {file_path}")

if __name__ == "__main__":
    main()