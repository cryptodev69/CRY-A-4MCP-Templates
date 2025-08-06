#!/usr/bin/env python3
"""
URL-to-Extractor Mapping System.

This package provides a flexible system for mapping URLs to appropriate content
extractors based on domain, path, or exact URL patterns.
"""

from .url_mapping import ExtractorConfig, URLExtractorMapping, URLMappingManager, extract_from_url

__all__ = ['ExtractorConfig', 'URLExtractorMapping', 'URLMappingManager', 'extract_from_url']