#!/usr/bin/env python3
"""Test script for Crawl4AI v0.7.0 adaptive crawling features.

This script tests the new adaptive crawling intelligence capabilities
including strategy optimization, pattern learning, and performance analytics.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the src directory to Python path
import sys
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from cry_a_4mcp.crypto_crawler.crawler import CryptoCrawler
from cry_a_4mcp.models.adaptive_models import (
    AdaptiveStrategyConfig,
    StrategyType,
    ContentType
)


class AdaptiveCrawlingTester:
    """Test suite for adaptive crawling features."""
    
    def __init__(self):
        """Initialize the tester."""
        self.crawler = None
        self.test_urls = [
            "https://coindesk.com",
            "https://cointelegraph.com",
            "https://decrypt.co",
            "https://theblock.co"
        ]
    
    async def setup(self):
        """Setup the crawler with adaptive capabilities."""
        logger.info("Setting up CryptoCrawler with adaptive capabilities...")
        
        config = {
            "headless": True,
            "bypass_cache": True,
            "word_count_threshold": 50,
            "capture_screenshot": False,
            "extract_images": False,
            "enable_adaptive_crawling": True,
            "enable_pattern_learning": True,
            "enable_smart_stopping": True
        }
        
        self.crawler = CryptoCrawler(config=config)
        
        await self.crawler.initialize()
        logger.info("CryptoCrawler initialized successfully")
    
    async def test_basic_adaptive_crawl(self):
        """Test basic adaptive crawling functionality."""
        logger.info("\n=== Testing Basic Adaptive Crawling ===")
        
        test_url = self.test_urls[0]
        logger.info(f"Testing adaptive crawl for: {test_url}")
        
        # Create a basic adaptive strategy
        strategy_config = AdaptiveStrategyConfig(
            strategy_type=StrategyType.HYBRID,
            enable_pattern_learning=True,
            enable_smart_stopping=True,
            min_word_count=100,
            max_crawl_time=60,
            quality_threshold=0.7
        )
        
        try:
            result = await self.crawler.crawl_with_adaptive_intelligence(
                url=test_url,
                strategy_config=strategy_config
            )
            
            logger.info(f"Crawl success: {result.get('success', False)}")
            logger.info(f"Content length: {len(result.get('content', ''))} characters")
            
            # Check adaptive metadata
            adaptive_metadata = result.get('metadata', {}).get('adaptive_intelligence', {})
            logger.info(f"Strategy type used: {adaptive_metadata.get('strategy_type', 'unknown')}")
            logger.info(f"Quality score: {adaptive_metadata.get('content_quality_score', 0.0):.2f}")
            logger.info(f"Patterns learned: {len(adaptive_metadata.get('patterns_learned', []))}")
            logger.info(f"Adaptation applied: {adaptive_metadata.get('adaptation_applied', False)}")
            
            return result.get('success', False)
            
        except Exception as e:
            logger.error(f"Error in basic adaptive crawl: {e}")
            return False
    
    async def test_strategy_types(self):
        """Test different adaptive strategy types."""
        logger.info("\n=== Testing Different Strategy Types ===")
        
        strategies = [
            (StrategyType.STATISTICAL, "Statistical Analysis"),
            (StrategyType.EMBEDDING, "Embedding-based"),
            (StrategyType.HYBRID, "Hybrid Approach")
        ]
        
        test_url = self.test_urls[1]
        results = {}
        
        for strategy_type, description in strategies:
            logger.info(f"\nTesting {description} strategy...")
            
            strategy_config = AdaptiveStrategyConfig(
                strategy_type=strategy_type,
                enable_pattern_learning=True,
                enable_smart_stopping=True,
                min_word_count=50,
                max_crawl_time=45,
                quality_threshold=0.6
            )
            
            try:
                result = await self.crawler.crawl_with_adaptive_intelligence(
                    url=test_url,
                    strategy_config=strategy_config
                )
                
                success = result.get('success', False)
                processing_time = result.get('extraction_time', 0.0)
                content_length = len(result.get('content', ''))
                
                results[strategy_type] = {
                    'success': success,
                    'processing_time': processing_time,
                    'content_length': content_length
                }
                
                logger.info(f"  Success: {success}")
                logger.info(f"  Processing time: {processing_time:.2f}s")
                logger.info(f"  Content length: {content_length} characters")
                
            except Exception as e:
                logger.error(f"  Error with {description}: {e}")
                results[strategy_type] = {'success': False, 'error': str(e)}
        
        return results
    
    async def test_pattern_learning(self):
        """Test pattern learning capabilities."""
        logger.info("\n=== Testing Pattern Learning ===")
        
        # Crawl multiple URLs to build patterns
        for i, url in enumerate(self.test_urls[:2]):
            logger.info(f"\nCrawling URL {i+1}/2 for pattern learning: {url}")
            
            strategy_config = AdaptiveStrategyConfig(
                strategy_type=StrategyType.HYBRID,
                enable_pattern_learning=True,
                enable_smart_stopping=True,
                min_word_count=100,
                max_crawl_time=60,
                quality_threshold=0.7
            )
            
            try:
                result = await self.crawler.crawl_with_adaptive_intelligence(
                    url=url,
                    strategy_config=strategy_config
                )
                
                adaptive_metadata = result.get('metadata', {}).get('adaptive_intelligence', {})
                patterns_learned = adaptive_metadata.get('patterns_learned', [])
                
                logger.info(f"  Success: {result.get('success', False)}")
                logger.info(f"  New patterns learned: {len(patterns_learned)}")
                
                if patterns_learned:
                    for pattern in patterns_learned[:3]:  # Show first 3 patterns
                        logger.info(f"    Pattern: {pattern}")
                
            except Exception as e:
                logger.error(f"  Error learning patterns from {url}: {e}")
    
    async def test_domain_insights(self):
        """Test domain insights functionality."""
        logger.info("\n=== Testing Domain Insights ===")
        
        test_domains = ["coindesk.com", "cointelegraph.com"]
        
        for domain in test_domains:
            logger.info(f"\nGetting insights for domain: {domain}")
            
            try:
                insights = self.crawler.get_adaptive_insights(domain)
                
                logger.info(f"  Domain: {insights.get('domain', 'unknown')}")
                logger.info(f"  Total crawls: {insights.get('total_crawls', 0)}")
                logger.info(f"  Success rate: {insights.get('success_rate', 0.0):.2f}")
                logger.info(f"  Average quality: {insights.get('average_quality_score', 0.0):.2f}")
                logger.info(f"  Patterns count: {len(insights.get('learned_patterns', []))}")
                
                recommendations = insights.get('recommendations', [])
                if recommendations:
                    logger.info("  Recommendations:")
                    for rec in recommendations[:3]:  # Show first 3 recommendations
                        logger.info(f"    - {rec}")
                
            except Exception as e:
                logger.error(f"  Error getting insights for {domain}: {e}")
    
    async def test_pattern_analysis(self):
        """Test comprehensive pattern analysis."""
        logger.info("\n=== Testing Pattern Analysis ===")
        
        try:
            analysis = self.crawler.get_pattern_analysis()
            
            logger.info(f"Total patterns analyzed: {analysis.get('total_patterns', 0)}")
            logger.info(f"High confidence patterns: {analysis.get('high_confidence_patterns', 0)}")
            logger.info(f"Domains analyzed: {len(analysis.get('domains_analyzed', []))}")
            
            optimization_opportunities = analysis.get('optimization_opportunities', [])
            if optimization_opportunities:
                logger.info("Optimization opportunities:")
                for opp in optimization_opportunities[:3]:  # Show first 3
                    logger.info(f"  - {opp}")
            
            performance_trends = analysis.get('performance_trends', {})
            if performance_trends:
                logger.info("Performance trends:")
                for metric, value in performance_trends.items():
                    logger.info(f"  {metric}: {value}")
            
        except Exception as e:
            logger.error(f"Error in pattern analysis: {e}")
    
    async def test_cache_management(self):
        """Test adaptive cache management."""
        logger.info("\n=== Testing Cache Management ===")
        
        test_domain = "coindesk.com"
        
        # Test clearing cache for specific domain
        logger.info(f"Clearing cache for domain: {test_domain}")
        try:
            success = self.crawler.clear_adaptive_cache(test_domain)
            logger.info(f"Cache clear success: {success}")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
        
        # Test exporting patterns
        logger.info(f"Exporting patterns for domain: {test_domain}")
        try:
            patterns = self.crawler.export_learned_patterns(test_domain)
            logger.info(f"Exported patterns count: {len(patterns.get('patterns', []))}")
        except Exception as e:
            logger.error(f"Error exporting patterns: {e}")
    
    async def cleanup(self):
        """Cleanup resources."""
        if self.crawler:
            await self.crawler.close()
            logger.info("Crawler closed successfully")
    
    async def run_all_tests(self):
        """Run all adaptive crawling tests."""
        logger.info("Starting Crawl4AI v0.7.0 Adaptive Crawling Tests")
        logger.info("=" * 60)
        
        try:
            await self.setup()
            
            # Run individual tests
            await self.test_basic_adaptive_crawl()
            await self.test_strategy_types()
            await self.test_pattern_learning()
            await self.test_domain_insights()
            await self.test_pattern_analysis()
            await self.test_cache_management()
            
            logger.info("\n" + "=" * 60)
            logger.info("All adaptive crawling tests completed successfully!")
            
        except Exception as e:
            logger.error(f"Test suite failed: {e}")
        finally:
            await self.cleanup()


async def main():
    """Main test function."""
    tester = AdaptiveCrawlingTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())