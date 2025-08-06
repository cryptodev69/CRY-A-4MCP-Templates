import os
import sys
import time
import subprocess

"""
Test script to verify the navigation in the database UI.
This script will:
1. Start the database UI
2. Wait for it to initialize
3. Print instructions for testing the navigation
"""

def main():
    print("Starting database UI test...")
    
    # Start the database UI
    process = subprocess.Popen(
        [sys.executable, "run_strategy_db_ui.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for the UI to initialize
    print("Waiting for UI to initialize (5 seconds)...")
    time.sleep(5)
    
    # Print test instructions
    print("\n" + "-"*50)
    print("DATABASE UI NAVIGATION TEST INSTRUCTIONS")
    print("-"*50)
    print("1. Open the UI at http://localhost:8501")
    print("2. Test the following navigation flows:")
    print("   a. Create New Strategy -> Test New Strategy")
    print("   b. Create New Strategy -> Back to Browse")
    print("   c. Browse Strategies -> Test Strategy")
    print("   d. Edit Strategy -> Test Updated Strategy")
    print("3. Verify that each navigation works correctly")
    print("-"*50)
    print("Press Ctrl+C to stop the test when finished")
    
    try:
        # Wait for the process to complete or user to interrupt
        process.wait()
    except KeyboardInterrupt:
        print("\nStopping test...")
        process.terminate()
        process.wait()
    
    print("Test completed.")


if __name__ == "__main__":
    main()