"""Comprehensive LLM extraction strategy.

This module provides a composite extraction strategy that combines multiple
domain-specific strategies to extract a comprehensive set of information from content
that may span multiple domains.
"""

import logging
from typing import Dict, Any, List, Optional, Union, Tuple
import asyncio
from datetime import datetime

from ..factory import CompositeExtractionStrategy
from ..registry import register_strategy, StrategyRegistry
from ..factory import StrategyFactory

logger = logging.getLogger(__name__)


@register_strategy(
    name="ComprehensiveLLMExtractionStrategy",
    description="Composite strategy that combines multiple domain-specific strategies",
    category="composite"
)
class ComprehensiveLLMExtractionStrategy(CompositeExtractionStrategy):
    """Comprehensive LLM extraction strategy.
    
    This strategy combines multiple domain-specific strategies to extract a comprehensive
    set of information from content that may span multiple domains. It uses content
    classification to determine which strategies to apply and then merges the results.
    
    Attributes:
        strategies (List[ExtractionStrategy]): List of extraction strategies to use.
        content_classifier (Optional[Callable]): Function to classify content type.
        merge_mode (str): How to merge results from multiple strategies.
    """
    
    def __init__(
        self,
        api_token: Optional[str] = None,
        model: Optional[str] = None,
        strategies: Optional[List[str]] = None,
        merge_mode: str = "smart",
        max_retries: int = 3,
        retry_delay: float = 1.0,
        timeout: float = 60.0,
        **kwargs
    ):
        """Initialize the ComprehensiveLLMExtractionStrategy.
        
        Args:
            api_token: The API token for the LLM provider.
            model: The model to use for extraction.
            strategies: List of strategy names to use. If None, uses a default set.
            merge_mode: How to merge results from multiple strategies.
                Options: "smart" (intelligently merge), "union" (include all fields),
                "intersection" (include only common fields).
            max_retries: Maximum number of retries for API calls.
            retry_delay: Delay between retries in seconds.
            timeout: Timeout for API calls in seconds.
            **kwargs: Additional keyword arguments.
        """
        # Define default strategies if none provided
        default_strategies = [
            "CryptoLLMExtractionStrategy",
            "NewsLLMExtractionStrategy",
            "SocialMediaLLMExtractionStrategy",
            "ProductLLMExtractionStrategy",
            "FinancialLLMExtractionStrategy",
            "AcademicLLMExtractionStrategy"
        ]
        
        strategy_names = strategies or default_strategies
        
        # Initialize strategy instances using the factory
        factory = StrategyFactory()
        strategy_instances = []
        
        for strategy_name in strategy_names:
            try:
                strategy = factory.create_strategy(
                    strategy_name,
                    api_token=api_token,
                    model=model,
                    max_retries=max_retries,
                    retry_delay=retry_delay,
                    timeout=timeout,
                    **kwargs
                )
                strategy_instances.append(strategy)
            except Exception as e:
                logger.warning(f"Failed to initialize strategy {strategy_name}: {e}")
        
        if not strategy_instances:
            raise ValueError("No valid strategies could be initialized")
        
        # Initialize the base class
        super().__init__(
            strategies=strategy_instances,
            merge_mode=merge_mode
        )
        
        self.content_classifier = self._classify_content
    
    async def extract(self, url: str, content: str, **kwargs) -> Dict[str, Any]:
        """Extract structured information from content using multiple strategies.
        
        This method first classifies the content to determine which strategies to apply,
        then applies the selected strategies and merges the results.
        
        Args:
            url: The URL of the content.
            content: The content to extract information from.
            **kwargs: Additional keyword arguments.
            
        Returns:
            A dictionary containing the merged extracted information.
            
        Raises:
            ExtractionError: If extraction fails.
        """
        # Classify content to determine which strategies to prioritize
        content_types, confidence_scores = self._classify_content(content)
        
        # Filter strategies based on content classification
        selected_strategies = self._select_strategies(content_types, confidence_scores)
        
        if not selected_strategies:
            logger.warning("No suitable strategies selected for content")
            # Fall back to using all strategies
            selected_strategies = self.strategies
        
        # Extract information using selected strategies
        results = []
        errors = []
        
        extraction_tasks = []
        for strategy in selected_strategies:
            task = asyncio.create_task(
                self._safe_extract(strategy, url, content, **kwargs)
            )
            extraction_tasks.append(task)
        
        # Wait for all extraction tasks to complete
        completed_tasks = await asyncio.gather(*extraction_tasks)
        
        for result, error in completed_tasks:
            if result:
                results.append(result)
            if error:
                errors.append(error)
        
        if not results:
            if errors:
                logger.error(f"All extraction strategies failed: {errors}")
                raise Exception(f"All extraction strategies failed: {errors}")
            return {}
        
        # Merge results from all strategies
        merged_result = self._merge_results(results, content_types, confidence_scores)
        
        # Add metadata about the extraction process
        if "_metadata" not in merged_result:
            merged_result["_metadata"] = {}
        
        merged_result["_metadata"].update({
            "strategy": "ComprehensiveLLMExtractionStrategy",
            "strategy_version": "1.0.0",
            "extraction_timestamp": datetime.utcnow().isoformat(),
            "source_url": url,
            "content_types": content_types,
            "confidence_scores": confidence_scores,
            "strategies_used": [strategy.__class__.__name__ for strategy in selected_strategies],
            "successful_strategies": [result.get("_metadata", {}).get("strategy", "unknown") for result in results],
            "failed_strategies": len(errors)
        })
        
        return merged_result
    
    async def _safe_extract(self, strategy, url, content, **kwargs) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Safely extract information using a strategy, catching any exceptions.
        
        Args:
            strategy: The extraction strategy to use.
            url: The URL of the content.
            content: The content to extract information from.
            **kwargs: Additional keyword arguments.
            
        Returns:
            A tuple containing the extraction result (or None) and an error message (or None).
        """
        try:
            result = await strategy.extract(url, content, **kwargs)
            return result, None
        except Exception as e:
            logger.error(f"Extraction failed with strategy {strategy.__class__.__name__}: {e}")
            return None, str(e)
    
    def _classify_content(self, content: str) -> Tuple[List[str], Dict[str, float]]:
        """Classify content to determine its type and domain.
        
        This is a simple keyword-based classification that could be replaced
        with a more sophisticated ML-based approach in the future.
        
        Args:
            content: The content to classify.
            
        Returns:
            A tuple containing a list of content types and a dictionary of confidence scores.
        """
        # Define keywords for different content types
        content_type_keywords = {
            "news": [
                "breaking", "reported", "announced", "according to", "sources", "officials",
                "statement", "press release", "news", "update", "latest", "developing story"
            ],
            "social_media": [
                "posted", "shared", "tweeted", "commented", "liked", "followers", "friends",
                "social media", "platform", "profile", "status", "timeline", "feed", "trending"
            ],
            "product": [
                "product", "price", "discount", "shipping", "warranty", "review", "rating",
                "specification", "feature", "model", "brand", "manufacturer", "in stock", "sold out"
            ],
            "financial": [
                "market", "stock", "investor", "trading", "price", "financial", "economy",
                "economic", "investment", "fund", "portfolio", "dividend", "earnings", "profit",
                "revenue", "fiscal", "quarter", "annual", "report"
            ],
            "crypto": [
                "crypto", "bitcoin", "ethereum", "blockchain", "token", "coin", "mining",
                "wallet", "exchange", "defi", "nft", "smart contract", "transaction", "ledger"
            ],
            "academic": [
                "research", "study", "paper", "journal", "publication", "author", "abstract",
                "methodology", "findings", "conclusion", "hypothesis", "experiment", "data",
                "analysis", "literature", "citation", "reference", "peer-reviewed"
            ]
        }
        
        # Count keyword occurrences for each content type
        content_lower = content.lower()
        scores = {content_type: 0 for content_type in content_type_keywords}
        
        for content_type, keywords in content_type_keywords.items():
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    scores[content_type] += 1
        
        # Normalize scores to get confidence values
        total_matches = sum(scores.values())
        if total_matches == 0:
            # If no keywords matched, default to equal probability for all types
            confidence = {content_type: 1.0 / len(content_type_keywords) for content_type in content_type_keywords}
        else:
            confidence = {content_type: score / total_matches for content_type, score in scores.items()}
        
        # Sort content types by confidence score
        sorted_types = sorted(confidence.items(), key=lambda x: x[1], reverse=True)
        
        # Return top content types (those with non-zero confidence)
        content_types = [content_type for content_type, score in sorted_types if score > 0]
        
        return content_types, confidence
    
    def _select_strategies(self, content_types: List[str], confidence_scores: Dict[str, float]) -> List[Any]:
        """Select appropriate strategies based on content classification.
        
        Args:
            content_types: List of identified content types.
            confidence_scores: Dictionary of confidence scores for each content type.
            
        Returns:
            List of selected extraction strategies.
        """
        # Map content types to strategy classes
        content_type_to_strategy = {
            "news": "NewsLLMExtractionStrategy",
            "social_media": "SocialMediaLLMExtractionStrategy",
            "product": "ProductLLMExtractionStrategy",
            "financial": "FinancialLLMExtractionStrategy",
            "crypto": "CryptoLLMExtractionStrategy",
            "academic": "AcademicLLMExtractionStrategy"
        }
        
        # Select strategies for the top content types
        selected_strategy_names = set()
        
        # First, add strategies for content types with high confidence
        threshold = 0.2  # Confidence threshold for including a strategy
        for content_type, score in confidence_scores.items():
            if score >= threshold and content_type in content_type_to_strategy:
                selected_strategy_names.add(content_type_to_strategy[content_type])
        
        # If no strategies meet the threshold, use the top 2 content types
        if not selected_strategy_names and content_types:
            for content_type in content_types[:2]:  # Use top 2 content types
                if content_type in content_type_to_strategy:
                    selected_strategy_names.add(content_type_to_strategy[content_type])
        
        # Find the corresponding strategy instances
        selected_strategies = []
        for strategy in self.strategies:
            if strategy.__class__.__name__ in selected_strategy_names:
                selected_strategies.append(strategy)
        
        return selected_strategies
    
    def _merge_results(self, results: List[Dict[str, Any]], content_types: List[str], confidence_scores: Dict[str, float]) -> Dict[str, Any]:
        """Merge results from multiple extraction strategies.
        
        Args:
            results: List of extraction results from different strategies.
            content_types: List of identified content types.
            confidence_scores: Dictionary of confidence scores for each content type.
            
        Returns:
            Merged extraction result.
        """
        if not results:
            return {}
        
        if len(results) == 1:
            return results[0]
        
        if self.merge_mode == "union":
            return self._merge_union(results)
        elif self.merge_mode == "intersection":
            return self._merge_intersection(results)
        else:  # "smart" merge mode
            return self._merge_smart(results, content_types, confidence_scores)
    
    def _merge_union(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge results using union strategy (include all fields).
        
        Args:
            results: List of extraction results from different strategies.
            
        Returns:
            Merged extraction result.
        """
        merged = {}
        
        # Start with the first result
        if results:
            merged.update(results[0])
        
        # Add fields from other results if they don't exist yet
        for result in results[1:]:
            for key, value in result.items():
                if key not in merged:
                    merged[key] = value
        
        return merged
    
    def _merge_intersection(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge results using intersection strategy (include only common fields).
        
        Args:
            results: List of extraction results from different strategies.
            
        Returns:
            Merged extraction result.
        """
        if not results:
            return {}
        
        # Find common keys across all results
        common_keys = set(results[0].keys())
        for result in results[1:]:
            common_keys &= set(result.keys())
        
        # Create merged result with common keys
        merged = {}
        for key in common_keys:
            # Use the value from the first result for simplicity
            merged[key] = results[0][key]
        
        return merged
    
    def _merge_smart(self, results: List[Dict[str, Any]], content_types: List[str], confidence_scores: Dict[str, float]) -> Dict[str, Any]:
        """Merge results using smart strategy (intelligently combine fields).
        
        Args:
            results: List of extraction results from different strategies.
            content_types: List of identified content types.
            confidence_scores: Dictionary of confidence scores for each content type.
            
        Returns:
            Merged extraction result.
        """
        if not results:
            return {}
        
        # Start with an empty merged result
        merged = {}
        
        # Define priority fields for each strategy type
        strategy_priority_fields = {
            "NewsLLMExtractionStrategy": [
                "headline", "summary", "key_points", "sources", "publication_date", 
                "author", "topics", "entities", "sentiment", "factual_claims"
            ],
            "SocialMediaLLMExtractionStrategy": [
                "post_text", "user", "platform", "engagement_metrics", "hashtags", 
                "mentions", "sentiment", "topics", "media_content", "urls"
            ],
            "ProductLLMExtractionStrategy": [
                "product_name", "brand", "description", "summary", "price", 
                "specifications", "features", "reviews", "availability", "images"
            ],
            "FinancialLLMExtractionStrategy": [
                "headline", "summary", "key_points", "market_impact", "financial_metrics", 
                "market_data", "companies", "cryptocurrencies", "events", "sentiment"
            ],
            "CryptoLLMExtractionStrategy": [
                "headline", "summary", "key_points", "cryptocurrencies", "blockchain_projects", 
                "market_data", "technical_analysis", "regulatory_impact", "sentiment", "events"
            ],
            "AcademicLLMExtractionStrategy": [
                "title", "abstract", "authors", "publication", "publication_date", 
                "methodology", "findings", "conclusions", "references", "keywords"
            ]
        }
        
        # Map results to their strategy types
        result_strategies = []
        for result in results:
            strategy_name = result.get("_metadata", {}).get("strategy", "unknown")
            result_strategies.append((result, strategy_name))
        
        # First, handle common fields that appear in multiple results
        common_fields = {}
        all_fields = set()
        
        for result, _ in result_strategies:
            all_fields.update(result.keys())
        
        for field in all_fields:
            if field == "_metadata":
                continue
                
            field_values = []
            for result, _ in result_strategies:
                if field in result:
                    field_values.append(result[field])
            
            if len(field_values) > 1:
                # Field appears in multiple results, need to merge
                if isinstance(field_values[0], dict):
                    # Merge dictionaries
                    merged_dict = {}
                    for val in field_values:
                        if isinstance(val, dict):
                            merged_dict.update(val)
                    common_fields[field] = merged_dict
                elif isinstance(field_values[0], list):
                    # Merge lists, removing duplicates
                    merged_list = []
                    for val in field_values:
                        if isinstance(val, list):
                            merged_list.extend(val)
                    # Remove duplicates while preserving order
                    seen = set()
                    common_fields[field] = [x for x in merged_list if not (x in seen or seen.add(x))]
                else:
                    # For scalar values, use the one from the highest confidence strategy
                    best_value = None
                    best_confidence = -1
                    
                    for result, strategy_name in result_strategies:
                        if field in result:
                            # Find the content type associated with this strategy
                            for content_type, strategy in [
                                ("news", "NewsLLMExtractionStrategy"),
                                ("social_media", "SocialMediaLLMExtractionStrategy"),
                                ("product", "ProductLLMExtractionStrategy"),
                                ("financial", "FinancialLLMExtractionStrategy"),
                                ("crypto", "CryptoLLMExtractionStrategy"),
                                ("academic", "AcademicLLMExtractionStrategy")
                            ]:
                                if strategy == strategy_name and content_type in confidence_scores:
                                    if confidence_scores[content_type] > best_confidence:
                                        best_confidence = confidence_scores[content_type]
                                        best_value = result[field]
                    
                    if best_value is not None:
                        common_fields[field] = best_value
        
        # Now, prioritize fields based on content types
        for content_type in content_types:
            # Map content type to strategy name
            strategy_name = None
            if content_type == "news":
                strategy_name = "NewsLLMExtractionStrategy"
            elif content_type == "social_media":
                strategy_name = "SocialMediaLLMExtractionStrategy"
            elif content_type == "product":
                strategy_name = "ProductLLMExtractionStrategy"
            elif content_type == "financial":
                strategy_name = "FinancialLLMExtractionStrategy"
            elif content_type == "crypto":
                strategy_name = "CryptoLLMExtractionStrategy"
            elif content_type == "academic":
                strategy_name = "AcademicLLMExtractionStrategy"
            
            if not strategy_name:
                continue
                
            # Find result from this strategy
            for result, result_strategy_name in result_strategies:
                if result_strategy_name == strategy_name:
                    # Add priority fields from this strategy
                    priority_fields = strategy_priority_fields.get(strategy_name, [])
                    for field in priority_fields:
                        if field in result and field not in merged:
                            merged[field] = result[field]
        
        # Add common fields
        for field, value in common_fields.items():
            if field not in merged:
                merged[field] = value
        
        # Add remaining fields from all results
        for result, _ in result_strategies:
            for field, value in result.items():
                if field != "_metadata" and field not in merged:
                    merged[field] = value
        
        # Merge metadata
        merged["_metadata"] = {}
        for result, _ in result_strategies:
            if "_metadata" in result and isinstance(result["_metadata"], dict):
                for key, value in result["_metadata"].items():
                    if key not in merged["_metadata"] and key not in ["strategy", "strategy_version", "extraction_timestamp"]:
                        merged["_metadata"][key] = value
        
        return merged