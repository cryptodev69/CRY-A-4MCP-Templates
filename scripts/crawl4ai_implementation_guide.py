"""
Universal News Crawler Implementation for CRY-A-4MCP
Using Crawl4AI for persona-based crypto news ingestion
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import LLMExtractionStrategy
import feedparser
import requests

class UniversalNewsCrawler:
    def __init__(self, config_path: str = "universal_news_crawler_config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)['universal_news_crawler']
        
        self.crawler = AsyncWebCrawler(
            verbose=True,
            headless=True,
            browser_type="chromium"
        )
        
        # AI extraction strategy for content classification
        self.extraction_strategy = LLMExtractionStrategy(
            provider="openai",
            api_token="your-openai-api-key",
            schema={
                "type": "object",
                "properties": {
                    "headline": {"type": "string"},
                    "summary": {"type": "string"},
                    "sentiment": {"type": "string", "enum": ["bullish", "bearish", "neutral"]},
                    "category": {"type": "string", "enum": ["breaking", "analysis", "regulatory", "institutional", "technical"]},
                    "persona_relevance": {
                        "type": "object",
                        "properties": {
                            "meme_snipers": {"type": "number", "minimum": 0, "maximum": 1},
                            "gem_hunters": {"type": "number", "minimum": 0, "maximum": 1},
                            "legacy_investors": {"type": "number", "minimum": 0, "maximum": 1}
                        }
                    },
                    "key_entities": {"type": "array", "items": {"type": "string"}},
                    "urgency_score": {"type": "number", "minimum": 0, "maximum": 10}
                }
            },
            instruction="Analyze this crypto news article and extract structured information including sentiment, category, and relevance to different crypto investor personas."
        )

    async def crawl_rss_feeds(self, source_config: Dict) -> List[Dict]:
        """Crawl RSS feeds for news articles"""
        articles = []
        
        for source in source_config['sources']:
            if 'rss_feed' not in source:
                continue
                
            try:
                feed = feedparser.parse(source['rss_feed'])
                
                for entry in feed.entries[:10]:  # Limit to latest 10 articles
                    article = {
                        'source': source['name'],
                        'title': entry.title,
                        'url': entry.link,
                        'published': entry.published if hasattr(entry, 'published') else None,
                        'summary': entry.summary if hasattr(entry, 'summary') else None,
                        'source_priority': source.get('priority', 'medium'),
                        'persona_relevance': source.get('persona_relevance', {})
                    }
                    articles.append(article)
                    
            except Exception as e:
                print(f"Error crawling RSS feed {source['name']}: {e}")
                
        return articles

    async def crawl_web_pages(self, articles: List[Dict]) -> List[Dict]:
        """Crawl full article content from web pages"""
        enriched_articles = []
        
        async with self.crawler as crawler:
            for article in articles:
                try:
                    result = await crawler.arun(
                        url=article['url'],
                        extraction_strategy=self.extraction_strategy,
                        bypass_cache=True
                    )
                    
                    if result.success:
                        # Parse AI extraction results
                        extracted_data = json.loads(result.extracted_content)
                        
                        article.update({
                            'full_content': result.cleaned_html,
                            'ai_analysis': extracted_data,
                            'crawl_timestamp': datetime.now().isoformat(),
                            'word_count': len(result.cleaned_html.split())
                        })
                        
                        enriched_articles.append(article)
                        
                except Exception as e:
                    print(f"Error crawling article {article['url']}: {e}")
                    
        return enriched_articles

    async def fetch_api_data(self) -> Dict:
        """Fetch data from various crypto APIs"""
        api_data = {}
        
        # Fear & Greed Index
        try:
            response = requests.get("https://api.alternative.me/fng/")
            if response.status_code == 200:
                api_data['fear_greed_index'] = response.json()
        except Exception as e:
            print(f"Error fetching Fear & Greed Index: {e}")
        
        # Bitcoin Dominance (using CoinGecko as example)
        try:
            response = requests.get("https://api.coingecko.com/api/v3/global")
            if response.status_code == 200:
                global_data = response.json()
                api_data['bitcoin_dominance'] = {
                    'btc_dominance': global_data['data']['market_cap_percentage']['btc'],
                    'total_market_cap': global_data['data']['total_market_cap']['usd'],
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            print(f"Error fetching Bitcoin Dominance: {e}")
            
        return api_data

    def route_to_personas(self, articles: List[Dict]) -> Dict[str, List[Dict]]:
        """Route articles to appropriate personas based on AI analysis"""
        persona_articles = {
            'meme_snipers': [],
            'gem_hunters': [],
            'legacy_investors': []
        }
        
        for article in articles:
            if 'ai_analysis' not in article:
                continue
                
            relevance = article['ai_analysis'].get('persona_relevance', {})
            
            # Route to personas based on relevance scores
            for persona, score in relevance.items():
                if score >= 0.6:  # Threshold for relevance
                    persona_articles[persona].append({
                        **article,
                        'relevance_score': score,
                        'routing_reason': f"AI relevance score: {score}"
                    })
        
        return persona_articles

    async def run_crawl_cycle(self) -> Dict:
        """Execute a complete crawl cycle"""
        print(f"Starting crawl cycle at {datetime.now()}")
        
        all_articles = []
        
        # Crawl Tier 1 sources (highest priority)
        tier1_articles = await self.crawl_rss_feeds(self.config['tier_1_crypto_news'])
        all_articles.extend(tier1_articles)
        
        # Crawl Tier 2 sources
        tier2_articles = await self.crawl_rss_feeds(self.config['tier_2_crypto_news'])
        all_articles.extend(tier2_articles)
        
        # Crawl mainstream financial news
        mainstream_articles = await self.crawl_rss_feeds(self.config['mainstream_financial_news'])
        all_articles.extend(mainstream_articles)
        
        # Enrich articles with full content and AI analysis
        enriched_articles = await self.crawl_web_pages(all_articles[:50])  # Limit for demo
        
        # Fetch API data
        api_data = await self.fetch_api_data()
        
        # Route articles to personas
        persona_routing = self.route_to_personas(enriched_articles)
        
        return {
            'crawl_timestamp': datetime.now().isoformat(),
            'total_articles_found': len(all_articles),
            'articles_processed': len(enriched_articles),
            'persona_routing': persona_routing,
            'market_indicators': api_data,
            'crawl_summary': {
                'meme_snipers_articles': len(persona_routing['meme_snipers']),
                'gem_hunters_articles': len(persona_routing['gem_hunters']),
                'legacy_investors_articles': len(persona_routing['legacy_investors'])
            }
        }

# Example usage and scheduler
class CrawlScheduler:
    def __init__(self):
        self.crawler = UniversalNewsCrawler()
        
    async def run_continuous_crawling(self):
        """Run continuous crawling with different frequencies for different sources"""
        while True:
            try:
                # High-frequency crawl (every 2 minutes) for breaking news
                if datetime.now().minute % 2 == 0:
                    results = await self.crawler.run_crawl_cycle()
                    await self.process_results(results)
                
                # Medium-frequency crawl (every 15 minutes) for analysis
                if datetime.now().minute % 15 == 0:
                    await self.crawl_analysis_sources()
                
                # Low-frequency crawl (hourly) for macro data
                if datetime.now().minute == 0:
                    await self.crawl_macro_sources()
                    
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                print(f"Error in crawl cycle: {e}")
                await asyncio.sleep(60)
    
    async def process_results(self, results: Dict):
        """Process and store crawl results"""
        print(f"Processed {results['articles_processed']} articles")
        print(f"Persona distribution: {results['crawl_summary']}")
        
        # Here you would typically:
        # 1. Store results in database
        # 2. Send alerts for breaking news
        # 3. Update persona-specific feeds
        # 4. Trigger downstream processing
        
        # Example: Save to JSON file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(f"crawl_results_{timestamp}.json", 'w') as f:
            json.dump(results, f, indent=2)

# Main execution
async def main():
    """Main execution function"""
    scheduler = CrawlScheduler()
    
    # Run a single crawl cycle for testing
    print("Running single crawl cycle...")
    results = await scheduler.crawler.run_crawl_cycle()
    await scheduler.process_results(results)
    
    # Uncomment to run continuous crawling
    # print("Starting continuous crawling...")
    # await scheduler.run_continuous_crawling()

if __name__ == "__main__":
    asyncio.run(main())

# Additional utility functions for specific use cases

def setup_crawl4ai_config():
    """Setup Crawl4AI with optimal configuration for crypto news"""
    return {
        "browser_type": "chromium",
        "headless": True,
        "page_timeout": 30000,
        "navigation_timeout": 30000,
        "wait_for": "networkidle",
        "delay_before_return_html": 2.0,
        "js_code": [
            "window.scrollTo(0, document.body.scrollHeight);",
            "await new Promise(resolve => setTimeout(resolve, 2000));"
        ],
        "css_selector": "article, .article-content, .post-content, main",
        "word_count_threshold": 100,
        "excluded_tags": ['nav', 'footer', 'aside', 'advertisement'],
        "remove_overlay_elements": True
    }

def get_priority_sources_for_persona(persona: str) -> List[str]:
    """Get priority news sources for specific persona"""
    priority_mapping = {
        'meme_snipers': [
            'Cointelegraph', 'CryptoPotato', 'U.Today', 'CoinGape'
        ],
        'gem_hunters': [
            'CoinDesk', 'The Block', 'Messari Research', 'Bankless'
        ],
        'legacy_investors': [
            'Bloomberg Crypto', 'Reuters Crypto', 'Wall Street Journal Crypto',
            'Federal Reserve Press Releases'
        ]
    }
    return priority_mapping.get(persona, [])

