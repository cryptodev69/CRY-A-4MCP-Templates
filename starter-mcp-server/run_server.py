#!/usr/bin/env python3
"""Simple script to run the main server with proper Python path setup."""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# Set environment variables for port 4000
os.environ.setdefault("PORT", "4000")
os.environ.setdefault("HOST", "0.0.0.0")

# Now import and run the main module
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "4000")),
        reload=os.getenv("RELOAD", "false").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )