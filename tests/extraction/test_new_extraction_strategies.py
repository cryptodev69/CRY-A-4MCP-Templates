#!/usr/bin/env python3
"""
Test suite for the new extraction strategies framework.

This module provides tests for the new extraction strategies framework,
including the base classes, registry, factory, and domain-specific strategies.
"""

import os
import sys
import json
import asyncio
import unittest
from unittest.mock import AsyncMock, patch
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.cry_a_4mcp.crawl4ai.extraction_strategies import (
    ExtractionStrategy,
    LLMExtractionStrategy,
    CryptoLLMExtractionStrategy,
    StrategyRegistry,
    StrategyFactory,
    CompositeExtractionStrategy,
    register_strategy
)


# Define a test strategy for testing purposes
@register_strategy(
    name="TestStrategy",
    description="A strategy for testing",
    category="test"
)
class TestStrategy(LLMExtractionStrategy):
    def __init__(self, provider="openrouter", api_token=None, **kwargs):
        test_schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "summary": {"type": "string"},
                "test_field": {"type": "string"}
            },
            "required": ["title", "summary"]
        }
        test_instruction = "Extract the title and summary from the content. Add a test_field with value 'test'."
        
        super().__init__(
            provider=provider,
            api_token=api_token,
            instruction=test_instruction,
            schema=test_schema,
            **kwargs
        )
    
    async def extract(self, url, content, **kwargs):
        result = await super().extract(url, content, **kwargs)
        # Add a test field to the result
        if result and isinstance(result, dict):
            result["test_field"] = "test"
        return result


# Sample content for testing
SAMPLE_CONTENT = """
# Bitcoin Surges Past $50,000 as Institutional Adoption Grows

Bitcoin has surged past the $50,000 mark for the first time in several weeks, 
driven by growing institutional adoption and positive market sentiment. 
The cryptocurrency market has been showing signs of recovery after a period of volatility.

Analysts at major investment banks have revised their price targets upward, 
with some suggesting Bitcoin could reach $75,000 by the end of the year. 
The positive outlook comes as more financial institutions announce plans to offer 
cryptocurrency services to their clients.

"We're seeing unprecedented interest from traditional financial players," 
said Jane Smith, crypto analyst at InvestBank. "This is no longer just about retail investors."

Ethereum has also performed well, climbing above $3,000 as the network prepares for 
its next major upgrade. The overall cryptocurrency market capitalization has increased 
by 15% in the past week alone.

However, regulatory concerns remain, with authorities in several countries 
considering new frameworks for cryptocurrency oversight.
"""


class TestExtractionStrategies(unittest.TestCase):
    def setUp(self):
        # Mock API response for testing
        self.mock_api_response = {
            "title": "Test Title",
            "summary": "Test Summary",
            "sentiment": "positive"
        }
    
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.base.LLMExtractionStrategy._call_llm_api')
    async def test_llm_extraction_strategy(self, mock_call_llm_api):
        # Setup mock
        mock_call_llm_api.return_value = self.mock_api_response
        
        # Create strategy
        strategy = LLMExtractionStrategy(
            provider="openrouter",
            api_token="test_token",
            instruction="Extract the title and summary.",
            schema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "summary": {"type": "string"},
                    "sentiment": {"type": "string"}
                },
                "required": ["title", "summary"]
            }
        )
        
        # Test extraction
        result = await strategy.extract(
            url="https://example.com",
            content="This is a test content."
        )
        
        # Assertions
        self.assertEqual(result["title"], "Test Title")
        self.assertEqual(result["summary"], "Test Summary")
        self.assertEqual(result["sentiment"], "positive")
        
        # Verify API call
        mock_call_llm_api.assert_called_once()
    
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.base.LLMExtractionStrategy._call_llm_api')
    async def test_crypto_llm_extraction_strategy(self, mock_call_llm_api):
        # Setup mock
        mock_crypto_response = {
            "headline": "Crypto Test Headline",
            "summary": "Crypto Test Summary",
            "sentiment": "bullish",
            "category": "news",
            "market_impact": "high",
            "key_entities": ["Bitcoin", "Ethereum"],
            "persona_relevance": {
                "meme_snipers": 0.8,
                "gem_hunters": 0.6,
                "legacy_investors": 0.4
            },
            "urgency_score": 8
        }
        mock_call_llm_api.return_value = mock_crypto_response
        
        # Create strategy
        strategy = CryptoLLMExtractionStrategy(
            provider="openrouter",
            api_token="test_token"
        )
        
        # Test extraction
        result = await strategy.extract(
            url="https://example.com/crypto",
            content="This is a crypto test content."
        )
        
        # Assertions
        self.assertEqual(result["headline"], "Crypto Test Headline")
        self.assertEqual(result["summary"], "Crypto Test Summary")
        self.assertEqual(result["sentiment"], "bullish")
        self.assertEqual(result["category"], "news")
        self.assertEqual(result["market_impact"], "high")
        self.assertIn("Bitcoin", result["key_entities"])
        self.assertEqual(result["persona_relevance"]["meme_snipers"], 0.8)
        self.assertEqual(result["urgency_score"], 8)
        
        # Verify API call
        mock_call_llm_api.assert_called_once()
    
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.base.LLMExtractionStrategy._call_llm_api')
    async def test_test_strategy(self, mock_call_llm_api):
        # Setup mock
        mock_call_llm_api.return_value = {
            "title": "Test Strategy Title",
            "summary": "Test Strategy Summary"
        }
        
        # Create strategy
        strategy = TestStrategy(
            provider="openrouter",
            api_token="test_token"
        )
        
        # Test extraction
        result = await strategy.extract(
            url="https://example.com/test",
            content="This is a test content for TestStrategy."
        )
        
        # Assertions
        self.assertEqual(result["title"], "Test Strategy Title")
        self.assertEqual(result["summary"], "Test Strategy Summary")
        self.assertEqual(result["test_field"], "test")
        
        # Verify API call
        mock_call_llm_api.assert_called_once()
    
    def test_strategy_registry(self):
        # Get all registered strategies
        strategies = StrategyRegistry.get_all()
        
        # Assertions
        self.assertIn("LLMExtractionStrategy", strategies)
        self.assertIn("CryptoLLMExtractionStrategy", strategies)
        self.assertIn("TestStrategy", strategies)
        
        # Get strategy by name
        strategy_class = StrategyRegistry.get("TestStrategy")
        self.assertEqual(strategy_class, TestStrategy)
        
        # Get strategies by category
        crypto_strategies = StrategyRegistry.get_by_category("crypto")
        self.assertIn("CryptoLLMExtractionStrategy", crypto_strategies)
        
        test_strategies = StrategyRegistry.get_by_category("test")
        self.assertIn("TestStrategy", test_strategies)
    
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.base.LLMExtractionStrategy._call_llm_api')
    async def test_strategy_factory(self, mock_call_llm_api):
        # Setup mock
        mock_call_llm_api.return_value = {
            "title": "Factory Test Title",
            "summary": "Factory Test Summary"
        }
        
        # Create strategy using factory
        strategy = StrategyFactory.create(
            "TestStrategy",
            {"provider": "openrouter", "api_token": "test_token"}
        )
        
        # Test extraction
        result = await strategy.extract(
            url="https://example.com/factory",
            content="This is a test content for factory."
        )
        
        # Assertions
        self.assertEqual(result["title"], "Factory Test Title")
        self.assertEqual(result["summary"], "Factory Test Summary")
        self.assertEqual(result["test_field"], "test")
        
        # Create from config
        config = {
            "strategy": "TestStrategy",
            "params": {
                "provider": "openrouter",
                "api_token": "test_token"
            }
        }
        strategy = StrategyFactory.create_from_config(config)
        self.assertIsInstance(strategy, TestStrategy)
        
        # Create from JSON
        json_config = json.dumps(config)
        strategy = StrategyFactory.create_from_json(json_config)
        self.assertIsInstance(strategy, TestStrategy)
    
    @patch('src.cry_a_4mcp.crawl4ai.extraction_strategies.base.LLMExtractionStrategy._call_llm_api')
    async def test_composite_strategy(self, mock_call_llm_api):
        # Setup mocks for different strategies
        mock_call_llm_api.side_effect = [
            {"title": "General Title", "summary": "General Summary"},
            {"headline": "Crypto Headline", "summary": "Crypto Summary", "sentiment": "neutral"}
        ]
        
        # Create individual strategies
        general_strategy = LLMExtractionStrategy(
            provider="openrouter",
            api_token="test_token",
            instruction="Extract general information.",
            schema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "summary": {"type": "string"}
                },
                "required": ["title", "summary"]
            }
        )
        
        crypto_strategy = CryptoLLMExtractionStrategy(
            provider="openrouter",
            api_token="test_token"
        )
        
        # Create composite strategy
        composite_strategy = CompositeExtractionStrategy([
            general_strategy,
            crypto_strategy
        ])
        
        # Test extraction
        result = await composite_strategy.extract(
            url="https://example.com/composite",
            content="This is a test content for composite strategy."
        )
        
        # Assertions
        self.assertEqual(result["title"], "General Title")
        self.assertEqual(result["summary"], "Crypto Summary")  # Last strategy's value takes precedence
        self.assertEqual(result["headline"], "Crypto Headline")
        self.assertEqual(result["sentiment"], "neutral")
        
        # Verify API calls
        self.assertEqual(mock_call_llm_api.call_count, 2)


# Run the tests
def run_tests():
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add the test cases
    test_suite.addTest(unittest.makeSuite(TestExtractionStrategies))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(test_suite)


# Run the tests asynchronously
if __name__ == "__main__":
    # Get all test methods
    test_methods = [method for method in dir(TestExtractionStrategies) if method.startswith('test_')]
    
    # Create an event loop
    loop = asyncio.get_event_loop()
    
    # Run each async test method
    for method in test_methods:
        test_method = getattr(TestExtractionStrategies, method)
        if asyncio.iscoroutinefunction(test_method):
            # Create a test instance
            test_instance = TestExtractionStrategies(method)
            test_instance.setUp()
            
            # Run the test method
            try:
                loop.run_until_complete(test_method(test_instance))
                print(f"{method}: PASSED")
            except Exception as e:
                print(f"{method}: FAILED - {str(e)}")
            finally:
                test_instance.tearDown()
        else:
            # For non-async test methods, use the standard unittest runner
            suite = unittest.TestSuite()
            suite.addTest(TestExtractionStrategies(method))
            runner = unittest.TextTestRunner(verbosity=2)
            runner.run(suite)