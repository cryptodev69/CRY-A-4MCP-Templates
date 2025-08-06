#!/usr/bin/env python3
"""
Content preprocessing module for the cry_a_4mcp.crawl4ai package.

This module provides utilities for cleaning and normalizing HTML content,
segmenting large documents, and handling non-text content like tables and lists.
"""

import re
import logging
from typing import Dict, Any, Optional, List, Tuple, Union
from dataclasses import dataclass
import json

# Conditionally import BeautifulSoup if available
try:
    from bs4 import BeautifulSoup, NavigableString, Tag
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False
    logging.warning("BeautifulSoup not installed. HTML preprocessing will be limited.")

# Conditionally import html2text if available
try:
    import html2text
    HTML2TEXT_AVAILABLE = True
except ImportError:
    HTML2TEXT_AVAILABLE = False
    logging.warning("html2text not installed. HTML to markdown conversion will not be available.")

# Conditionally import trafilatura if available
try:
    import trafilatura
    TRAFILATURA_AVAILABLE = True
except ImportError:
    TRAFILATURA_AVAILABLE = False
    logging.warning("trafilatura not installed. Advanced content extraction will not be available.")

logger = logging.getLogger(__name__)


@dataclass
class TableData:
    """Represents a table extracted from HTML content."""
    headers: List[str]
    rows: List[List[str]]
    caption: Optional[str] = None

    def to_markdown(self) -> str:
        """Convert the table to markdown format.
        
        Returns:
            Markdown representation of the table
        """
        md = ""
        
        # Add caption if available
        if self.caption:
            md += f"**{self.caption}**\n\n"
        
        # Add headers
        if self.headers:
            md += "| " + " | ".join(self.headers) + " |\n"
            md += "| " + " | ".join(["---" for _ in self.headers]) + " |\n"
        
        # Add rows
        for row in self.rows:
            md += "| " + " | ".join(row) + " |\n"
        
        return md

    def to_dict(self) -> Dict[str, Any]:
        """Convert the table to a dictionary.
        
        Returns:
            Dictionary representation of the table
        """
        return {
            "caption": self.caption,
            "headers": self.headers,
            "rows": self.rows
        }


@dataclass
class ListData:
    """Represents a list extracted from HTML content."""
    items: List[str]
    ordered: bool = False
    nested: bool = False

    def to_markdown(self) -> str:
        """Convert the list to markdown format.
        
        Returns:
            Markdown representation of the list
        """
        md = ""
        
        for i, item in enumerate(self.items):
            prefix = f"{i+1}." if self.ordered else "-"
            md += f"{prefix} {item}\n"
        
        return md

    def to_dict(self) -> Dict[str, Any]:
        """Convert the list to a dictionary.
        
        Returns:
            Dictionary representation of the list
        """
        return {
            "items": self.items,
            "ordered": self.ordered,
            "nested": self.nested
        }


@dataclass
class ContentSegment:
    """Represents a segment of content after preprocessing."""
    text: str
    segment_type: str = "text"  # text, table, list, image, code, etc.
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert the segment to a dictionary.
        
        Returns:
            Dictionary representation of the segment
        """
        return {
            "text": self.text,
            "segment_type": self.segment_type,
            "metadata": self.metadata or {}
        }


@dataclass
class PreprocessedContent:
    """Represents the result of content preprocessing."""
    text: str  # Main text content
    segments: List[ContentSegment]  # Segmented content
    tables: List[TableData]  # Extracted tables
    lists: List[ListData]  # Extracted lists
    metadata: Dict[str, Any]  # Additional metadata

    def to_dict(self) -> Dict[str, Any]:
        """Convert the preprocessed content to a dictionary.
        
        Returns:
            Dictionary representation of the preprocessed content
        """
        return {
            "text": self.text,
            "segments": [segment.to_dict() for segment in self.segments],
            "tables": [table.to_dict() for table in self.tables],
            "lists": [lst.to_dict() for lst in self.lists],
            "metadata": self.metadata
        }

    def to_json(self) -> str:
        """Convert the preprocessed content to a JSON string.
        
        Returns:
            JSON string representation of the preprocessed content
        """
        return json.dumps(self.to_dict(), indent=2)

    def get_combined_text(self, include_tables: bool = True, include_lists: bool = True) -> str:
        """Get the combined text content including tables and lists if requested.
        
        Args:
            include_tables: Whether to include tables in the combined text
            include_lists: Whether to include lists in the combined text
            
        Returns:
            Combined text content
        """
        combined = self.text
        
        if include_tables:
            for table in self.tables:
                combined += "\n\n" + table.to_markdown()
        
        if include_lists:
            for lst in self.lists:
                combined += "\n\n" + lst.to_markdown()
        
        return combined


class ContentPreprocessor:
    """Preprocessor for HTML content before extraction."""

    def __init__(self, max_segment_length: int = 4000, extract_tables: bool = True,
                 extract_lists: bool = True, use_trafilatura: bool = True):
        """Initialize the content preprocessor.
        
        Args:
            max_segment_length: Maximum length of a content segment
            extract_tables: Whether to extract tables from the content
            extract_lists: Whether to extract lists from the content
            use_trafilatura: Whether to use trafilatura for content extraction
        """
        self.max_segment_length = max_segment_length
        self.extract_tables = extract_tables and BEAUTIFULSOUP_AVAILABLE
        self.extract_lists = extract_lists and BEAUTIFULSOUP_AVAILABLE
        self.use_trafilatura = use_trafilatura and TRAFILATURA_AVAILABLE
        
        # Initialize html2text converter if available
        if HTML2TEXT_AVAILABLE:
            self.html2text_converter = html2text.HTML2Text()
            self.html2text_converter.ignore_links = False
            self.html2text_converter.ignore_images = False
            self.html2text_converter.ignore_tables = False
            self.html2text_converter.body_width = 0  # No wrapping

    def clean_html(self, html: str) -> str:
        """Clean HTML content by removing scripts, styles, and comments.
        
        Args:
            html: The HTML content to clean
            
        Returns:
            Cleaned HTML content
        """
        if not BEAUTIFULSOUP_AVAILABLE:
            # Basic cleaning with regex if BeautifulSoup is not available
            html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
            html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
            html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
            return html
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove scripts, styles, and comments
            for script in soup(["script", "style"]):
                script.decompose()
            
            for comment in soup.find_all(text=lambda text: isinstance(text, NavigableString) and text.strip().startswith('<!--')):
                comment.extract()
            
            # Remove hidden elements
            for hidden in soup.find_all(style=lambda value: value and "display:none" in value):
                hidden.decompose()
            
            for hidden in soup.find_all(style=lambda value: value and "visibility:hidden" in value):
                hidden.decompose()
            
            return str(soup)
        except Exception as e:
            logger.warning(f"Error cleaning HTML: {str(e)}")
            return html

    def extract_main_content(self, html: str) -> str:
        """Extract the main content from HTML using trafilatura if available.
        
        Args:
            html: The HTML content to extract from
            
        Returns:
            Extracted main content as text
        """
        if self.use_trafilatura:
            try:
                extracted_text = trafilatura.extract(html, include_tables=True, include_links=True, include_images=True)
                if extracted_text:
                    return extracted_text
            except Exception as e:
                logger.warning(f"Error extracting content with trafilatura: {str(e)}")
        
        # Fallback to html2text if available
        if HTML2TEXT_AVAILABLE:
            try:
                return self.html2text_converter.handle(html)
            except Exception as e:
                logger.warning(f"Error converting HTML to text: {str(e)}")
        
        # Fallback to BeautifulSoup if available
        if BEAUTIFULSOUP_AVAILABLE:
            try:
                soup = BeautifulSoup(html, 'html.parser')
                return soup.get_text(separator='\n', strip=True)
            except Exception as e:
                logger.warning(f"Error extracting text with BeautifulSoup: {str(e)}")
        
        # Last resort: strip HTML tags with regex
        return re.sub(r'<[^>]+>', ' ', html)

    def extract_tables(self, html: str) -> List[TableData]:
        """Extract tables from HTML content.
        
        Args:
            html: The HTML content to extract tables from
            
        Returns:
            List of extracted tables
        """
        if not self.extract_tables or not BEAUTIFULSOUP_AVAILABLE:
            return []
        
        tables = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            for table_elem in soup.find_all('table'):
                caption = None
                caption_elem = table_elem.find('caption')
                if caption_elem:
                    caption = caption_elem.get_text(strip=True)
                
                headers = []
                header_row = table_elem.find('thead')
                if header_row:
                    headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
                
                rows = []
                for tr in table_elem.find_all('tr'):
                    # Skip header rows
                    if tr.parent and tr.parent.name == 'thead':
                        continue
                    
                    row = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
                    if row:  # Skip empty rows
                        rows.append(row)
                
                # If no headers were found but we have rows, use the first row as headers
                if not headers and rows:
                    headers = rows[0]
                    rows = rows[1:]
                
                # Only add tables with actual content
                if headers or rows:
                    tables.append(TableData(headers=headers, rows=rows, caption=caption))
        except Exception as e:
            logger.warning(f"Error extracting tables: {str(e)}")
        
        return tables

    def extract_lists(self, html: str) -> List[ListData]:
        """Extract lists from HTML content.
        
        Args:
            html: The HTML content to extract lists from
            
        Returns:
            List of extracted lists
        """
        if not self.extract_lists or not BEAUTIFULSOUP_AVAILABLE:
            return []
        
        lists = []
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            for list_elem in soup.find_all(['ul', 'ol']):
                # Skip nested lists (they'll be processed with their parent)
                if list_elem.parent and list_elem.parent.name in ['ul', 'ol', 'li']:
                    continue
                
                ordered = list_elem.name == 'ol'
                nested = False
                
                items = []
                for li in list_elem.find_all('li', recursive=False):
                    # Check if this list item contains a nested list
                    if li.find(['ul', 'ol']):
                        nested = True
                    
                    # Get the text of this list item, excluding nested lists
                    item_text = ''
                    for content in li.contents:
                        if isinstance(content, NavigableString):
                            item_text += content.strip()
                        elif isinstance(content, Tag) and content.name not in ['ul', 'ol']:
                            item_text += content.get_text(strip=True)
                    
                    items.append(item_text.strip())
                
                # Only add lists with actual content
                if items:
                    lists.append(ListData(items=items, ordered=ordered, nested=nested))
        except Exception as e:
            logger.warning(f"Error extracting lists: {str(e)}")
        
        return lists

    def segment_content(self, text: str) -> List[ContentSegment]:
        """Segment content into manageable chunks.
        
        Args:
            text: The text content to segment
            
        Returns:
            List of content segments
        """
        segments = []
        
        # Split by paragraphs first
        paragraphs = re.split(r'\n\s*\n', text)
        
        current_segment = ""
        current_segment_type = "text"
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # Determine segment type based on content
            segment_type = "text"
            if paragraph.startswith('```') and paragraph.endswith('```'):
                segment_type = "code"
            elif paragraph.startswith('# ') or paragraph.startswith('## '):
                segment_type = "heading"
            
            # If adding this paragraph would exceed the max length, or if the segment type changes,
            # start a new segment
            if len(current_segment) + len(paragraph) > self.max_segment_length or current_segment_type != segment_type:
                if current_segment:
                    segments.append(ContentSegment(
                        text=current_segment,
                        segment_type=current_segment_type
                    ))
                current_segment = paragraph
                current_segment_type = segment_type
            else:
                if current_segment:
                    current_segment += "\n\n"
                current_segment += paragraph
        
        # Add the last segment
        if current_segment:
            segments.append(ContentSegment(
                text=current_segment,
                segment_type=current_segment_type
            ))
        
        return segments

    def preprocess(self, html: str, url: Optional[str] = None) -> PreprocessedContent:
        """Preprocess HTML content for extraction.
        
        Args:
            html: The HTML content to preprocess
            url: Optional URL of the content
            
        Returns:
            Preprocessed content
        """
        # Clean HTML
        cleaned_html = self.clean_html(html)
        
        # Extract tables and lists before main content extraction
        tables = self.extract_tables(cleaned_html) if self.extract_tables else []
        lists = self.extract_lists(cleaned_html) if self.extract_lists else []
        
        # Extract main content
        main_content = self.extract_main_content(cleaned_html)
        
        # Segment content
        segments = self.segment_content(main_content)
        
        # Prepare metadata
        metadata = {
            "url": url,
            "content_length": len(main_content),
            "segment_count": len(segments),
            "table_count": len(tables),
            "list_count": len(lists)
        }
        
        return PreprocessedContent(
            text=main_content,
            segments=segments,
            tables=tables,
            lists=lists,
            metadata=metadata
        )


# Global preprocessor instance for easy access
default_preprocessor = ContentPreprocessor()


def preprocess_html(html: str, url: Optional[str] = None) -> PreprocessedContent:
    """Convenience function to preprocess HTML content.
    
    Args:
        html: The HTML content to preprocess
        url: Optional URL of the content
        
    Returns:
        Preprocessed content
    """
    return default_preprocessor.preprocess(html, url)


def clean_html(html: str) -> str:
    """Convenience function to clean HTML content.
    
    Args:
        html: The HTML content to clean
        
    Returns:
        Cleaned HTML content
    """
    return default_preprocessor.clean_html(html)


def extract_main_content(html: str) -> str:
    """Convenience function to extract main content from HTML.
    
    Args:
        html: The HTML content to extract from
        
    Returns:
        Extracted main content as text
    """
    return default_preprocessor.extract_main_content(html)