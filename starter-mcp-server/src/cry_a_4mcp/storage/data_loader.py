"""Data loader for predefined URL configurations.

This module loads predefined URL configurations from the crypto data crawler
intelligence report into the database.
"""

import logging
from typing import List, Dict, Any

from .url_configuration_db import URLConfigurationDatabase


async def load_predefined_urls(db: URLConfigurationDatabase) -> None:
    """Load predefined URL configurations into the database.
    
    Args:
        db: URLConfigurationDatabase instance
    """
    logger = logging.getLogger(__name__)
    
    # Predefined URL configurations from the research report
    predefined_configs = [
        # Degen Gambler Profile
        {
            "name": "DEXScreener",
            "url": "https://dexscreener.com",
            "profile_type": "Degen Gambler",
            "description": "Real-time DEX trading data and token discovery platform",
            "scraping_difficulty": "Medium",
            "has_official_api": True,
            "api_pricing": "Free tier: 300 requests/minute, Paid: $50-500/month",
            "recommendation": "High Priority - Essential for degen trading",
            "key_data_points": "Token prices, volume, liquidity, new listings, trending tokens",
            "target_data": "Real-time price feeds, volume spikes, new token launches",
            "rationale": "Primary platform for discovering new tokens and monitoring price movements",
            "cost_analysis": "API recommended for high-frequency data",
            "category": "DEX Analytics",
            "priority": 10
        },
        {
            "name": "PooCoin",
            "url": "https://poocoin.app",
            "profile_type": "Degen Gambler",
            "description": "BSC token charts and trading analytics",
            "scraping_difficulty": "Hard",
            "has_official_api": False,
            "api_pricing": "No official API",
            "recommendation": "Medium Priority - BSC specific",
            "key_data_points": "BSC token prices, charts, holder analysis",
            "target_data": "Price charts, holder distribution, transaction history",
            "rationale": "Popular for BSC token analysis and memecoin tracking",
            "cost_analysis": "Scraping required, moderate complexity",
            "category": "BSC Analytics",
            "priority": 7
        },
        {
            "name": "DEXTools",
            "url": "https://www.dextools.io",
            "profile_type": "Degen Gambler",
            "description": "Multi-chain DEX analytics and trading tools",
            "scraping_difficulty": "Hard",
            "has_official_api": True,
            "api_pricing": "Premium: $25-100/month",
            "recommendation": "High Priority - Multi-chain coverage",
            "key_data_points": "Multi-chain token data, trading pairs, liquidity",
            "target_data": "Cross-chain token metrics, trading opportunities",
            "rationale": "Comprehensive multi-chain DEX analytics",
            "cost_analysis": "API subscription recommended",
            "category": "Multi-chain Analytics",
            "priority": 9
        },
        {
            "name": "Birdeye",
            "url": "https://birdeye.so",
            "profile_type": "Degen Gambler",
            "description": "Solana ecosystem analytics and token discovery",
            "scraping_difficulty": "Medium",
            "has_official_api": True,
            "api_pricing": "Free tier available, Premium: $50-200/month",
            "recommendation": "High Priority - Solana focus",
            "key_data_points": "Solana token metrics, trading data, portfolio tracking",
            "target_data": "Solana token prices, volume, new launches",
            "rationale": "Leading Solana analytics platform",
            "cost_analysis": "Free tier sufficient for basic use",
            "category": "Solana Analytics",
            "priority": 8
        },
        {
            "name": "Pump.fun",
            "url": "https://pump.fun",
            "profile_type": "Degen Gambler",
            "description": "Solana memecoin launchpad and trading platform",
            "scraping_difficulty": "Medium",
            "has_official_api": False,
            "api_pricing": "No official API",
            "recommendation": "High Priority - Memecoin launches",
            "key_data_points": "New token launches, trading activity, social metrics",
            "target_data": "New memecoin launches, early trading data",
            "rationale": "Primary platform for Solana memecoin launches",
            "cost_analysis": "Scraping required, real-time monitoring needed",
            "category": "Memecoin Launchpad",
            "priority": 9
        },
        {
            "name": "GMGN.AI",
            "url": "https://gmgn.ai",
            "profile_type": "Degen Gambler",
            "description": "AI-powered crypto trading insights and alpha discovery",
            "scraping_difficulty": "Very Hard",
            "has_official_api": False,
            "api_pricing": "No official API",
            "recommendation": "Medium Priority - Alpha insights",
            "key_data_points": "AI trading signals, alpha calls, market insights",
            "target_data": "Trading signals, market predictions, alpha opportunities",
            "rationale": "AI-driven insights for trading opportunities",
            "cost_analysis": "Complex scraping, may require advanced techniques",
            "category": "AI Analytics",
            "priority": 6
        },
        
        # Gem Hunter Profile
        {
            "name": "Token Sniffer",
            "url": "https://tokensniffer.com",
            "profile_type": "Gem Hunter",
            "description": "Token security analysis and rug pull detection",
            "scraping_difficulty": "Medium",
            "has_official_api": True,
            "api_pricing": "Free tier: 100 requests/day, Paid: $20-100/month",
            "recommendation": "High Priority - Security analysis",
            "key_data_points": "Security scores, contract analysis, risk assessment",
            "target_data": "Token security ratings, contract vulnerabilities",
            "rationale": "Essential for identifying safe investment opportunities",
            "cost_analysis": "API recommended for automated screening",
            "category": "Security Analysis",
            "priority": 9
        },
        {
            "name": "Solsniffer",
            "url": "https://solsniffer.com",
            "profile_type": "Gem Hunter",
            "description": "Solana token security and analysis platform",
            "scraping_difficulty": "Medium",
            "has_official_api": False,
            "api_pricing": "No official API",
            "recommendation": "High Priority - Solana security",
            "key_data_points": "Solana token security, holder analysis, trading patterns",
            "target_data": "Security assessments, holder distribution, trading behavior",
            "rationale": "Specialized Solana token security analysis",
            "cost_analysis": "Scraping required, moderate complexity",
            "category": "Solana Security",
            "priority": 8
        },
        {
            "name": "Moralis",
            "url": "https://moralis.io",
            "profile_type": "Gem Hunter",
            "description": "Web3 development platform with comprehensive blockchain APIs",
            "scraping_difficulty": "Easy",
            "has_official_api": True,
            "api_pricing": "Free tier: 40k requests/month, Paid: $49-999/month",
            "recommendation": "High Priority - Comprehensive data",
            "key_data_points": "Multi-chain token data, NFT metadata, DeFi protocols",
            "target_data": "Token fundamentals, transaction history, wallet analysis",
            "rationale": "Comprehensive blockchain data for fundamental analysis",
            "cost_analysis": "API-first approach, cost-effective",
            "category": "Blockchain APIs",
            "priority": 9
        },
        {
            "name": "CoinLaunch",
            "url": "https://coinlaunch.space",
            "profile_type": "Gem Hunter",
            "description": "New cryptocurrency project discovery and analysis",
            "scraping_difficulty": "Medium",
            "has_official_api": False,
            "api_pricing": "No official API",
            "recommendation": "Medium Priority - Early projects",
            "key_data_points": "New project launches, ICO/IDO information, project details",
            "target_data": "Early-stage projects, launch schedules, project fundamentals",
            "rationale": "Early discovery of promising new projects",
            "cost_analysis": "Scraping required, moderate frequency",
            "category": "Project Discovery",
            "priority": 6
        },
        
        # Traditional Investor Profile
        {
            "name": "Messari",
            "url": "https://messari.io",
            "profile_type": "Traditional Investor",
            "description": "Professional crypto research and market intelligence",
            "scraping_difficulty": "Medium",
            "has_official_api": True,
            "api_pricing": "Free tier: 20 requests/minute, Pro: $24-99/month",
            "recommendation": "High Priority - Professional research",
            "key_data_points": "Market data, research reports, fundamental metrics",
            "target_data": "Market analysis, project fundamentals, industry reports",
            "rationale": "High-quality research and institutional-grade data",
            "cost_analysis": "API subscription recommended for regular use",
            "category": "Research Platform",
            "priority": 10
        },
        {
            "name": "Token Terminal",
            "url": "https://tokenterminal.com",
            "profile_type": "Traditional Investor",
            "description": "Crypto project fundamentals and financial metrics",
            "scraping_difficulty": "Medium",
            "has_official_api": True,
            "api_pricing": "Free tier available, Pro: $50-200/month",
            "recommendation": "High Priority - Fundamental analysis",
            "key_data_points": "Revenue, fees, P/E ratios, fundamental metrics",
            "target_data": "Financial metrics, valuation data, protocol economics",
            "rationale": "Traditional financial analysis applied to crypto",
            "cost_analysis": "API access recommended for comprehensive data",
            "category": "Fundamental Analysis",
            "priority": 9
        },
        {
            "name": "CryptoRank",
            "url": "https://cryptorank.io",
            "profile_type": "Traditional Investor",
            "description": "Comprehensive crypto project database and analytics",
            "scraping_difficulty": "Medium",
            "has_official_api": True,
            "api_pricing": "Free tier: 100 requests/day, Paid: $29-199/month",
            "recommendation": "High Priority - Comprehensive database",
            "key_data_points": "Project rankings, ICO data, market metrics",
            "target_data": "Project information, market data, investment rounds",
            "rationale": "Comprehensive project database for due diligence",
            "cost_analysis": "API recommended for bulk data access",
            "category": "Project Database",
            "priority": 8
        },
        {
            "name": "Glassnode",
            "url": "https://glassnode.com",
            "profile_type": "Traditional Investor",
            "description": "On-chain analytics and market intelligence",
            "scraping_difficulty": "Hard",
            "has_official_api": True,
            "api_pricing": "Free tier limited, Advanced: $39-799/month",
            "recommendation": "High Priority - On-chain analysis",
            "key_data_points": "On-chain metrics, network health, market indicators",
            "target_data": "Network activity, holder behavior, market cycles",
            "rationale": "Leading on-chain analytics for institutional investors",
            "cost_analysis": "Premium subscription required for full access",
            "category": "On-chain Analytics",
            "priority": 9
        },
        
        # DeFi Yield Farmer Profile
        {
            "name": "DeFiLlama",
            "url": "https://defillama.com",
            "profile_type": "DeFi Yield Farmer",
            "description": "DeFi TVL tracking and protocol analytics",
            "scraping_difficulty": "Easy",
            "has_official_api": True,
            "api_pricing": "Free and open source",
            "recommendation": "High Priority - Essential DeFi data",
            "key_data_points": "TVL, yield rates, protocol metrics, chain analytics",
            "target_data": "Protocol TVL, yield opportunities, chain comparisons",
            "rationale": "Most comprehensive DeFi analytics platform",
            "cost_analysis": "Free API, excellent for automation",
            "category": "DeFi Analytics",
            "priority": 10
        },
        {
            "name": "De.Fi",
            "url": "https://de.fi",
            "profile_type": "DeFi Yield Farmer",
            "description": "DeFi portfolio tracking and yield optimization",
            "scraping_difficulty": "Medium",
            "has_official_api": True,
            "api_pricing": "Free tier available, Premium features paid",
            "recommendation": "High Priority - Portfolio management",
            "key_data_points": "Portfolio tracking, yield opportunities, risk assessment",
            "target_data": "Yield rates, portfolio performance, risk metrics",
            "rationale": "Comprehensive DeFi portfolio management",
            "cost_analysis": "Free tier sufficient for basic tracking",
            "category": "Portfolio Management",
            "priority": 9
        },
        {
            "name": "APY.Vision",
            "url": "https://apy.vision",
            "profile_type": "DeFi Yield Farmer",
            "description": "Liquidity pool analytics and impermanent loss tracking",
            "scraping_difficulty": "Medium",
            "has_official_api": True,
            "api_pricing": "Free tier: 100 requests/day, Pro: $20-100/month",
            "recommendation": "High Priority - LP analysis",
            "key_data_points": "LP performance, impermanent loss, yield analysis",
            "target_data": "LP returns, IL calculations, optimal strategies",
            "rationale": "Specialized LP and yield farming analytics",
            "cost_analysis": "API recommended for detailed analysis",
            "category": "LP Analytics",
            "priority": 8
        },
        {
            "name": "Yearn Finance",
            "url": "https://yearn.fi",
            "profile_type": "DeFi Yield Farmer",
            "description": "Automated yield farming and vault strategies",
            "scraping_difficulty": "Medium",
            "has_official_api": True,
            "api_pricing": "Free API access",
            "recommendation": "High Priority - Yield strategies",
            "key_data_points": "Vault APYs, strategies, historical performance",
            "target_data": "Vault yields, strategy details, performance metrics",
            "rationale": "Leading automated yield farming platform",
            "cost_analysis": "Free API, excellent for yield tracking",
            "category": "Yield Farming",
            "priority": 9
        },
        {
            "name": "Beefy Finance",
            "url": "https://beefy.finance",
            "profile_type": "DeFi Yield Farmer",
            "description": "Multi-chain yield optimization platform",
            "scraping_difficulty": "Medium",
            "has_official_api": True,
            "api_pricing": "Free API access",
            "recommendation": "High Priority - Multi-chain yields",
            "key_data_points": "Multi-chain vault APYs, auto-compounding strategies",
            "target_data": "Cross-chain yield opportunities, vault performance",
            "rationale": "Comprehensive multi-chain yield farming",
            "cost_analysis": "Free API, good for cross-chain analysis",
            "category": "Multi-chain Yield",
            "priority": 8
        },
        {
            "name": "Dune Analytics",
            "url": "https://dune.com",
            "profile_type": "DeFi Yield Farmer",
            "description": "Blockchain data analytics and custom dashboards",
            "scraping_difficulty": "Medium",
            "has_official_api": True,
            "api_pricing": "Free tier: 1k queries/month, Plus: $390/month",
            "recommendation": "High Priority - Custom analytics",
            "key_data_points": "Custom blockchain queries, protocol analytics",
            "target_data": "Custom DeFi metrics, protocol-specific data",
            "rationale": "Powerful custom analytics for DeFi research",
            "cost_analysis": "Free tier for basic use, paid for automation",
            "category": "Custom Analytics",
            "priority": 7
        }
    ]
    
    logger.info(f"Loading {len(predefined_configs)} predefined URL configurations")
    
    for config in predefined_configs:
        try:
            # Convert string fields to appropriate types for unified schema
            config_data = {
                'name': config['name'],
                'url': config['url'],
                'profile_type': config['profile_type'],
                'category': config['category'],
                'description': config.get('description', ''),
                'priority': config.get('priority', 1),
                'scraping_difficulty': config.get('scraping_difficulty'),
                'has_official_api': config.get('has_official_api', False),
                'api_pricing': config.get('api_pricing'),
                'recommendation': config.get('recommendation'),
                'key_data_points': config.get('key_data_points', '').split(', ') if config.get('key_data_points') else [],
                'target_data': {'description': config.get('target_data', '')},
                'rationale': config.get('rationale'),
                'cost_analysis': {'description': config.get('cost_analysis', '')},
                'url_patterns': [config['url']],
                'extractor_ids': [],
                'crawler_settings': {},
                'rate_limit': 60,
                'validation_rules': {},
                'is_active': True,
                'metadata': {'source': 'predefined_configs'}
            }
            await db.create_configuration(**config_data)
        except Exception as e:
            logger.error(f"Failed to load config {config['name']}: {str(e)}")
    
    logger.info("Predefined URL configurations loaded successfully")


async def get_predefined_configs() -> List[Dict[str, Any]]:
    """Get the list of predefined configurations without loading to database.
    
    Returns:
        List of predefined configuration dictionaries
    """
    # This function can be used to preview configurations before loading
    # or for testing purposes
    return [
        # ... (same configurations as above)
        # This is a simplified version for demonstration
        {
            "name": "DEXScreener",
            "url": "https://dexscreener.com",
            "profile_type": "Degen Gambler",
            "category": "DEX Analytics",
            "priority": 10
        }
    ]