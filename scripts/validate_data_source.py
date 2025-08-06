#!/usr/bin/env python3
"""
CRY-A-4MCP Data Source Validation Script

Validates new data source integrations for quality, performance, and compliance.
"""

import asyncio
import aiohttp
import json
import time
import importlib.util
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import argparse

class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

class DataSourceValidator:
    def __init__(self, source_path: str):
        self.source_path = Path(source_path)
        self.validation_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'source_path': str(source_path),
            'tests': [],
            'overall_score': 0,
            'passed': 0,
            'failed': 0,
            'warnings': 0
        }
    
    def log_test(self, test_name: str, status: str, message: str, details: Dict = None):
        """Log a test result"""
        test_result = {
            'name': test_name,
            'status': status,
            'message': message,
            'timestamp': datetime.utcnow().isoformat(),
            'details': details or {}
        }
        self.validation_results['tests'].append(test_result)
        
        if status == 'PASS':
            self.validation_results['passed'] += 1
        elif status == 'FAIL':
            self.validation_results['failed'] += 1
        elif status == 'WARN':
            self.validation_results['warnings'] += 1
    
    def validate_file_structure(self) -> bool:
        """Validate the data source file structure"""
        print(f"\n{Colors.BOLD}1. File Structure Validation{Colors.END}")
        
        required_files = [
            'connector.py',
            'models.py',
            'processor.py',
            '__init__.py'
        ]
        
        all_present = True
        for file_name in required_files:
            file_path = self.source_path / file_name
            if file_path.exists():
                self.log_test(f"File: {file_name}", "PASS", f"Required file {file_name} exists")
                print(f"  ✓ {file_name}")
            else:
                self.log_test(f"File: {file_name}", "FAIL", f"Required file {file_name} missing")
                print(f"  ✗ {file_name} {Colors.RED}MISSING{Colors.END}")
                all_present = False
        
        return all_present
    
    def validate_connector_interface(self) -> bool:
        """Validate connector implements required interface"""
        print(f"\n{Colors.BOLD}2. Connector Interface Validation{Colors.END}")
        
        try:
            # Import the connector module
            spec = importlib.util.spec_from_file_location(
                "connector", 
                self.source_path / "connector.py"
            )
            connector_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(connector_module)
            
            # Check for required classes and methods
            required_classes = ['BaseConnector', 'YourSourceConnector']  # Adjust as needed
            required_methods = ['fetch_data', 'health_check', '__aenter__', '__aexit__']
            
            interface_valid = True
            
            for class_name in required_classes:
                if hasattr(connector_module, class_name):
                    self.log_test(f"Class: {class_name}", "PASS", f"Class {class_name} found")
                    print(f"  ✓ {class_name}")
                    
                    # Check methods for main connector class
                    if 'Connector' in class_name and class_name != 'BaseConnector':
                        connector_class = getattr(connector_module, class_name)
                        for method_name in required_methods:
                            if hasattr(connector_class, method_name):
                                self.log_test(f"Method: {method_name}", "PASS", f"Method {method_name} implemented")
                                print(f"    ✓ {method_name}()")
                            else:
                                self.log_test(f"Method: {method_name}", "FAIL", f"Method {method_name} missing")
                                print(f"    ✗ {method_name}() {Colors.RED}MISSING{Colors.END}")
                                interface_valid = False
                else:
                    self.log_test(f"Class: {class_name}", "FAIL", f"Class {class_name} missing")
                    print(f"  ✗ {class_name} {Colors.RED}MISSING{Colors.END}")
                    interface_valid = False
            
            return interface_valid
            
        except Exception as e:
            self.log_test("Connector Import", "FAIL", f"Failed to import connector: {e}")
            print(f"  ✗ Import failed: {Colors.RED}{e}{Colors.END}")
            return False
    
    def validate_data_models(self) -> bool:
        """Validate data models are properly defined"""
        print(f"\n{Colors.BOLD}3. Data Models Validation{Colors.END}")
        
        try:
            spec = importlib.util.spec_from_file_location(
                "models", 
                self.source_path / "models.py"
            )
            models_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(models_module)
            
            # Check for Pydantic models
            required_models = ['YourSourceConfig', 'YourSourceData']  # Adjust as needed
            models_valid = True
            
            for model_name in required_models:
                if hasattr(models_module, model_name):
                    model_class = getattr(models_module, model_name)
                    
                    # Check if it's a Pydantic model
                    if hasattr(model_class, '__fields__'):
                        self.log_test(f"Model: {model_name}", "PASS", f"Pydantic model {model_name} found")
                        print(f"  ✓ {model_name} (Pydantic)")
                        
                        # Check required fields
                        fields = model_class.__fields__
                        print(f"    Fields: {', '.join(fields.keys())}")
                    else:
                        self.log_test(f"Model: {model_name}", "WARN", f"Model {model_name} not using Pydantic")
                        print(f"  ⚠ {model_name} {Colors.YELLOW}(not Pydantic){Colors.END}")
                else:
                    self.log_test(f"Model: {model_name}", "FAIL", f"Model {model_name} missing")
                    print(f"  ✗ {model_name} {Colors.RED}MISSING{Colors.END}")
                    models_valid = False
            
            return models_valid
            
        except Exception as e:
            self.log_test("Models Import", "FAIL", f"Failed to import models: {e}")
            print(f"  ✗ Import failed: {Colors.RED}{e}{Colors.END}")
            return False
    
    def validate_processor(self) -> bool:
        """Validate data processor implementation"""
        print(f"\n{Colors.BOLD}4. Data Processor Validation{Colors.END}")
        
        try:
            spec = importlib.util.spec_from_file_location(
                "processor", 
                self.source_path / "processor.py"
            )
            processor_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(processor_module)
            
            required_classes = ['BaseProcessor', 'YourSourceProcessor']  # Adjust as needed
            required_methods = ['process_item', 'calculate_quality_score']
            
            processor_valid = True
            
            for class_name in required_classes:
                if hasattr(processor_module, class_name):
                    self.log_test(f"Processor: {class_name}", "PASS", f"Processor {class_name} found")
                    print(f"  ✓ {class_name}")
                    
                    # Check methods for main processor class
                    if 'Processor' in class_name and class_name != 'BaseProcessor':
                        processor_class = getattr(processor_module, class_name)
                        for method_name in required_methods:
                            if hasattr(processor_class, method_name):
                                self.log_test(f"Processor Method: {method_name}", "PASS", f"Method {method_name} implemented")
                                print(f"    ✓ {method_name}()")
                            else:
                                self.log_test(f"Processor Method: {method_name}", "FAIL", f"Method {method_name} missing")
                                print(f"    ✗ {method_name}() {Colors.RED}MISSING{Colors.END}")
                                processor_valid = False
                else:
                    self.log_test(f"Processor: {class_name}", "FAIL", f"Processor {class_name} missing")
                    print(f"  ✗ {class_name} {Colors.RED}MISSING{Colors.END}")
                    processor_valid = False
            
            return processor_valid
            
        except Exception as e:
            self.log_test("Processor Import", "FAIL", f"Failed to import processor: {e}")
            print(f"  ✗ Import failed: {Colors.RED}{e}{Colors.END}")
            return False
    
    def validate_documentation(self) -> bool:
        """Validate documentation completeness"""
        print(f"\n{Colors.BOLD}5. Documentation Validation{Colors.END}")
        
        doc_files = ['README.md', 'API.md', 'examples.md']
        docs_present = 0
        
        for doc_file in doc_files:
            doc_path = self.source_path / doc_file
            if doc_path.exists():
                self.log_test(f"Documentation: {doc_file}", "PASS", f"Documentation file {doc_file} exists")
                print(f"  ✓ {doc_file}")
                docs_present += 1
            else:
                self.log_test(f"Documentation: {doc_file}", "WARN", f"Documentation file {doc_file} missing")
                print(f"  ⚠ {doc_file} {Colors.YELLOW}MISSING{Colors.END}")
        
        # Check for inline documentation
        connector_path = self.source_path / "connector.py"
        if connector_path.exists():
            with open(connector_path, 'r') as f:
                content = f.read()
                if '"""' in content or "'''" in content:
                    self.log_test("Inline Documentation", "PASS", "Docstrings found in connector")
                    print(f"  ✓ Inline docstrings")
                else:
                    self.log_test("Inline Documentation", "WARN", "No docstrings found in connector")
                    print(f"  ⚠ No inline docstrings {Colors.YELLOW}MISSING{Colors.END}")
        
        return docs_present >= 1  # At least one doc file should exist
    
    def validate_test_coverage(self) -> bool:
        """Validate test coverage"""
        print(f"\n{Colors.BOLD}6. Test Coverage Validation{Colors.END}")
        
        test_dir = self.source_path / "tests"
        if test_dir.exists():
            test_files = list(test_dir.glob("test_*.py"))
            if test_files:
                self.log_test("Test Files", "PASS", f"Found {len(test_files)} test files")
                print(f"  ✓ {len(test_files)} test files found")
                
                for test_file in test_files:
                    print(f"    - {test_file.name}")
                
                return True
            else:
                self.log_test("Test Files", "WARN", "Test directory exists but no test files found")
                print(f"  ⚠ No test files in tests/ directory {Colors.YELLOW}MISSING{Colors.END}")
                return False
        else:
            self.log_test("Test Directory", "WARN", "No tests directory found")
            print(f"  ⚠ No tests/ directory {Colors.YELLOW}MISSING{Colors.END}")
            return False
    
    async def validate_performance(self) -> bool:
        """Validate performance characteristics"""
        print(f"\n{Colors.BOLD}7. Performance Validation{Colors.END}")
        
        # This is a placeholder for actual performance testing
        # In a real implementation, you would:
        # 1. Load the connector
        # 2. Run sample queries
        # 3. Measure response times
        # 4. Check memory usage
        
        self.log_test("Performance Test", "PASS", "Performance validation placeholder")
        print(f"  ✓ Performance tests (placeholder)")
        
        return True
    
    def calculate_overall_score(self):
        """Calculate overall validation score"""
        total_tests = len(self.validation_results['tests'])
        if total_tests == 0:
            self.validation_results['overall_score'] = 0
            return
        
        # Weight different test types
        weights = {
            'PASS': 1.0,
            'WARN': 0.5,
            'FAIL': 0.0
        }
        
        weighted_score = sum(
            weights.get(test['status'], 0) 
            for test in self.validation_results['tests']
        )
        
        self.validation_results['overall_score'] = (weighted_score / total_tests) * 100
    
    def print_summary(self):
        """Print validation summary"""
        self.calculate_overall_score()
        
        print(f"\n{Colors.BLUE}{Colors.BOLD}Validation Summary{Colors.END}")
        print("=" * 50)
        
        score = self.validation_results['overall_score']
        score_color = Colors.GREEN if score >= 80 else Colors.YELLOW if score >= 60 else Colors.RED
        
        print(f"Overall Score: {score_color}{score:.1f}%{Colors.END}")
        print(f"Tests Passed: {Colors.GREEN}{self.validation_results['passed']}{Colors.END}")
        print(f"Tests Failed: {Colors.RED}{self.validation_results['failed']}{Colors.END}")
        print(f"Warnings:     {Colors.YELLOW}{self.validation_results['warnings']}{Colors.END}")
        
        if score >= 80:
            print(f"\n{Colors.GREEN}✓ Data source is ready for integration{Colors.END}")
        elif score >= 60:
            print(f"\n{Colors.YELLOW}⚠ Data source needs improvements before integration{Colors.END}")
        else:
            print(f"\n{Colors.RED}✗ Data source requires significant work before integration{Colors.END}")
    
    async def run_validation(self) -> Dict:
        """Run complete validation suite"""
        print(f"{Colors.BLUE}{Colors.BOLD}CRY-A-4MCP Data Source Validation{Colors.END}")
        print(f"Validating: {self.source_path}")
        print("=" * 60)
        
        # Run all validation tests
        validations = [
            self.validate_file_structure(),
            self.validate_connector_interface(),
            self.validate_data_models(),
            self.validate_processor(),
            self.validate_documentation(),
            self.validate_test_coverage(),
            await self.validate_performance()
        ]
        
        self.print_summary()
        
        return self.validation_results

async def main():
    parser = argparse.ArgumentParser(description='CRY-A-4MCP Data Source Validator')
    parser.add_argument('source_path', help='Path to data source directory')
    parser.add_argument('--json', action='store_true', help='Output results in JSON format')
    parser.add_argument('--output', type=str, help='Save results to file')
    
    args = parser.parse_args()
    
    if not Path(args.source_path).exists():
        print(f"{Colors.RED}Error: Source path '{args.source_path}' does not exist{Colors.END}")
        sys.exit(1)
    
    validator = DataSourceValidator(args.source_path)
    results = await validator.run_validation()
    
    if args.json:
        print(json.dumps(results, indent=2))
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {args.output}")

if __name__ == "__main__":
    asyncio.run(main())

