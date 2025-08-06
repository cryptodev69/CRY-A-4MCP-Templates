"""Sequential LLM extraction strategy.

This module provides a workflow extraction strategy that processes content
through a sequence of extraction steps, where each step can use the results
of previous steps to improve extraction quality.
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
    name="SequentialLLMExtractionStrategy",
    description="Workflow strategy that processes content through sequential extraction steps",
    category="workflow"
)
class SequentialLLMExtractionStrategy(CompositeExtractionStrategy):
    """Sequential LLM extraction strategy.
    
    This strategy processes content through a sequence of extraction steps,
    where each step can use the results of previous steps to improve extraction quality.
    
    Attributes:
        strategies (List[ExtractionStrategy]): Ordered list of extraction strategies to apply.
        pass_results (bool): Whether to pass results from previous steps to subsequent steps.
    """
    
    def __init__(
        self,
        api_token: Optional[str] = None,
        model: Optional[str] = None,
        strategies: Optional[List[str]] = None,
        pass_results: bool = True,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        timeout: float = 60.0,
        **kwargs
    ):
        """Initialize the SequentialLLMExtractionStrategy.
        
        Args:
            api_token: The API token for the LLM provider.
            model: The model to use for extraction.
            strategies: Ordered list of strategy names to apply. If None, uses a default sequence.
            pass_results: Whether to pass results from previous steps to subsequent steps.
            max_retries: Maximum number of retries for API calls.
            retry_delay: Delay between retries in seconds.
            timeout: Timeout for API calls in seconds.
            **kwargs: Additional keyword arguments.
        """
        # Define default strategies if none provided
        default_strategies = [
            "GeneralLLMExtractionStrategy",  # First get general information
            "CryptoLLMExtractionStrategy",   # Then domain-specific extraction
            "FinancialLLMExtractionStrategy"
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
        super().__init__(strategies=strategy_instances)
        
        self.pass_results = pass_results
    
    async def extract(self, url: str, content: str, **kwargs) -> Dict[str, Any]:
        """Extract structured information from content using sequential strategies.
        
        This method applies each strategy in sequence, optionally passing results
        from previous steps to subsequent steps.
        
        Args:
            url: The URL of the content.
            content: The content to extract information from.
            **kwargs: Additional keyword arguments.
            
        Returns:
            A dictionary containing the extracted information.
            
        Raises:
            ExtractionError: If extraction fails.
        """
        logger.info(f"Starting sequential extraction for URL: {url}")
        
        # Apply each strategy in sequence
        combined_result = {}
        errors = []
        
        for i, strategy in enumerate(self.strategies):
            try:
                logger.info(f"Applying strategy {i+1}/{len(self.strategies)}: {strategy.__class__.__name__}")
                
                # Pass combined results to subsequent strategies if enabled
                if self.pass_results and combined_result and i > 0:
                    # Create a copy of kwargs and add previous results
                    step_kwargs = kwargs.copy()
                    step_kwargs["previous_results"] = combined_result
                    result = await strategy.extract(url, content, **step_kwargs)
                else:
                    result = await strategy.extract(url, content, **kwargs)
                
                # Merge the result with the combined result
                combined_result = self._merge_step_result(combined_result, result, i)
                
            except Exception as e:
                logger.error(f"Strategy {i+1}/{len(self.strategies)} failed: {str(e)}")
                errors.append({
                    "strategy": strategy.__class__.__name__,
                    "error": str(e)
                })
                # Continue with other strategies even if one fails
        
        # Add metadata about the extraction process
        if "_metadata" not in combined_result:
            combined_result["_metadata"] = {}
        
        combined_result["_metadata"].update({
            "strategy": "SequentialLLMExtractionStrategy",
            "strategy_version": "1.0.0",
            "extraction_timestamp": datetime.utcnow().isoformat(),
            "source_url": url,
            "strategies_used": [strategy.__class__.__name__ for strategy in self.strategies],
            "errors": errors
        })
        
        logger.info(f"Completed sequential extraction for URL: {url}")
        return combined_result
    
    def _merge_step_result(self, combined_result: Dict[str, Any], step_result: Dict[str, Any], step_index: int) -> Dict[str, Any]:
        """Merge the result of a step with the combined result.
        
        This method merges the result of a step with the combined result,
        handling conflicts and preserving metadata.
        
        Args:
            combined_result: The combined result so far.
            step_result: The result of the current step.
            step_index: The index of the current step.
            
        Returns:
            The merged result.
        """
        if not combined_result:
            return step_result.copy()
        
        # Create a copy of the combined result
        merged = combined_result.copy()
        
        # Merge metadata
        if "_metadata" in step_result:
            if "_metadata" not in merged:
                merged["_metadata"] = {}
            
            for key, value in step_result["_metadata"].items():
                if key not in merged["_metadata"]:
                    merged["_metadata"][key] = value
                elif isinstance(value, dict) and isinstance(merged["_metadata"][key], dict):
                    # Recursively merge dictionaries
                    merged["_metadata"][key].update(value)
        
        # Add step-specific metadata
        if "_metadata" not in merged:
            merged["_metadata"] = {}
        
        if "steps" not in merged["_metadata"]:
            merged["_metadata"]["steps"] = []
        
        merged["_metadata"]["steps"].append({
            "strategy": self.strategies[step_index].__class__.__name__,
            "step_index": step_index,
            "fields_added": [k for k in step_result.keys() if k != "_metadata" and k not in combined_result]
        })
        
        # Merge other fields, preferring later steps for conflicts
        for key, value in step_result.items():
            if key == "_metadata":
                continue
            
            if key not in merged:
                merged[key] = value
            elif isinstance(value, list) and isinstance(merged[key], list):
                # Combine lists, avoiding duplicates
                merged[key] = list(set(merged[key] + value))
            elif isinstance(value, dict) and isinstance(merged[key], dict):
                # Recursively merge dictionaries
                merged[key].update(value)
            else:
                # For conflicts, prefer the result from the later step
                merged[key] = value
        
        return merged