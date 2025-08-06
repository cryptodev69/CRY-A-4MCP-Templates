#!/usr/bin/env python3
"""
Data loader for URL configurations based on the Crypto Data Crawler Intelligence Report.

This script populates the URL configuration database with predefined URLs and metadata
for different trader profiles (Degen Gambler, Gem Hunter, Traditional Investor, DeFi Yield Farmer).
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cry_a_4mcp.crawl4ai.url_configs.database.url_config_db import URLConfigDatabase

def get_predefined_url_configs():
    """Get predefined URL configurations from the research report.
    
    Returns:
        List of URL configuration dictionaries
    """
    configs = [
        # Degen Gambler Profile URLs
        {
            'name': 'DEXScreener',
            'url': 'https://dexscreener.com',
            'profile_type': 'Degen Gambler',
            'description': 'Real-time DEX trading data and token discovery platform',
            'scraping_difficulty': 3,
            'has_official_api': True,
            'api_pricing': 'Free tier: 300 requests/minute, Pro: $50/month for 1000 req/min',
            'recommendation': 'Use official API for reliable data access',
            'key_data_points': [
                'Token prices and volume',
                'Liquidity pools',
                'Trading pairs',
                'Price charts',
                'Market cap data'
            ],
            'target_data': [
                'New token listings',
                'Volume spikes',
                'Price movements',
                'Liquidity changes'
            ],
            'rationale': 'Essential for tracking new tokens and quick price movements',
            'cost_analysis': 'API recommended for high-volume usage',
            'category': 'DEX Analytics',
            'priority': 5
        },
        {
            'name': 'PooCoin',
            'url': 'https://poocoin.app',
            'profile_type': 'Degen Gambler',
            'description': 'BSC token charts and trading analytics',
            'scraping_difficulty': 4,
            'has_official_api': False,
            'api_pricing': 'No official API',
            'recommendation': 'Scraping required, use rotating proxies',
            'key_data_points': [
                'BSC token prices',
                'Trading volume',
                'Holder analytics',
                'Rug pull warnings',
                'Token security scores'
            ],
            'target_data': [
                'New BSC tokens',
                'Rug pull alerts',
                'Holder distribution',
                'Trading patterns'
            ],
            'rationale': 'Critical for BSC token safety and discovery',
            'cost_analysis': 'Scraping costs moderate, consider proxy rotation',
            'category': 'BSC Analytics',
            'priority': 4
        },
        {
            'name': 'DEXTools',
            'url': 'https://www.dextools.io',
            'profile_type': 'Degen Gambler',
            'description': 'Multi-chain DEX analytics and trading tools',
            'scraping_difficulty': 4,
            'has_official_api': True,
            'api_pricing': 'Premium: $25/month for API access',
            'recommendation': 'API access recommended for reliable data',
            'key_data_points': [
                'Multi-chain token data',
                'DEX trading analytics',
                'Pool information',
                'Token security analysis',
                'Social sentiment'
            ],
            'target_data': [
                'Cross-chain opportunities',
                'Security alerts',
                'Trading volume trends',
                'New pool creation'
            ],
            'rationale': 'Comprehensive multi-chain DEX analytics',
            'cost_analysis': 'API subscription cost-effective for regular use',
            'category': 'Multi-chain DEX',
            'priority': 4
        },
        {
            'name': 'Birdeye',
            'url': 'https://birdeye.so',
            'profile_type': 'Degen Gambler',
            'description': 'Solana ecosystem analytics and trading data',
            'scraping_difficulty': 3,
            'has_official_api': True,
            'api_pricing': 'Free tier available, Pro plans from $99/month',
            'recommendation': 'Use API for Solana-focused trading',
            'key_data_points': [
                'Solana token prices',
                'DEX analytics',
                'Portfolio tracking',
                'Market trends',
                'Token metadata'
            ],
            'target_data': [
                'Solana token opportunities',
                'DEX volume data',
                'Price alerts',
                'Market movements'
            ],
            'rationale': 'Best-in-class Solana ecosystem analytics',
            'cost_analysis': 'API pricing reasonable for Solana focus',
            'category': 'Solana Analytics',
            'priority': 4
        },
        {
            'name': 'Pump.fun',
            'url': 'https://pump.fun',
            'profile_type': 'Degen Gambler',
            'description': 'Solana meme coin launchpad and trading platform',
            'scraping_difficulty': 5,
            'has_official_api': False,
            'api_pricing': 'No official API',
            'recommendation': 'Scraping required, high difficulty due to anti-bot measures',
            'key_data_points': [
                'New meme coin launches',
                'Trading volume',
                'Creator information',
                'Community engagement',
                'Price progression'
            ],
            'target_data': [
                'Early meme coin opportunities',
                'Launch notifications',
                'Volume spikes',
                'Community sentiment'
            ],
            'rationale': 'Primary source for Solana meme coin discovery',
            'cost_analysis': 'High scraping complexity, consider specialized tools',
            'category': 'Meme Coins',
            'priority': 3
        },
        {
            'name': 'GMGN.AI',
            'url': 'https://gmgn.ai',
            'profile_type': 'Degen Gambler',
            'description': 'AI-powered crypto trading signals and analytics',
            'scraping_difficulty': 4,
            'has_official_api': False,
            'api_pricing': 'No official API',
            'recommendation': 'Scraping required, monitor for API development',
            'key_data_points': [
                'AI trading signals',
                'Market predictions',
                'Token analysis',
                'Risk assessments',
                'Performance metrics'
            ],
            'target_data': [
                'Trading signals',
                'AI predictions',
                'Risk alerts',
                'Performance data'
            ],
            'rationale': 'AI-driven insights for trading decisions',
            'cost_analysis': 'Scraping complexity moderate, valuable data',
            'category': 'AI Analytics',
            'priority': 3
        },
        
        # Gem Hunter Profile URLs
        {
            'name': 'Token Sniffer',
            'url': 'https://tokensniffer.com',
            'profile_type': 'Gem Hunter',
            'description': 'Token security analysis and rug pull detection',
            'scraping_difficulty': 3,
            'has_official_api': True,
            'api_pricing': 'Free tier: 100 requests/day, Pro: $29/month',
            'recommendation': 'API recommended for security analysis',
            'key_data_points': [
                'Token security scores',
                'Contract analysis',
                'Rug pull indicators',
                'Audit results',
                'Risk assessments'
            ],
            'target_data': [
                'Security alerts',
                'Contract vulnerabilities',
                'Risk scores',
                'Audit status'
            ],
            'rationale': 'Essential for token security verification',
            'cost_analysis': 'API cost-effective for security focus',
            'category': 'Security Analysis',
            'priority': 5
        },
        {
            'name': 'Solsniffer',
            'url': 'https://solsniffer.com',
            'profile_type': 'Gem Hunter',
            'description': 'Solana token security and analysis platform',
            'scraping_difficulty': 3,
            'has_official_api': False,
            'api_pricing': 'No official API currently',
            'recommendation': 'Scraping required, monitor for API release',
            'key_data_points': [
                'Solana token security',
                'Contract verification',
                'Holder analysis',
                'Liquidity assessment',
                'Risk indicators'
            ],
            'target_data': [
                'Solana security alerts',
                'Contract risks',
                'Holder patterns',
                'Liquidity risks'
            ],
            'rationale': 'Specialized Solana security analysis',
            'cost_analysis': 'Scraping moderate complexity',
            'category': 'Solana Security',
            'priority': 4
        },
        {
            'name': 'Moralis',
            'url': 'https://moralis.io',
            'profile_type': 'Gem Hunter',
            'description': 'Web3 development platform with comprehensive APIs',
            'scraping_difficulty': 1,
            'has_official_api': True,
            'api_pricing': 'Free tier: 40k requests/month, Pro: $49/month',
            'recommendation': 'Use API for comprehensive blockchain data',
            'key_data_points': [
                'Multi-chain token data',
                'NFT analytics',
                'DeFi protocols',
                'Wallet analytics',
                'Transaction history'
            ],
            'target_data': [
                'Token metadata',
                'Wallet movements',
                'DeFi interactions',
                'NFT trends'
            ],
            'rationale': 'Comprehensive Web3 data infrastructure',
            'cost_analysis': 'Excellent API value for comprehensive data',
            'category': 'Web3 Infrastructure',
            'priority': 5
        },
        {
            'name': 'Messari',
            'url': 'https://messari.io',
            'profile_type': 'Gem Hunter',
            'description': 'Crypto research and market intelligence platform',
            'scraping_difficulty': 3,
            'has_official_api': True,
            'api_pricing': 'Free tier limited, Pro: $29/month, Enterprise: Custom',
            'recommendation': 'API recommended for research data',
            'key_data_points': [
                'Project fundamentals',
                'Market research',
                'Token metrics',
                'Team information',
                'Roadmap analysis'
            ],
            'target_data': [
                'Project research',
                'Fundamental analysis',
                'Market insights',
                'Team backgrounds'
            ],
            'rationale': 'High-quality research for gem identification',
            'cost_analysis': 'API subscription valuable for research focus',
            'category': 'Research Platform',
            'priority': 4
        },
        
        # Traditional Investor Profile URLs
        {
            'name': 'Token Terminal',
            'url': 'https://tokenterminal.com',
            'profile_type': 'Traditional Investor',
            'description': 'Crypto project fundamentals and financial metrics',
            'scraping_difficulty': 2,
            'has_official_api': True,
            'api_pricing': 'Free tier available, Pro: $49/month',
            'recommendation': 'API recommended for fundamental analysis',
            'key_data_points': [
                'Revenue metrics',
                'P/E ratios',
                'TVL data',
                'User metrics',
                'Financial KPIs'
            ],
            'target_data': [
                'Financial performance',
                'Valuation metrics',
                'Growth indicators',
                'Competitive analysis'
            ],
            'rationale': 'Essential for fundamental crypto analysis',
            'cost_analysis': 'API provides excellent value for institutional analysis',
            'category': 'Fundamental Analysis',
            'priority': 5
        },
        {
            'name': 'CryptoRank',
            'url': 'https://cryptorank.io',
            'profile_type': 'Traditional Investor',
            'description': 'Crypto analytics and market data platform',
            'scraping_difficulty': 3,
            'has_official_api': True,
            'api_pricing': 'Free tier: 100 requests/day, Pro: $99/month',
            'recommendation': 'API recommended for comprehensive market data',
            'key_data_points': [
                'Market rankings',
                'Price data',
                'Volume analytics',
                'Market cap trends',
                'Exchange data'
            ],
            'target_data': [
                'Market positions',
                'Ranking changes',
                'Volume trends',
                'Exchange flows'
            ],
            'rationale': 'Comprehensive market analytics for institutional use',
            'cost_analysis': 'API pricing reasonable for institutional data needs',
            'category': 'Market Analytics',
            'priority': 4
        },
        {
            'name': 'Nansen',
            'url': 'https://nansen.ai',
            'profile_type': 'Traditional Investor',
            'description': 'On-chain analytics and wallet intelligence platform',
            'scraping_difficulty': 5,
            'has_official_api': True,
            'api_pricing': 'Alpha: $150/month, Pro: $500/month, Enterprise: Custom',
            'recommendation': 'API required, premium pricing for institutional features',
            'key_data_points': [
                'Wallet analytics',
                'On-chain flows',
                'Smart money tracking',
                'Token holder analysis',
                'DeFi analytics'
            ],
            'target_data': [
                'Institutional flows',
                'Smart money movements',
                'Whale activities',
                'Market sentiment'
            ],
            'rationale': 'Premium on-chain intelligence for institutional investors',
            'cost_analysis': 'High-value data justifies premium pricing',
            'category': 'On-chain Analytics',
            'priority': 5
        },
        {
            'name': 'Glassnode',
            'url': 'https://glassnode.com',
            'profile_type': 'Traditional Investor',
            'description': 'On-chain market intelligence and analytics',
            'scraping_difficulty': 2,
            'has_official_api': True,
            'api_pricing': 'Free tier limited, Advanced: $39/month, Professional: $799/month',
            'recommendation': 'API essential for on-chain metrics',
            'key_data_points': [
                'On-chain metrics',
                'Network health',
                'Market indicators',
                'Institutional flows',
                'Long-term trends'
            ],
            'target_data': [
                'Network fundamentals',
                'Market cycles',
                'Institutional adoption',
                'Long-term indicators'
            ],
            'rationale': 'Industry-standard on-chain analytics',
            'cost_analysis': 'Professional tier valuable for institutional analysis',
            'category': 'On-chain Metrics',
            'priority': 5
        },
        
        # DeFi Yield Farmer Profile URLs
        {
            'name': 'DeFiLlama',
            'url': 'https://defillama.com',
            'profile_type': 'DeFi Yield Farmer',
            'description': 'DeFi TVL and protocol analytics platform',
            'scraping_difficulty': 2,
            'has_official_api': True,
            'api_pricing': 'Free API with rate limits',
            'recommendation': 'Use free API for TVL and protocol data',
            'key_data_points': [
                'Protocol TVL',
                'Yield rates',
                'Chain analytics',
                'Protocol rankings',
                'Historical data'
            ],
            'target_data': [
                'TVL changes',
                'Yield opportunities',
                'Protocol growth',
                'Chain migration'
            ],
            'rationale': 'Essential for DeFi protocol discovery and analysis',
            'cost_analysis': 'Free API provides excellent value',
            'category': 'DeFi Analytics',
            'priority': 5
        },
        {
            'name': 'De.Fi',
            'url': 'https://de.fi',
            'profile_type': 'DeFi Yield Farmer',
            'description': 'DeFi portfolio management and yield optimization',
            'scraping_difficulty': 4,
            'has_official_api': False,
            'api_pricing': 'No official API',
            'recommendation': 'Scraping required, complex due to dynamic content',
            'key_data_points': [
                'Yield farming opportunities',
                'Portfolio tracking',
                'Risk assessments',
                'APY calculations',
                'Protocol integrations'
            ],
            'target_data': [
                'High-yield opportunities',
                'Risk-adjusted returns',
                'Portfolio optimization',
                'Yield strategies'
            ],
            'rationale': 'Comprehensive yield farming intelligence',
            'cost_analysis': 'Scraping complexity high but valuable data',
            'category': 'Yield Optimization',
            'priority': 4
        },
        {
            'name': 'APY.Vision',
            'url': 'https://apy.vision',
            'profile_type': 'DeFi Yield Farmer',
            'description': 'Liquidity pool analytics and impermanent loss tracking',
            'scraping_difficulty': 3,
            'has_official_api': False,
            'api_pricing': 'No official API',
            'recommendation': 'Scraping required for LP analytics',
            'key_data_points': [
                'LP performance',
                'Impermanent loss',
                'Yield calculations',
                'Pool analytics',
                'Historical returns'
            ],
            'target_data': [
                'LP opportunities',
                'IL risk assessment',
                'Pool performance',
                'Yield optimization'
            ],
            'rationale': 'Specialized LP and impermanent loss analysis',
            'cost_analysis': 'Scraping moderate complexity for specialized data',
            'category': 'LP Analytics',
            'priority': 4
        },
        {
            'name': 'Yearn Finance',
            'url': 'https://yearn.finance',
            'profile_type': 'DeFi Yield Farmer',
            'description': 'Automated yield farming and vault strategies',
            'scraping_difficulty': 3,
            'has_official_api': True,
            'api_pricing': 'Free API available',
            'recommendation': 'Use API for vault data and strategies',
            'key_data_points': [
                'Vault performance',
                'Strategy details',
                'APY data',
                'Risk metrics',
                'Historical yields'
            ],
            'target_data': [
                'Vault opportunities',
                'Strategy performance',
                'Risk-adjusted yields',
                'Automated strategies'
            ],
            'rationale': 'Leading automated yield farming platform',
            'cost_analysis': 'Free API provides excellent value',
            'category': 'Automated Yield',
            'priority': 4
        },
        {
            'name': 'Beefy Finance',
            'url': 'https://beefy.finance',
            'profile_type': 'DeFi Yield Farmer',
            'description': 'Multi-chain yield optimization platform',
            'scraping_difficulty': 3,
            'has_official_api': True,
            'api_pricing': 'Free API available',
            'recommendation': 'Use API for multi-chain yield data',
            'key_data_points': [
                'Multi-chain vaults',
                'APY optimization',
                'Auto-compounding',
                'Risk assessments',
                'Chain analytics'
            ],
            'target_data': [
                'Cross-chain opportunities',
                'Optimized yields',
                'Auto-compound strategies',
                'Chain comparisons'
            ],
            'rationale': 'Multi-chain yield optimization leader',
            'cost_analysis': 'Free API excellent for multi-chain strategies',
            'category': 'Multi-chain Yield',
            'priority': 4
        }
    ]
    
    return configs

def load_url_configs():
    """Load predefined URL configurations into the database."""
    try:
        # Initialize database
        db = URLConfigDatabase()
        
        # Get predefined configurations
        configs = get_predefined_url_configs()
        
        # Bulk insert configurations
        inserted_count = db.bulk_insert_configs(configs)
        
        print(f"Successfully loaded {inserted_count} URL configurations into the database.")
        print(f"Database location: {db.db_path}")
        
        # Print summary by profile type
        profile_types = db.get_profile_types()
        print("\nLoaded configurations by profile type:")
        for profile_type in profile_types:
            count = len(db.get_all_url_configs(profile_type=profile_type))
            print(f"  {profile_type}: {count} URLs")
        
        db.close()
        
    except Exception as e:
        print(f"Error loading URL configurations: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Loading URL configurations from Crypto Data Crawler Intelligence Report...")
    success = load_url_configs()
    if success:
        print("\nURL configurations loaded successfully!")
    else:
        print("\nFailed to load URL configurations.")
        sys.exit(1)