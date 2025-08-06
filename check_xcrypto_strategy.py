import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Import the strategy class
from cry_a_4mcp.crawl4ai.extraction_strategies.crypto.xcryptohunter_llm import XCryptoHunterLLMExtractionStrategy
from cry_a_4mcp.crawl4ai.extraction_strategies.registry import StrategyRegistry

# Check if the class has SCHEMA and INSTRUCTION attributes
print("Checking XCryptoHunterLLMExtractionStrategy class attributes:")
print(f"Has SCHEMA attribute: {hasattr(XCryptoHunterLLMExtractionStrategy, 'SCHEMA')}")
print(f"Has INSTRUCTION attribute: {hasattr(XCryptoHunterLLMExtractionStrategy, 'INSTRUCTION')}")

# Try to register the strategy
print("\nAttempting to register the strategy:")
try:
    StrategyRegistry.register()(XCryptoHunterLLMExtractionStrategy)
    print("✅ Strategy registered successfully!")
    
    # Check if it's in the registry
    all_strategies = StrategyRegistry.get_all()
    if 'XCryptoHunterLLMExtractionStrategy' in all_strategies:
        print("✅ Strategy is in the registry!")
    else:
        print("❌ Strategy is NOT in the registry!")
        
    # Get metadata for the strategy
    metadata = StrategyRegistry.get_metadata('XCryptoHunterLLMExtractionStrategy')
    print("\nStrategy metadata:")
    for key, value in metadata.items():
        print(f"{key}: {value}")
        
except Exception as e:
    print(f"❌ Error registering strategy: {str(e)}")