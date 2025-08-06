#!/usr/bin/env python3
"""
Monitoring Demo for CRY-A-4MCP

This script demonstrates how to use the monitoring system with a sample extraction service.
It simulates extractions with different content types and quality levels to generate metrics.

Usage:
    python monitoring_demo.py [--port PORT] [--duration SECONDS]

Options:
    --port PORT       Port to run the metrics server on (default: 8000)
    --duration SEC    Duration to run the demo in seconds (default: 60)

Example:
    python monitoring_demo.py --port 8000 --duration 120
"""

import asyncio
import argparse
import logging
import random
import time
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import the metrics integration
try:
    from cry_a_4mcp.monitoring.extraction_metrics_integration import track_extraction
    from cry_a_4mcp.monitoring.metrics_exporter import start_metrics_server
    METRICS_AVAILABLE = True
except ImportError:
    logger.warning("Metrics modules not found. Running without metrics tracking.")
    METRICS_AVAILABLE = False
    
    # Define a dummy decorator if metrics are not available
    def track_extraction(func):
        return func
    
    def start_metrics_server(port=8000):
        logger.warning(f"Metrics server would start on port {port} if available.")

# Sample content for different content types
SAMPLE_CONTENTS = {
    "CRYPTO": [
        """
        Bitcoin ETFs Finally Approved by SEC After Decade-Long Battle
        
        The U.S. Securities and Exchange Commission has approved spot Bitcoin exchange-traded funds,
        marking a historic moment for the cryptocurrency industry after a decade-long battle for acceptance.
        
        The approval allows financial giants like BlackRock, Fidelity, and Grayscale to offer investment
        products that directly track Bitcoin's price, potentially opening the cryptocurrency to millions
        of traditional investors.
        """,
        """
        Ethereum Completes Successful Merge to Proof-of-Stake
        
        Ethereum has successfully completed its transition from proof-of-work to proof-of-stake in an upgrade
        known as "The Merge." This historic update reduces Ethereum's energy consumption by approximately 99.95%
        and sets the stage for future scalability improvements.
        
        The transition occurred when the network reached a specific Total Terminal Difficulty (TTD) threshold,
        at which point mining was no longer required to produce new blocks.
        """,
        """
        Ripple Wins Partial Victory in SEC Case as Judge Rules XRP Not a Security
        
        In a landmark decision for the cryptocurrency industry, a federal judge has ruled that Ripple's XRP
        token is not a security when sold to the general public on digital asset exchanges, dealing a significant
        blow to the SEC's regulatory approach to cryptocurrencies.
        
        The ruling distinguishes between institutional sales of XRP, which the court found could be considered
        securities offerings, and sales to retail investors on exchanges, which do not qualify as investment contracts.
        """
    ],
    "NEWS": [
        """
        Federal Reserve Holds Interest Rates Steady, Signals Potential Cuts Later This Year
        
        The Federal Reserve kept its benchmark interest rate unchanged at the latest policy meeting, maintaining
        the target range at 5.25% to 5.5%. Fed Chair Jerome Powell indicated that the central bank is prepared
        to begin cutting rates later this year if inflation continues to move toward the 2% target.
        
        Markets reacted positively to the news, with major indices climbing and Treasury yields falling as
        investors anticipated an eventual easing of monetary policy.
        """,
        """
        Tech Giants Report Strong Quarterly Earnings Amid AI Boom
        
        Major technology companies including Microsoft, Google, and NVIDIA reported better-than-expected
        quarterly earnings, driven largely by growing demand for artificial intelligence products and services.
        
        Microsoft's cloud revenue surged 29%, while Google's parent company Alphabet saw advertising revenue
        increase by 11%. NVIDIA, whose chips power many AI applications, reported a 125% year-over-year
        increase in revenue.
        """,
        """
        Global Climate Summit Ends with New Commitments to Reduce Emissions
        
        The latest international climate conference concluded with several major economies announcing new
        targets for reducing greenhouse gas emissions. The United States pledged to cut emissions by 50-52%
        below 2005 levels by 2030, while the European Union reaffirmed its commitment to become carbon-neutral
        by 2050.
        
        The summit also saw increased financial commitments to help developing nations transition to cleaner
        energy sources and adapt to climate change impacts.
        """
    ],
    "SOCIAL_MEDIA": [
        """
        @CryptoAnalyst: Just looked at the $BTC chart and we're seeing a classic cup and handle formation.
        This is typically bullish and could signal a breakout above $50k soon. NFA but I'm loading up! 🚀
        
        @TradingExpert: Disagree. Volume doesn't support this move and RSI is overbought on 4h. Expecting
        a pullback to $42k before any sustainable move higher. #Bitcoin #TechnicalAnalysis
        
        @CryptoAnalyst: Fair points but institutional inflows tell a different story. BlackRock's ETF
        alone brought in $500M yesterday. This isn't retail FOMO, it's smart money positioning.
        """,
        """
        r/Cryptocurrency - What's your most undervalued altcoin pick for 2023?
        
        u/BlockchainDeveloper: I think ATOM is still flying under the radar. The Cosmos ecosystem
        is growing rapidly with IBC connections, and the tokenomics are improving with each upgrade.
        
        u/AltcoinTrader: ATOM has terrible tokenomics and inflation. If you want real value, look at
        projects with actual revenue like GMX or DYDX. DEXs that share revenue with holders are the future.
        
        u/CryptoNewbie: Can someone explain like I'm 5 what makes a coin "undervalued"? Is it just
        price or are there specific metrics I should be looking at?
        """,
        """
        @ETHDeveloper: Just deployed my first zkRollup on Ethereum testnet. The throughput is incredible -
        over 2000 TPS with minimal gas costs. This is the scaling solution we've been waiting for! #Ethereum #zkRollups
        
        @L2Enthusiast: Which zkRollup solution did you use? StarkNet, zkSync, or something else?
        
        @ETHDeveloper: I went with zkSync Era. Documentation is excellent and the developer experience
        is much smoother than alternatives. Happy to share my code if anyone's interested.
        """
    ]
}

# Sample extraction function with the metrics tracking decorator
@track_extraction
async def extract_content(content: str, content_type: str = "CRYPTO") -> Dict[str, Any]:
    """
    Simulate content extraction with random success/failure and metrics.
    
    Args:
        content: The content to extract from
        content_type: Type of content (CRYPTO, NEWS, SOCIAL_MEDIA)
        
    Returns:
        Extraction result with metadata
    """
    # Simulate extraction time (longer for larger content)
    content_size = len(content)
    base_extraction_time = 0.5 + (content_size / 5000)  # Base time plus size factor
    extraction_time = random.uniform(base_extraction_time, base_extraction_time * 1.5)
    await asyncio.sleep(extraction_time)
    
    # Randomly determine if extraction fails (10% chance)
    if random.random() < 0.1:
        logger.warning(f"Extraction failed for {content_type} content")
        raise Exception(f"Failed to extract {content_type} content: API error")
    
    # Generate extraction result
    token_usage = random.randint(100, 500)
    estimated_cost = token_usage * 0.00002  # $0.02 per 1000 tokens
    quality_score = random.uniform(0.6, 1.0)
    
    # Content type specific adjustments
    if content_type == "CRYPTO":
        # Crypto content has higher quality on average
        quality_score = min(1.0, quality_score + 0.1)
    elif content_type == "SOCIAL_MEDIA":
        # Social media content has more variance in quality
        quality_score = quality_score * random.uniform(0.8, 1.2)
        quality_score = max(0.0, min(1.0, quality_score))  # Clamp between 0 and 1
    
    # Generate random validation errors (20% chance)
    validation_errors = []
    if random.random() < 0.2:
        error_types = ["missing_required_field", "invalid_type", "invalid_value"]
        fields = ["source", "timestamp", "entities", "sentiment"]
        
        # Add 1-2 random errors
        for _ in range(random.randint(1, 2)):
            error_type = random.choice(error_types)
            field = random.choice(fields)
            validation_errors.append({
                "error_type": error_type,
                "field": field,
                "message": f"{error_type.replace('_', ' ').title()} for '{field}'"
            })
    
    # Create extraction result
    result = {
        "content_type": content_type,
        "timestamp": datetime.now().isoformat(),
        "entities": generate_entities(content_type),
        "sentiment": random.choice(["positive", "neutral", "negative"]),
        "summary": generate_summary(content, content_type),
        "_metadata": {
            "token_usage": token_usage,
            "estimated_cost_dollars": estimated_cost,
            "extraction_quality": quality_score,
            "extraction_time_seconds": extraction_time,
            "content_size_bytes": content_size,
            "validation_errors": validation_errors
        }
    }
    
    logger.info(f"Extracted {content_type} content with quality score: {quality_score:.2f}")
    return result


def generate_entities(content_type: str) -> List[str]:
    """
    Generate random entities based on content type.
    """
    crypto_entities = ["Bitcoin", "Ethereum", "Ripple", "Binance", "Coinbase", "SEC", "CFTC"]
    news_entities = ["Federal Reserve", "Congress", "White House", "EU", "China", "Russia", "UN"]
    social_entities = ["Twitter", "Reddit", "Discord", "Telegram", "YouTube", "TikTok"]
    
    if content_type == "CRYPTO":
        pool = crypto_entities + random.sample(news_entities, 2)
    elif content_type == "NEWS":
        pool = news_entities + random.sample(crypto_entities, 1)
    else:  # SOCIAL_MEDIA
        pool = social_entities + random.sample(crypto_entities, 2)
    
    # Return 3-5 random entities
    return random.sample(pool, random.randint(3, 5))


def generate_summary(content: str, content_type: str) -> str:
    """
    Generate a simple summary based on the content.
    """
    # Take the first sentence or two as a simple summary
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    first_paragraph = lines[0] if lines else "No content available"
    
    # Add a content type specific prefix
    prefixes = {
        "CRYPTO": "Cryptocurrency update: ",
        "NEWS": "News report: ",
        "SOCIAL_MEDIA": "Social media discussion: "
    }
    
    return f"{prefixes.get(content_type, '')}{first_paragraph}"


async def run_extraction_demo(duration: int = 60, interval: float = 2.0):
    """
    Run a demo of the extraction service with metrics tracking.
    
    Args:
        duration: Duration to run the demo in seconds
        interval: Interval between extractions in seconds
    """
    logger.info(f"Starting extraction demo for {duration} seconds")
    start_time = time.time()
    end_time = start_time + duration
    
    while time.time() < end_time:
        # Select a random content type
        content_type = random.choice(["CRYPTO", "NEWS", "SOCIAL_MEDIA"])
        
        # Select a random content for the chosen type
        content = random.choice(SAMPLE_CONTENTS[content_type])
        
        try:
            # Perform extraction
            result = await extract_content(content, content_type=content_type)
            
            # Log a summary of the result
            metadata = result.get("_metadata", {})
            logger.info(
                f"Extraction completed: {content_type} | "
                f"Quality: {metadata.get('extraction_quality', 0):.2f} | "
                f"Tokens: {metadata.get('token_usage', 0)} | "
                f"Cost: ${metadata.get('estimated_cost_dollars', 0):.5f} | "
                f"Validation Errors: {len(metadata.get('validation_errors', []))}"
            )
            
        except Exception as e:
            logger.error(f"Extraction error: {str(e)}")
        
        # Wait before next extraction
        await asyncio.sleep(interval)
    
    logger.info(f"Extraction demo completed after {time.time() - start_time:.1f} seconds")


def parse_arguments():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(description="Run a demo of the extraction service with metrics tracking")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the metrics server on")
    parser.add_argument("--duration", type=int, default=60, help="Duration to run the demo in seconds")
    parser.add_argument("--interval", type=float, default=2.0, help="Interval between extractions in seconds")
    return parser.parse_args()


async def main():
    """
    Main function to run the demo.
    """
    args = parse_arguments()
    
    # Start the metrics server if available
    if METRICS_AVAILABLE:
        start_metrics_server(port=args.port)
        logger.info(f"Metrics server started on port {args.port}")
        logger.info(f"Metrics available at: http://localhost:{args.port}/metrics")
    else:
        logger.warning("Metrics tracking not available. Running without metrics.")
    
    # Run the extraction demo
    await run_extraction_demo(duration=args.duration, interval=args.interval)
    
    # Keep the server running for a moment to allow final metrics to be scraped
    if METRICS_AVAILABLE:
        logger.info("Demo completed. Keeping metrics server running for 10 more seconds...")
        await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(main())