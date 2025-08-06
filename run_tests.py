#!/usr/bin/env python3
"""
Quick test runner for URL mapping services.

This script provides a simple way to test the URL mapping functionality
without needing to manually interact with the frontend.

Usage:
    python run_tests.py [--backend-url URL] [--verbose]
    
Examples:
    python run_tests.py
    python run_tests.py --backend-url http://localhost:4001
    python run_tests.py --verbose
"""

import argparse
import asyncio
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from test_url_mapping_integration import URLMappingIntegrationTester


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Test runner for URL mapping services",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                           # Run with default settings
  python run_tests.py --backend-url http://localhost:4001
  python run_tests.py --verbose                 # Show detailed output
        """
    )
    
    parser.add_argument(
        "--backend-url",
        default="http://localhost:4001",
        help="Backend server URL (default: http://localhost:4001)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    return parser.parse_args()


async def main():
    """Main entry point."""
    args = parse_arguments()
    
    if args.verbose:
        print(f"Backend URL: {args.backend_url}")
        print(f"Verbose mode: {args.verbose}")
        print()
    
    print("🧪 Running URL Mapping Service Tests...")
    print("======================================\n")
    
    async with URLMappingIntegrationTester(backend_url=args.backend_url) as tester:
        await tester.run_all_tests()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        sys.exit(1)