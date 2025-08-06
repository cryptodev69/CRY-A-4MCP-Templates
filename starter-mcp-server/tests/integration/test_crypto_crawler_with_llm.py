import asyncio
import sys
import os
import json
from typing import Dict, List, Optional
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from cry_a_4mcp.crawl4ai.crawler import CryptoCrawler
from cry_a_4mcp.crawl4ai.models import CrawlResult
on
# Import LLMExtractionStrategy from cry_a_4mcp.crawl4ai
from cry_a_4mcp.crawl4ai.extraction_strategy import LLMExtractionStrategy


class CryptoLLMExtractionStrategy(LLMExtractionStrategy):
    """Cryptocurrency-specific LLM extraction strategy.
    
    This class extends the base LLMExtractionStrategy with cryptocurrency-specific
    schema and instructions.
    """
    
    def __init__(self, provider: str, api_token: str):
        """Initialize the cryptocurrency LLM extraction strategy.
        
        Args:
            provider: LLM provider (e.g., "openai", "groq")
            api_token: API token for the LLM provider
        """
        # Define the schema for cryptocurrency content extraction
        schema = {
            "type": "object",
            "properties": {
                "headline": {"type": "string"},
                "summary": {"type": "string"},
                "sentiment": {"type": "string", "enum": ["bullish", "bearish", "neutral"]},
                "category": {"type": "string", "enum": ["breaking", "analysis", "regulatory", "institutional", "technical", "defi", "nft", "meme"]},
                "market_impact": {"type": "string", "enum": ["high", "medium", "low", "none"]},
                "key_entities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"type": "string", "enum": ["token", "exchange", "protocol", "person", "company", "regulator"]},
                            "relevance": {"type": "number", "minimum": 0, "maximum": 1}
                        }
                    }
                },
                "persona_relevance": {
                    "type": "object",
                    "properties": {
                        "meme_snipers": {"type": "number", "minimum": 0, "maximum": 1},
                        "gem_hunters": {"type": "number", "minimum": 0, "maximum": 1},
                        "legacy_investors": {"type": "number", "minimum": 0, "maximum": 1}
                    }
                },
                "urgency_score": {"type": "number", "minimum": 0, "maximum": 10},
                "price_mentions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "token": {"type": "string"},
                            "price": {"type": "string"},
                            "change": {"type": "string"}
                        }
                    }
                }
            }
        }
        
        # Define the instruction for cryptocurrency content extraction
        instruction = """
        Analyze this cryptocurrency content and extract structured information including:
        1. Headline and summary
        2. Overall sentiment (bullish, bearish, neutral)
        3. Content category (breaking, analysis, regulatory, etc.)
        4. Market impact assessment (high, medium, low, none)
        5. Key entities mentioned (tokens, exchanges, protocols, people, companies, regulators)
        6. Relevance to different crypto investor personas (meme snipers, gem hunters, legacy investors)
        7. Urgency score (0-10) indicating how time-sensitive this information is
        8. Any specific price mentions for tokens
        
        Focus on extracting factual information and avoid speculation. If certain information
        is not present in the content, omit those fields from your response.
        """
        
        # Initialize the base class
        super().__init__(
            provider=provider,
            api_token=api_token,
            schema=schema,
            instruction=instruction
        )


class CryptoCrawlerWithLLM(CryptoCrawler):
    """CryptoCrawler with LLM extraction strategy integration.
    
    This class extends the base CryptoCrawler with LLM extraction capabilities.
    """
    
    def __init__(self, config: Optional[Dict] = None, config_file_path: Optional[str] = None, llm_strategy: Optional[LLMExtractionStrategy] = None):
        """Initialize the cryptocurrency crawler with LLM extraction.
        
        Args:
            config: Optional configuration dictionary for the crawler
            config_file_path: Optional path to a JSON configuration file
            llm_strategy: Optional LLM extraction strategy
        """
        super().__init__(config=config, config_file_path=config_file_path)
        self.llm_strategy = llm_strategy
    
    async def crawl_crypto_website_with_llm(self, url: str, content_type: str, extract_entities: bool = True, generate_triples: bool = True) -> Dict:
        """Crawl a cryptocurrency website with LLM extraction.
        
        Args:
            url: The URL to crawl
            content_type: Type of content (news, blog, exchange, etc.)
            extract_entities: Whether to extract entities
            generate_triples: Whether to generate knowledge graph triples
            
        Returns:
            Dictionary containing the crawl result and LLM extraction result
        """
        if not self.initialized or not self.crawler:
            raise RuntimeError("Crawler not initialized. Call initialize() first.")
        
        if not self.llm_strategy:
            raise ValueError("LLM extraction strategy not provided. Initialize with llm_strategy parameter.")
        
        # Crawl the website using the base method
        crawl_result = await self.crawl_crypto_website(
            url=url,
            content_type=content_type,
            extract_entities=extract_entities,
            generate_triples=generate_triples
        )
        
        # Extract content using LLM if the crawl was successful
        llm_extraction = None
        if crawl_result.metadata.success and crawl_result.markdown:
            try:
                # Use the LLM extraction strategy to analyze the content
                llm_extraction = await self.llm_strategy.extract(
                    url=url,
                    html=crawl_result.markdown,  # Using markdown as HTML is not available in CrawlResult
                    instruction=self.llm_strategy.instruction,
                    schema=self.llm_strategy.schema
                )
            except Exception as e:
                print(f"Error during LLM extraction: {str(e)}")
        
        # Return both the crawl result and LLM extraction
        return {
            "crawl_result": crawl_result,
            "llm_extraction": llm_extraction
        }
    
    async def crawl_all_websites_with_llm(self, priority: Optional[str] = None, content_type: Optional[str] = None, frequency: Optional[str] = None) -> List[Dict]:
        """Crawl all websites matching the specified filters with LLM extraction.
        
        Args:
            priority: Optional priority filter (high, medium, low)
            content_type: Optional content type filter
            frequency: Optional crawl frequency filter (hourly, daily, weekly)
            
        Returns:
            List of dictionaries containing crawl results and LLM extraction results
        """
        if not self.initialized or not self.crawler:
            raise RuntimeError("Crawler not initialized. Call initialize() first.")
        
        if not self.llm_strategy:
            raise ValueError("LLM extraction strategy not provided. Initialize with llm_strategy parameter.")
        
        # Filter websites based on provided criteria
        websites_to_crawl = self.websites
        
        if priority:
            websites_to_crawl = [w for w in websites_to_crawl if w.get('priority') == priority]
        
        if content_type:
            websites_to_crawl = [w for w in websites_to_crawl if w.get('content_type') == content_type]
        
        if frequency:
            websites_to_crawl = [w for w in websites_to_crawl if w.get('crawl_frequency') == frequency]
        
        # Crawl each website with LLM extraction
        results = []
        for website in websites_to_crawl:
            try:
                result = await self.crawl_crypto_website_with_llm(
                    url=website['url'],
                    content_type=website['content_type'],
                    extract_entities=True,
                    generate_triples=True
                )
                results.append(result)
            except Exception as e:
                print(f"Error crawling {website.get('name', website.get('url'))}: {str(e)}")
        
        return results


async def test_crypto_crawler_with_llm():
    """Test the CryptoCrawlerWithLLM class."""
    # Path to the configuration file
    config_file_path = os.path.join(
        os.path.dirname(__file__),
        'src/cry_a_4mcp/crawl4ai/crypto_website_config.json'
    )
    
    print(f"Loading configuration from: {config_file_path}")
    
    # Get OpenRouter API key from environment variable
    openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")
    if not openrouter_api_key:
        print("Error: OPENROUTER_API_KEY environment variable not set")
        return
        
    # Create a CryptoLLMExtractionStrategy instance with OpenRouter
    llm_strategy = CryptoLLMExtractionStrategy(
        provider="openai",  # OpenRouter uses OpenAI-compatible API
        api_token=openrouter_api_key,
        base_url="https://openrouter.ai/api/v1"
    )
    
    # Create a CryptoCrawlerWithLLM instance
    crawler = CryptoCrawlerWithLLM(
        config_file_path=config_file_path,
        llm_strategy=llm_strategy
    )
    
    print("Created CryptoCrawlerWithLLM instance")
    
    try:
        # Initialize the crawler
        await crawler.initialize()
        print("Initialized CryptoCrawlerWithLLM")
        
        # Test crawling a specific website with LLM extraction
        website_name = "Altcoin Season Index"
        website = crawler.get_website_by_name(website_name)
        
        if website:
            print(f"\nCrawling {website_name} with LLM extraction...")
            result = await crawler.crawl_crypto_website_with_llm(
                url=website['url'],
                content_type=website['content_type'],
                extract_entities=True,
                generate_triples=True
            )
            
            # Print crawl result
            print_crawl_result(result["crawl_result"])
            
            # Print LLM extraction result
            print_llm_extraction(result["llm_extraction"])
        else:
            print(f"Website '{website_name}' not found in configuration")
        
    finally:
        # Ensure crawler is properly closed
        await crawler.close()
        print("\nCrawler closed properly")


def print_crawl_result(result: CrawlResult) -> None:
    """Print details of a crawl result."""
    print("\nCrawl Result:")
    print(f"Success: {result.metadata.success}")
    print(f"URL: {result.metadata.url}")
    print(f"Content Type: {result.metadata.content_type}")
    print(f"Content Length: {result.metadata.content_length} characters")
    print(f"Processing Time: {result.metadata.processing_time:.2f} seconds")
    print(f"Quality Score: {result.quality_score:.2f}")
    
    print("\nExtracted Entities:")
    for entity in result.entities[:5]:  # Print first 5 entities
        print(f"  - {entity.name} ({entity.entity_type}): {entity.confidence}")
    if len(result.entities) > 5:
        print(f"  ... and {len(result.entities) - 5} more entities")
    
    print("\nExtracted Triples:")
    for triple in result.triples[:5]:  # Print first 5 triples
        print(f"  - {triple.subject} {triple.predicate} {triple.object}: {triple.confidence}")
    if len(result.triples) > 5:
        print(f"  ... and {len(result.triples) - 5} more triples")


def print_llm_extraction(extraction: Optional[Dict]) -> None:
    """Print details of an LLM extraction result."""
    print("\nLLM Extraction Result:")
    if not extraction:
        print("  No LLM extraction result available")
        return
    
    # Print headline and summary
    if "headline" in extraction:
        print(f"Headline: {extraction['headline']}")
    if "summary" in extraction:
        print(f"Summary: {extraction['summary']}")
    
    # Print sentiment and category
    if "sentiment" in extraction:
        print(f"Sentiment: {extraction['sentiment']}")
    if "category" in extraction:
        print(f"Category: {extraction['category']}")
    if "market_impact" in extraction:
        print(f"Market Impact: {extraction['market_impact']}")
    
    # Print key entities
    if "key_entities" in extraction and extraction["key_entities"]:
        print("\nKey Entities:")
        for entity in extraction["key_entities"]:
            print(f"  - {entity['name']} ({entity['type']}): {entity['relevance']}")
    
    # Print persona relevance
    if "persona_relevance" in extraction:
        print("\nPersona Relevance:")
        for persona, score in extraction["persona_relevance"].items():
            print(f"  - {persona}: {score}")
    
    # Print urgency score
    if "urgency_score" in extraction:
        print(f"\nUrgency Score: {extraction['urgency_score']}/10")
    
    # Print price mentions
    if "price_mentions" in extraction and extraction["price_mentions"]:
        print("\nPrice Mentions:")
        for price in extraction["price_mentions"]:
            print(f"  - {price['token']}: {price['price']} ({price['change']})")


if __name__ == "__main__":
    asyncio.run(test_crypto_crawler_with_llm())