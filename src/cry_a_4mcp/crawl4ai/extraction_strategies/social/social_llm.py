"""Social media-specific LLM extraction strategy.

This module provides a specialized extraction strategy for social media content,
focusing on extracting structured information from posts, comments, and profiles.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

from ..base import LLMExtractionStrategy
from ..registry import register_strategy

logger = logging.getLogger(__name__)


@register_strategy(
    name="SocialMediaLLMExtractionStrategy",
    description="Extraction strategy for social media content",
    category="social"
)
class SocialMediaLLMExtractionStrategy(LLMExtractionStrategy):
    """Social media-specific LLM extraction strategy.
    
    This strategy is specialized for extracting structured information from social media content,
    including posts, comments, threads, user profiles, and engagement metrics.
    
    Attributes:
        provider (str): The LLM provider to use (e.g., "openrouter", "openai").
        api_token (str): The API token for the LLM provider.
        model (str): The model to use for extraction.
        instruction (str): The instruction for the LLM.
        schema (dict): The JSON schema for the extraction result.
        max_retries (int): Maximum number of retries for API calls.
        retry_delay (float): Delay between retries in seconds.
        timeout (float): Timeout for API calls in seconds.
    """
    
    # Define the default schema for social media extraction as a class attribute
    SCHEMA = {
        "type": "object",
        "properties": {
            "content_type": {
                "type": "string",
                "enum": ["post", "comment", "thread", "profile", "story", "other"],
                "description": "Type of social media content"
            },
            "platform": {
                "type": "string",
                "description": "Social media platform (e.g., Twitter, Facebook, Instagram, LinkedIn)"
            },
            "main_text": {
                "type": "string",
                "description": "The main text content of the post or comment"
            },
            "summary": {
                "type": "string",
                "description": "A concise summary of the content (1-2 sentences)"
            },
            "author": {
                "type": "object",
                "properties": {
                    "username": {"type": "string"},
                    "display_name": {"type": "string"},
                    "verified": {"type": "boolean"},
                    "follower_count": {"type": "integer"},
                    "description": {"type": "string"}
                },
                "description": "Information about the content author"
            },
            "hashtags": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Hashtags used in the content"
            },
            "mentions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "User mentions in the content"
            },
            "urls": {
                "type": "array",
                "items": {"type": "string"},
                "description": "URLs shared in the content"
            },
            "media": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "enum": ["image", "video", "gif", "audio", "other"]},
                        "description": {"type": "string"},
                        "url": {"type": "string"}
                    }
                },
                "description": "Media attached to the content"
            },
            "engagement": {
                "type": "object",
                "properties": {
                    "likes": {"type": "integer"},
                    "shares": {"type": "integer"},
                    "comments": {"type": "integer"},
                    "views": {"type": "integer"}
                },
                "description": "Engagement metrics for the content"
            },
            "sentiment": {
                "type": "string",
                "enum": ["positive", "negative", "neutral", "mixed"],
                "description": "Overall sentiment of the content"
            },
            "topics": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Main topics covered in the content"
            },
            "entities": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "type": {"type": "string"},
                        "relevance": {"type": "number", "minimum": 0, "maximum": 1}
                    },
                    "required": ["name", "type"]
                },
                "description": "Entities mentioned in the content (people, organizations, products, etc.)"
            },
            "timestamp": {
                "type": "string",
                "format": "date-time",
                "description": "Timestamp of when the content was posted"
            },
            "location": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "coordinates": {
                        "type": "object",
                        "properties": {
                            "latitude": {"type": "number"},
                            "longitude": {"type": "number"}
                        }
                    }
                },
                "description": "Location information if available"
            },
            "is_reply": {
                "type": "boolean",
                "description": "Whether the content is a reply to another post"
            },
            "reply_to": {
                "type": "string",
                "description": "Username of the user being replied to"
            },
            "thread_context": {
                "type": "string",
                "description": "Context of the thread this content belongs to"
            },
            "virality_score": {
                "type": "integer",
                "minimum": 1,
                "maximum": 10,
                "description": "Estimated virality potential on a scale of 1-10"
            },
            "promotional": {
                "type": "boolean",
                "description": "Whether the content appears to be promotional or sponsored"
            }
        },
        "required": ["content_type", "platform", "main_text", "sentiment"]
    }
    
    # Define the default instruction for social media extraction as a class attribute
    INSTRUCTION = """
    Extract structured information from the provided social media content.
    Identify the type of content (post, comment, thread, profile, story) and the platform it's from.
    Extract the main text content and create a concise summary.
    Identify information about the author including username, display name, and verification status if available.
    Extract hashtags, user mentions, and URLs shared in the content.
    Describe any media attached to the content.
    Note engagement metrics (likes, shares, comments, views) if available.
    Determine the overall sentiment of the content.
    Identify main topics discussed and entities mentioned.
    Extract timestamp and location information if available.
    Determine if the content is a reply and provide context about the thread.
    Estimate the virality potential on a scale of 1-10.
    Identify if the content appears to be promotional or sponsored.
    
    Ensure the extraction is objective and based solely on the content provided.
    Do not include information not present in the content.
    """
    
    def __init__(
        self,
        provider: str = "openrouter",
        api_token: Optional[str] = None,
        model: Optional[str] = None,
        instruction: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        timeout: float = 30.0,
        **kwargs
    ):
        """Initialize the SocialMediaLLMExtractionStrategy.
        
        Args:
            provider: The LLM provider to use (e.g., "openrouter", "openai").
            api_token: The API token for the LLM provider.
            model: The model to use for extraction.
            instruction: Custom instruction for the LLM (overrides default).
            schema: Custom JSON schema (overrides default).
            max_retries: Maximum number of retries for API calls.
            retry_delay: Delay between retries in seconds.
            timeout: Timeout for API calls in seconds.
            **kwargs: Additional keyword arguments.
        """
        # Define the default schema for social media extraction
        social_schema = schema or {
            "type": "object",
            "properties": {
                "content_type": {
                    "type": "string",
                    "enum": ["post", "comment", "thread", "profile", "story", "other"],
                    "description": "Type of social media content"
                },
                "platform": {
                    "type": "string",
                    "description": "Social media platform (e.g., Twitter, Facebook, Instagram, LinkedIn)"
                },
                "main_text": {
                    "type": "string",
                    "description": "The main text content of the post or comment"
                },
                "summary": {
                    "type": "string",
                    "description": "A concise summary of the content (1-2 sentences)"
                },
                "author": {
                    "type": "object",
                    "properties": {
                        "username": {"type": "string"},
                        "display_name": {"type": "string"},
                        "verified": {"type": "boolean"},
                        "follower_count": {"type": "integer"},
                        "description": {"type": "string"}
                    },
                    "description": "Information about the content author"
                },
                "hashtags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Hashtags used in the content"
                },
                "mentions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "User mentions in the content"
                },
                "urls": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "URLs shared in the content"
                },
                "media": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["image", "video", "gif", "audio", "other"]},
                            "description": {"type": "string"},
                            "url": {"type": "string"}
                        }
                    },
                    "description": "Media attached to the content"
                },
                "engagement": {
                    "type": "object",
                    "properties": {
                        "likes": {"type": "integer"},
                        "shares": {"type": "integer"},
                        "comments": {"type": "integer"},
                        "views": {"type": "integer"}
                    },
                    "description": "Engagement metrics for the content"
                },
                "sentiment": {
                    "type": "string",
                    "enum": ["positive", "negative", "neutral", "mixed"],
                    "description": "Overall sentiment of the content"
                },
                "topics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Main topics covered in the content"
                },
                "entities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "type": {"type": "string"},
                            "relevance": {"type": "number", "minimum": 0, "maximum": 1}
                        },
                        "required": ["name", "type"]
                    },
                    "description": "Entities mentioned in the content (people, organizations, products, etc.)"
                },
                "timestamp": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Timestamp of when the content was posted"
                },
                "location": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "coordinates": {
                            "type": "object",
                            "properties": {
                                "latitude": {"type": "number"},
                                "longitude": {"type": "number"}
                            }
                        }
                    },
                    "description": "Location information if available"
                },
                "is_reply": {
                    "type": "boolean",
                    "description": "Whether the content is a reply to another post"
                },
                "reply_to": {
                    "type": "string",
                    "description": "Username of the user being replied to"
                },
                "thread_context": {
                    "type": "string",
                    "description": "Context of the thread this content belongs to"
                },
                "virality_score": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10,
                    "description": "Estimated virality potential on a scale of 1-10"
                },
                "promotional": {
                    "type": "boolean",
                    "description": "Whether the content appears to be promotional or sponsored"
                }
            },
            "required": ["content_type", "platform", "main_text", "sentiment"]
        }
        
        # Define the default instruction for social media extraction
        social_instruction = instruction or """
        Extract structured information from the provided social media content.
        Identify the type of content (post, comment, thread, profile, story) and the platform it's from.
        Extract the main text content and create a concise summary.
        Identify information about the author including username, display name, and verification status if available.
        Extract hashtags, user mentions, and URLs shared in the content.
        Describe any media attached to the content.
        Note engagement metrics (likes, shares, comments, views) if available.
        Determine the overall sentiment of the content.
        Identify main topics discussed and entities mentioned.
        Extract timestamp and location information if available.
        Determine if the content is a reply and provide context about the thread.
        Estimate the virality potential on a scale of 1-10.
        Identify if the content appears to be promotional or sponsored.
        
        Ensure the extraction is objective and based solely on the content provided.
        Do not include information not present in the content.
        """
        
        # Initialize the base class
        super().__init__(
            provider=provider,
            api_token=api_token,
            model=model,
            instruction=social_instruction,
            schema=social_schema,
            max_retries=max_retries,
            retry_delay=retry_delay,
            timeout=timeout,
            **kwargs
        )
    
    async def extract(self, url: str, content: str, **kwargs) -> Dict[str, Any]:
        """Extract structured information from social media content.
        
        Args:
            url: The URL of the content.
            content: The content to extract information from.
            **kwargs: Additional keyword arguments.
            
        Returns:
            A dictionary containing the extracted information.
            
        Raises:
            ExtractionError: If extraction fails.
        """
        # Call the base class extract method
        result = await super().extract(url, content, **kwargs)
        
        # Perform social media-specific post-processing
        if result:
            result = self._validate_social_extraction(result)
            result = self._enhance_social_extraction(result, url)
            result = self._detect_platform(result, url, content)
        
        return result
    
    def _validate_social_extraction(self, extraction: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the social media extraction result.
        
        Args:
            extraction: The extraction result to validate.
            
        Returns:
            The validated extraction result.
        """
        # Check for required fields
        required_fields = ["content_type", "platform", "main_text", "sentiment"]
        for field in required_fields:
            if field not in extraction:
                logger.warning(f"Required field '{field}' missing from extraction result")
                if field == "content_type":
                    extraction["content_type"] = "other"
                elif field == "platform":
                    extraction["platform"] = "unknown"
                elif field == "main_text":
                    extraction["main_text"] = "No content available."
                elif field == "sentiment":
                    extraction["sentiment"] = "neutral"
        
        # Validate content_type value
        valid_content_types = ["post", "comment", "thread", "profile", "story", "other"]
        if extraction.get("content_type") not in valid_content_types:
            logger.warning(f"Invalid content_type value: {extraction.get('content_type')}")
            extraction["content_type"] = "other"
        
        # Validate sentiment value
        valid_sentiments = ["positive", "negative", "neutral", "mixed"]
        if extraction.get("sentiment") not in valid_sentiments:
            logger.warning(f"Invalid sentiment value: {extraction.get('sentiment')}")
            extraction["sentiment"] = "neutral"
        
        # Validate virality_score
        if "virality_score" in extraction:
            try:
                score = int(extraction["virality_score"])
                if score < 1 or score > 10:
                    logger.warning(f"Invalid virality_score: {score}")
                    extraction["virality_score"] = max(1, min(10, score))
            except (ValueError, TypeError):
                logger.warning(f"Invalid virality_score: {extraction.get('virality_score')}")
                extraction["virality_score"] = 5
        
        # Ensure hashtags is a list
        if "hashtags" in extraction and not isinstance(extraction["hashtags"], list):
            if isinstance(extraction["hashtags"], str):
                # Try to convert string to list by splitting
                hashtags = extraction["hashtags"].split()
                extraction["hashtags"] = [h.strip("#") for h in hashtags if h.strip()]
            else:
                extraction["hashtags"] = []
        
        # Ensure mentions is a list
        if "mentions" in extraction and not isinstance(extraction["mentions"], list):
            if isinstance(extraction["mentions"], str):
                # Try to convert string to list by splitting
                mentions = extraction["mentions"].split()
                extraction["mentions"] = [m.strip("@") for m in mentions if m.strip()]
            else:
                extraction["mentions"] = []
        
        return extraction
    
    def _enhance_social_extraction(self, extraction: Dict[str, Any], url: str) -> Dict[str, Any]:
        """Enhance the social media extraction result with additional information.
        
        Args:
            extraction: The extraction result to enhance.
            url: The URL of the content.
            
        Returns:
            The enhanced extraction result.
        """
        # Add metadata
        if "_metadata" not in extraction:
            extraction["_metadata"] = {}
        
        extraction["_metadata"].update({
            "strategy": "SocialMediaLLMExtractionStrategy",
            "strategy_version": "1.0.0",
            "extraction_timestamp": datetime.utcnow().isoformat(),
            "source_url": url
        })
        
        # Ensure author is an object
        if "author" not in extraction or not isinstance(extraction["author"], dict):
            extraction["author"] = {}
        
        # Ensure engagement is an object
        if "engagement" not in extraction or not isinstance(extraction["engagement"], dict):
            extraction["engagement"] = {}
        
        # Ensure hashtags is a list
        if "hashtags" not in extraction:
            extraction["hashtags"] = []
        
        # Ensure mentions is a list
        if "mentions" not in extraction:
            extraction["mentions"] = []
        
        # Ensure urls is a list
        if "urls" not in extraction:
            extraction["urls"] = []
        
        # Ensure media is a list
        if "media" not in extraction:
            extraction["media"] = []
        
        # Ensure topics is a list
        if "topics" not in extraction:
            extraction["topics"] = []
        
        # Ensure entities is a list
        if "entities" not in extraction:
            extraction["entities"] = []
        
        # Set default values for boolean fields
        if "is_reply" not in extraction:
            extraction["is_reply"] = False
        
        if "promotional" not in extraction:
            extraction["promotional"] = False
        
        # Set default virality_score if not present
        if "virality_score" not in extraction:
            extraction["virality_score"] = 5
        
        # Add summary if not present
        if "summary" not in extraction and "main_text" in extraction:
            # Create a simple summary by truncating the main text
            text = extraction["main_text"]
            if len(text) > 100:
                extraction["summary"] = text[:97] + "..."
            else:
                extraction["summary"] = text
        
        return extraction
    
    def _detect_platform(self, extraction: Dict[str, Any], url: str, content: str) -> Dict[str, Any]:
        """Attempt to detect the social media platform if not already identified.
        
        Args:
            extraction: The extraction result.
            url: The URL of the content.
            content: The original content.
            
        Returns:
            The updated extraction result.
        """
        if extraction.get("platform") not in [None, "", "unknown"]:
            return extraction
        
        # Try to detect platform from URL
        platform_domains = {
            "twitter.com": "Twitter",
            "x.com": "Twitter",
            "facebook.com": "Facebook",
            "instagram.com": "Instagram",
            "linkedin.com": "LinkedIn",
            "reddit.com": "Reddit",
            "tiktok.com": "TikTok",
            "youtube.com": "YouTube",
            "pinterest.com": "Pinterest",
            "threads.net": "Threads",
            "mastodon": "Mastodon",  # Generic for various Mastodon instances
            "tumblr.com": "Tumblr",
            "snapchat.com": "Snapchat",
            "weibo.com": "Weibo",
            "vk.com": "VK",
            "telegram.org": "Telegram",
            "discord.com": "Discord",
            "whatsapp.com": "WhatsApp"
        }
        
        for domain, platform_name in platform_domains.items():
            if domain in url.lower():
                extraction["platform"] = platform_name
                return extraction
        
        # If platform still not detected, try to infer from content patterns
        content_lower = content.lower()
        
        # Look for platform-specific patterns
        if any(term in content_lower for term in ["tweet", "retweet", "rt @"]):
            extraction["platform"] = "Twitter"
        elif any(term in content_lower for term in ["posted on facebook", "facebook post", "fb post"]):
            extraction["platform"] = "Facebook"
        elif any(term in content_lower for term in ["instagram post", "insta", "ig post"]):
            extraction["platform"] = "Instagram"
        elif any(term in content_lower for term in ["subreddit", "upvote", "downvote", "r/"]):
            extraction["platform"] = "Reddit"
        elif any(term in content_lower for term in ["tiktok", "tiktok video"]):
            extraction["platform"] = "TikTok"
        elif any(term in content_lower for term in ["youtube", "yt video", "subscribe", "channel"]):
            extraction["platform"] = "YouTube"
        elif any(term in content_lower for term in ["linkedin", "connection", "professional network"]):
            extraction["platform"] = "LinkedIn"
        
        return extraction