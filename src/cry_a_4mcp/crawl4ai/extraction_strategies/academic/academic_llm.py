#!/usr/bin/env python3
"""
AcademicLLMExtractionStrategy extraction strategy for the cry_a_4mcp.crawl4ai package.

This module provides a specialized extraction strategy for AcademicLLMExtractionStrategy content,
with a detailed schema for extracting relevant information from AcademicLLMExtractionStrategy sources.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Union
from ..base import LLMExtractionStrategy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('academic_extraction_strategy')

class AcademicLLMExtractionStrategy(LLMExtractionStrategy):
    """Specialized extraction strategy for AcademicLLMExtractionStrategy content.
    
    Academic-specific LLM extraction strategy.
    
    This strategy is specialized for extracting structured information from academic content,
    including research papers, journal articles, conference proceedings, and other scholarly publications.
    
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
    
    def __init__(self, 
                 provider: str = "openai", 
                 api_token: Optional[str] = None,
                 base_url: Optional[str] = None,
                 model: Optional[str] = None,
                 extra_args: Optional[Dict[str, Any]] = None,
                 max_retries: int = 3,
                 timeout: int = 60,
                 **kwargs):
        """Initialize the AcademicLLMExtractionStrategy extraction strategy.
        
        Args:
            provider: LLM provider (e.g., "openai", "groq", "openrouter")
            api_token: API token for the LLM provider
            base_url: Optional base URL for the API
            model: Model to use for extraction
            extra_args: Additional arguments to pass to the API
            max_retries: Maximum number of retries for API calls
            timeout: Timeout for API calls in seconds
            **kwargs: Additional configuration options
        """
        # Define the AcademicLLMExtractionStrategy-specific schema
        academic_schema = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "The title of the academic paper or article"
        },
        "abstract": {
            "type": "string",
            "description": "The abstract or summary of the paper"
        },
        "authors": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "affiliation": {
                        "type": "string"
                    },
                    "email": {
                        "type": "string"
                    },
                    "is_corresponding": {
                        "type": "boolean"
                    }
                },
                "required": [
                    "name"
                ]
            },
            "description": "Authors of the paper"
        },
        "publication_info": {
            "type": "object",
            "properties": {
                "journal": {
                    "type": "string"
                },
                "conference": {
                    "type": "string"
                },
                "volume": {
                    "type": "string"
                },
                "issue": {
                    "type": "string"
                },
                "pages": {
                    "type": "string"
                },
                "year": {
                    "type": "integer"
                },
                "publisher": {
                    "type": "string"
                },
                "doi": {
                    "type": "string"
                },
                "url": {
                    "type": "string"
                }
            },
            "description": "Publication information"
        },
        "keywords": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "Keywords or subject terms"
        },
        "research_questions": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "Main research questions addressed in the paper"
        },
        "methodology": {
            "type": "object",
            "properties": {
                "approach": {
                    "type": "string"
                },
                "data_collection": {
                    "type": "string"
                },
                "analysis_techniques": {
                    "type": "string"
                },
                "sample_size": {
                    "type": "string"
                },
                "limitations": {
                    "type": "string"
                }
            },
            "description": "Research methodology used"
        },
        "findings": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "Key findings or results of the research"
        },
        "conclusions": {
            "type": "string",
            "description": "Main conclusions drawn by the authors"
        },
        "contributions": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "Main contributions to the field"
        },
        "future_work": {
            "type": "string",
            "description": "Suggestions for future research"
        },
        "references": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string"
                    },
                    "key_reference": {
                        "type": "boolean"
                    }
                },
                "required": [
                    "text"
                ]
            },
            "description": "Key references cited in the paper"
        },
        "figures_tables": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": [
                            "figure",
                            "table"
                        ]
                    },
                    "number": {
                        "type": "string"
                    },
                    "caption": {
                        "type": "string"
                    },
                    "description": {
                        "type": "string"
                    }
                },
                "required": [
                    "type",
                    "caption"
                ]
            },
            "description": "Key figures and tables in the paper"
        },
        "funding": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "agency": {
                        "type": "string"
                    },
                    "grant_number": {
                        "type": "string"
                    },
                    "details": {
                        "type": "string"
                    }
                },
                "required": [
                    "agency"
                ]
            },
            "description": "Funding information"
        },
        "field_of_study": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "description": "Fields or disciplines the paper belongs to"
        },
        "research_impact": {
            "type": "object",
            "properties": {
                "theoretical": {
                    "type": "string"
                },
                "practical": {
                    "type": "string"
                },
                "societal": {
                    "type": "string"
                }
            },
            "description": "Potential impact of the research"
        },
        "technical_terms": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "term": {
                        "type": "string"
                    },
                    "definition": {
                        "type": "string"
                    }
                },
                "required": [
                    "term"
                ]
            },
            "description": "Important technical terms and their definitions"
        },
        "quality_assessment": {
            "type": "object",
            "properties": {
                "rigor": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10
                },
                "originality": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10
                },
                "significance": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10
                },
                "clarity": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10
                }
            },
            "description": "Assessment of the paper's quality (1-10 scale)"
        }
    },
    "required": [
        "title",
        "abstract",
        "authors",
        "findings",
        "conclusions"
    ]
}
        
        # Define the instruction for the LLM
        instruction = """
        Extract structured information from the provided academic paper or article.
        Focus on identifying the title, abstract, authors, and publication information.
        Extract the main research questions, methodology, key findings, and conclusions.
        Identify the main contributions to the field and suggestions for future work.
        Note key references cited in the paper.
        Describe important figures and tables
        Extract funding information if available.
        Identify the fields of study the paper belongs to.
        Assess the potential theoretical, practical, and societal impact of the research.
        Identify important technical terms and their definitions.
        Evaluate the paper's quality in terms of rigor, originality, significance, and clarity on a scale of 1-10.
        
        Ensure the extraction is objective and based solely on the content provided.
        Do not include information not present in the paper.
        """
        
        # Initialize the base class with the schema and instruction
        super().__init__(
            provider=provider,
            api_token=api_token,
            instruction=instruction,
            schema=academic_schema,
            base_url=base_url,
            model=model,
            extra_args=extra_args,
            max_retries=max_retries,
            timeout=timeout,
            **kwargs
        )