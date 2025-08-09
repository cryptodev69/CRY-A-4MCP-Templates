"""Adaptive Crawling API Endpoints Module.

This module provides RESTful API endpoints for the new adaptive crawling intelligence
features introduced in Crawl4AI v0.7.0. It enables clients to leverage machine learning
and statistical analysis for optimized web crawling strategies.

Key Features:
    - Adaptive crawling with intelligent strategy selection
    - Pattern learning and optimization
    - Domain-specific insights and analytics
    - Strategy configuration and management
    - Performance metrics and analysis
    - Cache management for learned patterns

API Endpoints:
    POST /api/adaptive/crawl - Perform adaptive crawling with intelligence
    GET /api/adaptive/insights/{domain} - Get domain-specific insights
    GET /api/adaptive/patterns - Get comprehensive pattern analysis
    POST /api/adaptive/strategy - Create custom adaptive strategy
    DELETE /api/adaptive/cache/{domain} - Clear adaptive cache for domain
    GET /api/adaptive/export/{domain} - Export learned patterns

Author: CRY-A-4MCP Development Team
Version: 1.0.0
"""

# Standard library imports
from typing import Dict, Optional, Any
import logging
import json

# FastAPI framework imports
from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.responses import JSONResponse

# Internal imports
from ...crypto_crawler.crawler import CryptoCrawler
from ...models.adaptive_models import (
    AdaptiveStrategyConfig,
    AdaptiveCrawlRequest,
    AdaptiveCrawlResponse,
    DomainInsights,
    PatternAnalysis,
    StrategyType,
    ContentType
)

# FastAPI router instance
router = APIRouter(prefix="/adaptive", tags=["Adaptive Crawling"])

# Module-level logger
logger = logging.getLogger(__name__)


def setup_adaptive_routes(crypto_crawler: CryptoCrawler):
    """Configure and register all adaptive crawling API endpoints.
    
    This function sets up the complete set of RESTful API endpoints for the new
    adaptive crawling intelligence features. It injects the crawler dependency
    and configures proper error handling and response formatting.
    
    Args:
        crypto_crawler (CryptoCrawler): The initialized crypto crawler instance
            with adaptive capabilities enabled.
    
    Returns:
        APIRouter: Configured FastAPI router instance with all adaptive endpoints.
    """
    
    @router.post("/crawl", response_model=AdaptiveCrawlResponse)
    async def adaptive_crawl(
        request: AdaptiveCrawlRequest = Body(..., description="Adaptive crawl request configuration")
    ):
        """Perform intelligent adaptive crawling with machine learning optimization.
        
        This endpoint leverages Crawl4AI v0.7.0's adaptive intelligence features to
        automatically optimize crawling strategies based on URL patterns, content types,
        and learned behaviors. It can apply statistical analysis, embedding-based
        strategies, or hybrid approaches for optimal results.
        
        Args:
            request (AdaptiveCrawlRequest): Complete crawl request with URL, strategy
                configuration, and optional parameters.
        
        Returns:
            AdaptiveCrawlResponse: Comprehensive crawl results with adaptive metadata,
                learned patterns, and performance metrics.
        
        Raises:
            HTTPException: 400 for invalid requests, 500 for crawling errors.
        """
        try:
            # Log incoming request with full details
            logger.info(f"🔥 [BACKEND] Received adaptive crawl request for URL: {request.url}")
            logger.info(f"🔥 [BACKEND] Full request data: {request.model_dump()}")
            logger.info(f"🔥 [BACKEND] Request strategy_type: {request.strategy_type}")
            logger.info(f"🔥 [BACKEND] Request parameters: min_word_count={request.min_word_count}, max_word_count={request.max_word_count}")
            logger.info(f"🔥 [BACKEND] Request thresholds: content_quality={request.content_quality_threshold}, similarity={request.similarity_threshold}")
            logger.info(f"🔥 [BACKEND] Request flags: smart_stopping={request.enable_smart_stopping}, pattern_learning={request.enable_pattern_learning}")
            
            # Validate URL
            if not request.url or not request.url.startswith(('http://', 'https://')):
                logger.error(f"🔥 [BACKEND] Invalid URL format: {request.url}")
                raise HTTPException(
                    status_code=400, 
                    detail="Invalid URL format. Must start with http:// or https://"
                )
            
            # Prepare strategy configuration from request fields
            strategy_config = AdaptiveStrategyConfig(
                strategy_type=request.strategy_type,
                min_word_count=request.min_word_count,
                max_word_count=request.max_word_count,
                content_quality_threshold=request.content_quality_threshold,
                similarity_threshold=request.similarity_threshold,
                learning_rate=request.learning_rate,
                enable_smart_stopping=request.enable_smart_stopping,
                enable_pattern_learning=request.enable_pattern_learning
            )
            
            logger.info(f"🔥 [BACKEND] Created strategy config: {strategy_config.model_dump()}")
            
            # Check if LLM extraction is requested via extractor_config
            if request.extractor_config and request.extractor_config.get('llm_config'):
                logger.info(f"🔥 [BACKEND] LLM extraction requested via extractor_config for {request.url}")
                
                # Extract LLM configuration from extractor_config
                llm_config = request.extractor_config.get('llm_config', {})
                instruction = request.extractor_config.get('instruction', 'Extract the main content and key information from this webpage.')
                schema = request.extractor_config.get('schema')
                
                logger.info(f"🔥 [BACKEND] LLM config: {llm_config}")
                logger.info(f"🔥 [BACKEND] Instruction: {instruction}")
                logger.info(f"🔥 [BACKEND] Schema: {schema}")
                
                # Initialize GenericAsyncCrawler for LLM extraction
                from ...crypto_crawler.crawler import GenericAsyncCrawler
                llm_crawler = GenericAsyncCrawler()
                await llm_crawler.initialize()
                
                try:
                    # Perform LLM-based extraction
                    llm_result = await llm_crawler.test_url_with_llm(
                        url=request.url,
                        instruction=instruction,
                        schema=schema,
                        provider=llm_config.get('provider', 'openrouter'),
                        model=llm_config.get('model', 'anthropic/claude-3.5-sonnet'),
                        api_key=llm_config.get('api_key'),
                        temperature=llm_config.get('temperature', 0.7),
                        max_tokens=llm_config.get('max_tokens', 1000),
                        timeout=llm_config.get('timeout', 30)
                    )
                    
                    logger.info(f"🔥 [BACKEND] LLM extraction result: {llm_result}")
                    
                    # Close the LLM crawler
                    await llm_crawler.close()
                    
                    # Convert LLM result to adaptive crawl format
                    # LLM extracted data is now directly in 'data' field
                    extracted_data = llm_result.get('data', {})
                    
                    # Ensure we have structured data, not raw HTML
                    if isinstance(extracted_data, dict) and len(extracted_data) > 0:
                        logger.info(f"🔥 [BACKEND] LLM extraction returned structured data with keys: {list(extracted_data.keys())}")
                        content_for_response = extracted_data  # Use structured data as content
                    else:
                        logger.warning(f"🔥 [BACKEND] LLM extraction did not return structured data. Type: {type(extracted_data)}, Value: {str(extracted_data)[:200]}...")
                        content_for_response = extracted_data  # Fallback to whatever was returned
                    
                    crawl_result = {
                        'success': llm_result.get('success', False),
                        'url': request.url,
                        'content': content_for_response,  # Use structured data as content
                        'extracted_data': extracted_data,  # Keep structured data in extracted_data field
                        'metadata': {
                            'extraction_time': llm_result.get('response_time', 0.0),
                            'llm_extraction': True,
                            'extractor_used': f"llm_{llm_config.get('provider', 'openrouter')}_{llm_config.get('model', 'claude')}",
                            'llm_metadata': llm_result.get('metadata', {}),  # Include LLM metadata
                            'adaptive_intelligence': {
                                'patterns_learned': [],
                                'content_quality_score': 0.9,  # High quality for LLM extraction
                                'adaptation_applied': True,
                                'stopping_reason': 'llm_extraction_complete',
                                'statistical_metrics': {},
                                'strategy_type': strategy_config.strategy_type,
                                'learning_enabled': strategy_config.enable_pattern_learning,
                                'smart_stopping_enabled': strategy_config.enable_smart_stopping
                            }
                        },
                        'extraction_time': llm_result.get('response_time', 0.0),
                        'error': llm_result.get('error') if not llm_result.get('success') else None
                    }
                    
                except Exception as llm_error:
                    logger.error(f"🔥 [BACKEND] LLM extraction failed: {llm_error}")
                    await llm_crawler.close()
                    
                    # Fall back to regular adaptive crawling
                    logger.info(f"🔥 [BACKEND] Falling back to regular adaptive crawling for {request.url}")
                    crawl_result = await crypto_crawler.crawl_with_adaptive_intelligence(
                        url=request.url,
                        strategy_config=strategy_config
                    )
                    
                    # Add error information
                    if 'metadata' not in crawl_result:
                        crawl_result['metadata'] = {}
                    crawl_result['metadata']['llm_extraction_error'] = str(llm_error)
                    
            else:
                # Perform regular adaptive crawling
                logger.info(f"🔥 [BACKEND] Starting regular crawl_with_adaptive_intelligence for {request.url}")
                crawl_result = await crypto_crawler.crawl_with_adaptive_intelligence(
                    url=request.url,
                    strategy_config=strategy_config
                )
            
            logger.info(f"🔥 [BACKEND] Raw crawl result keys: {list(crawl_result.keys()) if isinstance(crawl_result, dict) else 'Not a dict'}")
            logger.info(f"🔥 [BACKEND] Raw crawl result type: {type(crawl_result)}")
            logger.info(f"🔥 [BACKEND] Raw crawl result success: {crawl_result.get('success') if isinstance(crawl_result, dict) else 'N/A'}")
            logger.info(f"🔥 [BACKEND] Raw crawl result content length: {len(str(crawl_result.get('content', ''))) if isinstance(crawl_result, dict) else 'N/A'}")
            logger.info(f"🔥 [BACKEND] Raw crawl result metadata: {crawl_result.get('metadata', {}) if isinstance(crawl_result, dict) else 'N/A'}")
            logger.info(f"🔥 [BACKEND] Full raw crawl result: {crawl_result}")
            
            # Extract adaptive metadata
            adaptive_metadata = crawl_result.get('metadata', {}).get('adaptive_intelligence', {})
            logger.info(f"🔥 [BACKEND] Extracted adaptive metadata: {adaptive_metadata}")
            
            # Prepare structured data for frontend compatibility
            extracted_data = crawl_result.get('extracted_data', {})
            content = crawl_result.get('content', '')
            
            # Determine if we have structured data from LLM extraction
            has_structured_data = (
                extracted_data and 
                isinstance(extracted_data, dict) and 
                len(extracted_data) > 0 and
                not isinstance(extracted_data, str)
            )
            
            # For LLM extraction, prioritize structured data
            if has_structured_data:
                    content_for_display = json.dumps(extracted_data, indent=2) if isinstance(extracted_data, dict) else str(extracted_data)
            elif isinstance(content, dict) and len(content) > 0:
                # Content is already structured (from LLM)
                content_for_display = json.dumps(content, indent=2)
                extracted_data = content  # Ensure extracted_data is populated
                logger.info(f"🔥 [BACKEND] Using structured content: {len(str(content))} characters")
            else:
                # Fall back to raw content
                content=str(content_for_display)

                
            
            structured_data = {
                'content': content_for_display,
                'url': request.url,
                'success': crawl_result.get('success', False),
                'metadata': crawl_result.get('metadata', {}),
                'adaptive_features': adaptive_metadata,
                'extraction_time': crawl_result.get('extraction_time', 0.0),
                'extracted_data': extracted_data,
                'links': crawl_result.get('links', []),
                'images': crawl_result.get('images', []),
                'media': crawl_result.get('media', {})
            }
            
            # Create response
            response = AdaptiveCrawlResponse(
                success=crawl_result.get('success', False),
                url=request.url,
                content=content_for_display,  # Keep structured data as-is for frontend
                data=structured_data,  # Structured data for frontend
                metadata={ **crawl_result.get('metadata', {}),"extraction_status": "failed" if  structured_data.get("error")=="true" else "success",  "extraction_warning": "Extractor not used due to LLM issues" },
                adaptive_features=adaptive_metadata,
                extraction_time=crawl_result.get('extraction_time', 0.0),
                error=crawl_result.get('error') if not crawl_result.get('success') else None,
                screenshot=crawl_result.get('screenshot')
            )
            
            # Log the complete response being sent
            logger.info(f"🔥 [BACKEND] Created AdaptiveCrawlResponse:")
            logger.info(f"🔥 [BACKEND] Response success: {response.success}")
            logger.info(f"🔥 [BACKEND] Response URL: {response.url}")
            logger.info(f"🔥 [BACKEND] Response content length: {len(response.content)}")
            logger.info(f"🔥 [BACKEND] Response content preview: {response.content[:200]}...")
            logger.info(f"🔥 [BACKEND] Response data keys: {list(response.data.keys()) if response.data else 'None'}")
            logger.info(f"🔥 [BACKEND] Response data size (JSON): {len(str(response.data)) if response.data else 0} characters")
            logger.info(f"🔥 [BACKEND] Response metadata: {response.metadata}")
            logger.info(f"🔥 [BACKEND] Response adaptive_features: {response.adaptive_features}")
            logger.info(f"🔥 [BACKEND] Response extraction_time: {response.extraction_time}")
            logger.info(f"🔥 [BACKEND] Response error: {response.error}")
            logger.info(f"🔥 [BACKEND] Full response model dump: {response.model_dump()}")
            
            logger.info(f"🔥 [BACKEND] Adaptive crawl completed for {request.url}: success={response.success}")
            return response
            
        except HTTPException as he:
            logger.error(f"🔥 [BACKEND] HTTP Exception in adaptive crawl for {request.url}: {he.detail}")
            raise
        except Exception as e:
            logger.error(f"🔥 [BACKEND] Unexpected error in adaptive crawl for {request.url}: {e}")
            logger.error(f"🔥 [BACKEND] Exception type: {type(e)}")
            logger.error(f"🔥 [BACKEND] Exception args: {e.args}")
            import traceback
            logger.error(f"🔥 [BACKEND] Full traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Crawling failed: {str(e)}")
    
    @router.get("/insights/{domain}", response_model=DomainInsights)
    async def get_domain_insights(
        domain: str,
        include_recommendations: bool = Query(True, description="Include optimization recommendations")
    ):
        """Get comprehensive insights and analytics for a specific domain.
        
        This endpoint provides detailed analysis of crawling patterns, performance
        metrics, and optimization opportunities for a given domain based on
        historical crawling data and learned patterns.
        
        Args:
            domain (str): Domain name to analyze (e.g., 'example.com')
            include_recommendations (bool): Whether to include optimization suggestions
        
        Returns:
            DomainInsights: Comprehensive domain analysis with metrics and recommendations
        
        Raises:
            HTTPException: 404 if domain has no data, 500 for analysis errors
        """
        try:
            logger.info(f"Retrieving insights for domain: {domain}")
            
            # Get insights from crawler
            insights_data = crypto_crawler.get_adaptive_insights(domain)
            
            if not insights_data:
                raise HTTPException(
                    status_code=404,
                    detail=f"No adaptive crawling data found for domain: {domain}"
                )
            
            logger.info(f"Successfully retrieved insights for domain: {domain}")
            return insights_data
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error retrieving insights for domain {domain}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve insights: {str(e)}")
    
    @router.get("/patterns", response_model=PatternAnalysis)
    async def get_pattern_analysis(
        min_confidence: float = Query(0.5, ge=0.0, le=1.0, description="Minimum pattern confidence"),
        content_type: Optional[ContentType] = Query(None, description="Filter by content type")
    ):
        """Get comprehensive pattern analysis across all domains.
        
        This endpoint provides system-wide analysis of learned patterns,
        optimization opportunities, and performance trends across all
        crawled domains and content types.
        
        Args:
            min_confidence (float): Minimum confidence threshold for patterns (0.0-1.0)
            content_type (Optional[ContentType]): Filter patterns by content type
        
        Returns:
            PatternAnalysis: Comprehensive pattern analysis with trends and insights
        
        Raises:
            HTTPException: 500 for analysis errors
        """
        try:
            logger.info(f"Retrieving pattern analysis (min_confidence={min_confidence}, content_type={content_type})")
            
            # Get pattern analysis from crawler
            analysis_data = crypto_crawler.get_pattern_analysis()
            
            # Apply filters if specified
            if min_confidence > 0.0 and 'patterns' in analysis_data:
                analysis_data['patterns'] = [
                    pattern for pattern in analysis_data['patterns']
                    if pattern.get('confidence', 0.0) >= min_confidence
                ]
            
            if content_type and 'patterns' in analysis_data:
                analysis_data['patterns'] = [
                    pattern for pattern in analysis_data['patterns']
                    if pattern.get('content_type') == content_type.value
                ]
            
            logger.info(f"Successfully retrieved pattern analysis with {len(analysis_data.get('patterns', []))} patterns")
            return analysis_data
            
        except Exception as e:
            logger.error(f"Error retrieving pattern analysis: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve pattern analysis: {str(e)}")
    
    @router.post("/strategy", response_model=Dict[str, Any])
    async def create_adaptive_strategy(
        strategy_config: AdaptiveStrategyConfig = Body(..., description="Custom adaptive strategy configuration")
    ):
        """Create and validate a custom adaptive crawling strategy.
        
        This endpoint allows clients to create custom adaptive strategies
        with specific parameters and validate them before use in crawling operations.
        
        Args:
            strategy_config (AdaptiveStrategyConfig): Custom strategy configuration
        
        Returns:
            Dict[str, Any]: Strategy validation results and recommendations
        
        Raises:
            HTTPException: 400 for invalid strategy, 500 for validation errors
        """
        try:
            logger.info(f"Creating custom adaptive strategy: {strategy_config.strategy_type}")
            
            # Validate strategy configuration
            if strategy_config.min_word_count < 0:
                raise HTTPException(
                    status_code=400,
                    detail="min_word_count must be non-negative"
                )
            
            if strategy_config.max_crawl_time <= 0:
                raise HTTPException(
                    status_code=400,
                    detail="max_crawl_time must be positive"
                )
            
            if not 0.0 <= strategy_config.quality_threshold <= 1.0:
                raise HTTPException(
                    status_code=400,
                    detail="quality_threshold must be between 0.0 and 1.0"
                )
            
            # Create strategy validation response
            validation_result = {
                "valid": True,
                "strategy_type": strategy_config.strategy_type,
                "configuration": strategy_config.dict(),
                "recommendations": [],
                "estimated_performance": {
                    "speed": "medium",
                    "accuracy": "high" if strategy_config.strategy_type == StrategyType.HYBRID else "medium",
                    "resource_usage": "high" if strategy_config.strategy_type == StrategyType.EMBEDDING else "medium"
                }
            }
            
            # Add recommendations based on configuration
            if strategy_config.strategy_type == StrategyType.STATISTICAL and strategy_config.min_word_count < 50:
                validation_result["recommendations"].append(
                    "Consider increasing min_word_count for better statistical analysis"
                )
            
            if strategy_config.max_crawl_time > 600:
                validation_result["recommendations"].append(
                    "Long crawl times may impact system performance"
                )
            
            logger.info(f"Successfully created and validated adaptive strategy")
            return validation_result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating adaptive strategy: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to create strategy: {str(e)}")
    
    @router.delete("/cache/{domain}")
    async def clear_adaptive_cache(
        domain: str,
        confirm: bool = Query(False, description="Confirmation flag for cache clearing")
    ):
        """Clear adaptive learning cache for a specific domain.
        
        This endpoint removes all learned patterns and cached strategies
        for a domain, forcing the system to relearn optimal approaches.
        
        Args:
            domain (str): Domain to clear cache for
            confirm (bool): Confirmation flag to prevent accidental clearing
        
        Returns:
            Dict[str, Any]: Cache clearing results
        
        Raises:
            HTTPException: 400 for missing confirmation, 404 if domain not found
        """
        try:
            if not confirm:
                raise HTTPException(
                    status_code=400,
                    detail="Cache clearing requires confirmation. Set confirm=true"
                )
            
            logger.info(f"Clearing adaptive cache for domain: {domain}")
            
            # Clear cache
            success = crypto_crawler.clear_adaptive_cache(domain)
            
            if not success:
                raise HTTPException(
                    status_code=404,
                    detail=f"No cache data found for domain: {domain}"
                )
            
            result = {
                "success": True,
                "domain": domain,
                "message": f"Adaptive cache cleared for domain: {domain}",
                "timestamp": "2024-01-01T00:00:00Z"  # Would use actual timestamp
            }
            
            logger.info(f"Successfully cleared adaptive cache for domain: {domain}")
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error clearing cache for domain {domain}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")
    
    @router.get("/export/{domain}")
    async def export_learned_patterns(
        domain: str,
        format: str = Query("json", regex="^(json|csv)$", description="Export format (json or csv)")
    ):
        """Export learned patterns for a domain in specified format.
        
        This endpoint allows exporting of learned crawling patterns
        for backup, analysis, or transfer to other systems.
        
        Args:
            domain (str): Domain to export patterns for
            format (str): Export format ('json' or 'csv')
        
        Returns:
            JSONResponse: Exported patterns in requested format
        
        Raises:
            HTTPException: 404 if domain has no patterns, 500 for export errors
        """
        try:
            logger.info(f"Exporting learned patterns for domain: {domain} in {format} format")
            
            # Export patterns
            patterns_data = crypto_crawler.export_learned_patterns(domain)
            
            if not patterns_data:
                raise HTTPException(
                    status_code=404,
                    detail=f"No learned patterns found for domain: {domain}"
                )
            
            # Format response based on requested format
            if format == "json":
                response_data = {
                    "domain": domain,
                    "export_format": "json",
                    "patterns": patterns_data,
                    "export_timestamp": "2024-01-01T00:00:00Z",
                    "pattern_count": len(patterns_data.get('patterns', []))
                }
                
                logger.info(f"Successfully exported {len(patterns_data.get('patterns', []))} patterns for domain: {domain}")
                return JSONResponse(content=response_data)
            
            elif format == "csv":
                # For CSV format, we'd convert to CSV structure
                # This is a simplified implementation
                csv_data = {
                    "domain": domain,
                    "export_format": "csv",
                    "message": "CSV export functionality would be implemented here",
                    "patterns_summary": patterns_data
                }
                
                return JSONResponse(content=csv_data)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error exporting patterns for domain {domain}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to export patterns: {str(e)}")
    
    return router