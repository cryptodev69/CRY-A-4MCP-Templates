#!/usr/bin/env python3
"""Test script for adaptive crawling API endpoints."""

import sys
sys.path.insert(0, 'src')

from cry_a_4mcp.api.endpoints.adaptive_crawling import setup_adaptive_routes
from fastapi import FastAPI

def test_api_endpoints():
    """Test that adaptive crawling API endpoints can be created."""
    try:
        # Create FastAPI app
        app = FastAPI()
        
        # Setup adaptive routes
        router = setup_adaptive_routes(None)
        
        print("✓ Adaptive API endpoints created successfully")
        print(f"✓ Number of routes: {len(router.routes)}")
        
        for route in router.routes:
            methods = list(route.methods) if hasattr(route, 'methods') else ['GET']
            path = route.path if hasattr(route, 'path') else 'unknown'
            print(f"  - {methods} {path}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing API endpoints: {e}")
        return False

if __name__ == "__main__":
    success = test_api_endpoints()
    if success:
        print("\n✓ All API endpoint tests passed!")
    else:
        print("\n✗ API endpoint tests failed!")
        sys.exit(1)