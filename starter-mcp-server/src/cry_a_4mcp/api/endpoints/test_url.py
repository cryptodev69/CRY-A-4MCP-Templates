"""Test URL API endpoints for CRY-A-4MCP platform.

This module provides REST API endpoints for testing URL extraction capabilities
within the CRY-A-4MCP platform. It allows users to test extraction strategies
against specific URLs before setting up full crawl jobs, enabling validation
and debugging of extraction logic.

The module supports:
    - LLM-based extraction testing with configurable models and parameters
    - Traditional extractor-based testing
    - Comprehensive error handling and logging
    - Real-time extraction performance metrics

Typical usage:
    POST /api/test-url - Test URL extraction with LLM or traditional extractors
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from pydantic import ValidationError

from ..models import TestURLRequest, TestURLResponse
from ...crypto_crawler.crawler import GenericAsyncCrawler

# Module-level logger
logger = logging.getLogger(__name__)

# Create router instance
router = APIRouter(
    prefix="/test-url",
    tags=["test-url"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)


@router.post("", response_model=TestURLResponse)
async def test_url_extraction(request: TestURLRequest) -> TestURLResponse:
    """Test URL extraction capabilities with LLM or traditional extractors.
    
    This endpoint allows users to test extraction strategies against specific URLs
    before setting up full crawl jobs. It supports both LLM-based extraction with
    configurable models and parameters, as well as traditional extractor-based testing.
    
    The endpoint:
        1. Validates the incoming request parameters
        2. Initializes the appropriate crawler configuration
        3. Performs the extraction using the specified method
        4. Returns comprehensive results including extracted data and metadata
        5. Handles errors gracefully with detailed error messages
    
    Args:
        request (TestURLRequest): The test request containing:
            - url: Target URL to test extraction against
            - extractor_id: Optional traditional extractor identifier
            - llm_config: Optional LLM configuration for AI-based extraction
            - instruction: Extraction instruction for LLM
            - schema: Optional JSON schema for structured extraction
    
    Returns:
        TestURLResponse: Comprehensive test results containing:
            - url: The original URL that was tested
            - extractor_used: The actual extractor that was used
            - success: Whether the extraction was successful
            - extracted_data: The extracted content and metadata
            - response_time: Time taken for the extraction
            - timestamp: When the test was performed
            - error_message: Error details if extraction failed
    
    Raises:
        HTTPException:
            - 400 Bad Request: Invalid request parameters or configuration
            - 422 Unprocessable Entity: Request validation failed
            - 500 Internal Server Error: Extraction process failed
    
    Example Request:
        {
            "url": "https://cryptonews.com/news/bitcoin-reaches-new-high",
            "llm_config": {
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "api_key": "your-api-key",
                "temperature": 0.7,
                "max_tokens": 1000,
                "timeout": 30
            },
            "instruction": "Extract the main content and key information",
            "schema": {"title": "string", "content": "string"}
        }
    
    Example Response:
        {
            "url": "https://cryptonews.com/news/bitcoin-reaches-new-high",
            "extractor_used": "llm_extraction",
            "success": true,
            "extracted_data": {
                "title": "Bitcoin Reaches New All-Time High",
                "content": "Bitcoin has reached a new all-time high...",
                "metadata": {...}
            },
            "response_time": 2.5,
            "timestamp": "2024-01-15T10:30:00Z",
            "error_message": null
        }
    
    HTTP Status Codes:
        200 OK: Extraction test completed successfully
        400 Bad Request: Invalid request parameters
        422 Unprocessable Entity: Request validation failed
        500 Internal Server Error: Extraction process failed
    
    Note:
        This endpoint is designed for testing and validation purposes.
        For production crawling, use the dedicated crawl job endpoints.
        LLM-based extraction may incur API costs depending on the provider.
    """
    try:
        logger.info(f"Processing test URL request for: {request.url}")
        logger.debug(f"Request details - Model: {request.model}, Extractor ID: {request.extractor_id}, Custom instructions: {bool(request.custom_instructions)}")
        
        # Validate the request URL
        if not request.url or not request.url.strip():
            logger.warning("Received empty or whitespace-only URL")
            raise HTTPException(
                status_code=400,
                detail="URL cannot be empty or whitespace"
            )
        
        logger.info("Initializing GenericAsyncCrawler...")
        # Initialize crawler
        crawler = GenericAsyncCrawler()
        
        # Initialize and start the crawler
        logger.info("Starting crawler initialization...")
        await crawler.initialize()
        logger.info("Crawler initialization completed successfully")
        
        # Determine extraction method based on request
        if request.llm_config or request.model or request.custom_instructions or request.instruction:
            # Use LLM configuration if provided, otherwise fall back to individual fields
            if request.llm_config:
                provider = request.llm_config.provider
                model_to_use = request.llm_config.model
                api_key = request.llm_config.api_key
                temperature = request.llm_config.temperature
                max_tokens = request.llm_config.max_tokens
                timeout = request.llm_config.timeout
                instruction_to_use = request.instruction or "Extract the main content and key information from this webpage."
                schema_to_use = request.schema
                logger.info(f"Using LLM-based extraction with provider: {provider}, model: {model_to_use}")
            else:
                # Fall back to legacy fields for backward compatibility
                provider = "openai"
                model_to_use = request.model or "gpt-3.5-turbo"
                api_key = None
                temperature = 0.1
                max_tokens = 4000
                timeout = 30
                instruction_to_use = request.custom_instructions or "Extract the main content and key information from this webpage."
                schema_to_use = None
                logger.info(f"Using legacy LLM-based extraction with model: {model_to_use}")
            
            logger.debug(f"Extraction instruction: {instruction_to_use[:100]}...")
            
            try:
                # Perform LLM-based extraction
                logger.info("Starting LLM-based URL extraction...")
                result = await crawler.test_url_with_llm(
                    url=request.url,
                    instruction=instruction_to_use,
                    schema=schema_to_use,
                    provider=provider,
                    model=model_to_use,
                    api_key=api_key,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=timeout
                )
                logger.info(f"LLM extraction completed. Success: {result.get('success', False)}")
                if not result.get('success', False):
                    logger.error(f"LLM extraction failed with error: {result.get('error', 'Unknown error')}")
                
            except Exception as llm_error:
                logger.error(f"Exception during LLM extraction: {str(llm_error)}", exc_info=True)
                raise
            
            extractor_used = f"llm_extraction_{provider}_{model_to_use.replace('/', '_')}"
            
        elif request.extractor_id:
            logger.info(f"Using traditional extractor: {request.extractor_id}")
            logger.warning("Traditional extractor testing requested but not yet implemented")
            
            # TODO: Implement traditional extractor-based testing
            # This would involve loading the specified extractor and running it
            raise HTTPException(
                status_code=501,
                detail="Traditional extractor testing not yet implemented"
            )
            
        else:
            # Default to basic LLM extraction with OpenRouter
            logger.info("Using default LLM-based extraction (no model or extractor specified)")
            try:
                logger.info("Starting default LLM extraction...")
                result = await crawler.test_url_with_llm(
                    url=request.url,
                    instruction="Extract the main content and key information from this webpage.",
                    schema=None,
                    provider="openrouter",
                    model="anthropic/claude-3.5-sonnet",
                    api_key=None,  # This will need to be configured
                    temperature=0.1,
                    max_tokens=4000,
                    timeout=30
                )
                logger.info(f"Default LLM extraction completed. Success: {result.get('success', False)}")
                if not result.get('success', False):
                    logger.error(f"Default LLM extraction failed with error: {result.get('error', 'Unknown error')}")
                
            except Exception as default_llm_error:
                logger.error(f"Exception during default LLM extraction: {str(default_llm_error)}", exc_info=True)
                raise
                
            extractor_used = "llm_extraction_default_openrouter"
        
        # Process the result
        success = result.get('success', False)
        extracted_data = result.get('data', {})
        response_time = result.get('response_time', 0.0)
        error_message = result.get('error') if not success else None
        
        logger.info(f"Processing extraction result - Success: {success}, Response time: {response_time}s")
        if error_message:
            logger.error(f"Extraction error message: {error_message}")
        if extracted_data:
            logger.debug(f"Extracted data keys: {list(extracted_data.keys()) if isinstance(extracted_data, dict) else 'Non-dict data'}")
        
        # Create metadata from the result
        metadata = {
            "timestamp": result.get('timestamp', datetime.now().isoformat()),
            "response_time_ms": response_time * 1000,
            "extractor_used": extractor_used,
            "url_tested": request.url
        }
        
        logger.info(f"Extraction completed. Success: {success}, Response time: {response_time}s")
        logger.debug(f"Metadata created: {metadata}")
        
        # Create and return response matching the existing model structure
        response = TestURLResponse(
            url=request.url,
            extractor_used=extractor_used,
            extraction_result=extracted_data,
            metadata=metadata,
            success=success,
            error_message=error_message
        )
        
        # Close the crawler
        logger.info("Closing crawler...")
        await crawler.close()
        logger.info("Crawler closed successfully")
        
        logger.info(f"Returning test result for URL: {request.url} - Success: {response.success}")
        return response
        
    except ValidationError as e:
        logger.error(f"Request validation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=422,
            detail=f"Request validation failed: {str(e)}"
        )
        
    except HTTPException as http_exc:
        # Re-raise HTTP exceptions as-is but log them
        logger.error(f"HTTP exception during URL testing: {http_exc.status_code} - {http_exc.detail}")
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error during URL testing: {e}", exc_info=True)
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error args: {e.args}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during URL testing: {str(e)}"
        )