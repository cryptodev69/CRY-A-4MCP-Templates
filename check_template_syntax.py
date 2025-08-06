#!/usr/bin/env python3

import os
import sys
import ast

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def check_template_file(file_path):
    print(f"\nChecking template file: {file_path}")
    print(f"File exists: {os.path.exists(file_path)}")
    
    if not os.path.exists(file_path):
        print(f"Error: File does not exist: {file_path}")
        return False
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            print(f"File size: {len(content)} bytes")
            
            # Check for type ignore directives
            print(f"Contains 'type: ignore': {'type: ignore' in content}")
            print(f"Contains 'pyright: ignore': {'pyright: ignore' in content}")
            print(f"Contains 'reportSyntaxError': {'reportSyntaxError' in content}")
            
            # Check for template variables
            print(f"Contains template variables: {'{{' in content and '}}' in content}")
            
            # Print first 5 lines
            print("First 5 lines:")
            lines = content.split('\n')[:5]
            for i, line in enumerate(lines):
                print(f"{i+1}: {line}")
            
            return True
    except Exception as e:
        print(f"Error reading file: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    template_dir = os.path.join('src', 'cry_a_4mcp', 'crawl4ai', 'extraction_strategies', 'ui', 'templates')
    template_files = [
        os.path.join(template_dir, 'strategy_template.py.tmpl'),
        os.path.join(template_dir, 'strategy_template_class_attrs.py.tmpl')
    ]
    
    success = True
    for template_file in template_files:
        if not check_template_file(template_file):
            success = False
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())