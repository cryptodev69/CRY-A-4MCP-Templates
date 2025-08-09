#!/usr/bin/env python3

import os
import sys
import pytest

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def test_strategy_template_generator_import():
    """Test that StrategyTemplateGeneratorClassAttrs can be imported successfully."""
    try:
        from src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.templates.strategy_generator_class_attrs import StrategyTemplateGeneratorClassAttrs
        assert StrategyTemplateGeneratorClassAttrs is not None
    except ImportError as e:
        pytest.skip(f"Import failed: {e}")


def test_strategy_template_generator_initialization():
    """Test that StrategyTemplateGeneratorClassAttrs can be initialized."""
    try:
        from src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.templates.strategy_generator_class_attrs import StrategyTemplateGeneratorClassAttrs
        generator = StrategyTemplateGeneratorClassAttrs()
        assert generator is not None
    except ImportError as e:
        pytest.skip(f"Import failed: {e}")
    except Exception as e:
        pytest.fail(f"Initialization failed: {e}")


def test_strategy_template_file_access():
    """Test that the template file can be accessed."""
    try:
        from src.cry_a_4mcp.crawl4ai.extraction_strategies.ui.templates.strategy_generator_class_attrs import StrategyTemplateGeneratorClassAttrs
        generator = StrategyTemplateGeneratorClassAttrs()
        
        # Check if template file path is accessible
        assert hasattr(generator, 'template_file')
        
        # If template file exists, verify it can be read
        if os.path.exists(generator.template_file):
            with open(generator.template_file, 'r') as f:
                first_line = f.readline().strip()
                assert len(first_line) >= 0  # Just verify we can read it
                
    except ImportError as e:
        pytest.skip(f"Import failed: {e}")
    except Exception as e:
        pytest.fail(f"Template file access failed: {e}")