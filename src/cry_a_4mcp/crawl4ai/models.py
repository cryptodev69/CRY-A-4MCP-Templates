#!/usr/bin/env python3
"""
Data models for the cry_a_4mcp.crawl4ai package.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class CrawlResult:
    """
    Represents the result of crawling a web page.
    This is a placeholder implementation to satisfy imports in universal_news_crawler.py.
    """
    url: str
    title: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    llm_extraction: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the crawl result to a dictionary.
        
        Returns:
            Dictionary representation of the crawl result
        """
        return {
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "metadata": self.metadata,
            "llm_extraction": self.llm_extraction
        }