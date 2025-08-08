import asyncio
import json
import time
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
from datetime import datetime, timedelta
import logging

# Crawl4AI v0.7.0 imports for adaptive features
try:
    # Import basic crawl4ai first to check compatibility
    import crawl4ai
    
    # Try to import adaptive features (may not exist in current version)
    try:
        from crawl4ai import StatisticalStrategy, EmbeddingStrategy
    except ImportError:
        StatisticalStrategy = None
        EmbeddingStrategy = None
    
    try:
        from crawl4ai.adaptive import AdaptiveConfig, AdaptiveCrawlingStrategy
    except ImportError:
        AdaptiveConfig = None
        AdaptiveCrawlingStrategy = None
    
    CRAWL4AI_AVAILABLE = True
except ImportError:
    # Fallback for missing crawl4ai
    StatisticalStrategy = None
    EmbeddingStrategy = None
    AdaptiveConfig = None
    AdaptiveCrawlingStrategy = None
    CRAWL4AI_AVAILABLE = False
except Exception as e:
    # Handle other import errors (like Python version compatibility)
    print(f"Warning: Crawl4AI import failed: {e}")
    StatisticalStrategy = None
    EmbeddingStrategy = None
    AdaptiveConfig = None
    AdaptiveCrawlingStrategy = None
    CRAWL4AI_AVAILABLE = False

# Fallback classes for when crawl4ai is not available
if not CRAWL4AI_AVAILABLE or StatisticalStrategy is None:
    class StatisticalStrategy:
        def __init__(self, **kwargs):
            self.config = kwargs

if not CRAWL4AI_AVAILABLE or EmbeddingStrategy is None:
    class EmbeddingStrategy:
        def __init__(self, **kwargs):
            self.config = kwargs

if not CRAWL4AI_AVAILABLE or AdaptiveConfig is None:
    class AdaptiveConfig:
        def __init__(self, **kwargs):
            self.config = kwargs

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

try:
    from sklearn.cluster import KMeans
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    KMeans = None
    cosine_similarity = None

try:
    import numpy as np
except ImportError:
    np = None

from ..models.adaptive_models import (
    AdaptiveStrategyConfig, AdaptiveMetrics, LearnedPattern,
    StrategyType, ContentType, DomainInsights, PatternAnalysis
)

logger = logging.getLogger(__name__)

class AdaptiveStrategyService:
    """Advanced service for managing adaptive crawling strategies."""
    
    def __init__(self):
        self.strategies_cache: Dict[str, AdaptiveStrategyConfig] = {}
        self.learned_patterns: Dict[str, List[LearnedPattern]] = {}
        self.domain_metrics: Dict[str, AdaptiveMetrics] = {}
        self.embedding_model = None
        self._initialize_embedding_model()
        
        # Domain-specific strategy templates
        self.domain_templates = {
            'news': AdaptiveStrategyConfig(
                strategy_type=StrategyType.HYBRID,
                content_type=ContentType.NEWS,
                min_word_count=200,
                max_word_count=15000,
                content_quality_threshold=0.8,
                similarity_threshold=0.75,
                learning_rate=0.15
            ),
            'social': AdaptiveStrategyConfig(
                strategy_type=StrategyType.EMBEDDING,
                content_type=ContentType.SOCIAL,
                min_word_count=50,
                max_word_count=5000,
                content_quality_threshold=0.6,
                similarity_threshold=0.85,
                learning_rate=0.2
            ),
            'technical': AdaptiveStrategyConfig(
                strategy_type=StrategyType.STATISTICAL,
                content_type=ContentType.TECHNICAL,
                min_word_count=300,
                max_word_count=20000,
                content_quality_threshold=0.9,
                similarity_threshold=0.7,
                learning_rate=0.1
            ),
            'ecommerce': AdaptiveStrategyConfig(
                strategy_type=StrategyType.HYBRID,
                content_type=ContentType.ECOMMERCE,
                min_word_count=100,
                max_word_count=8000,
                content_quality_threshold=0.75,
                similarity_threshold=0.8,
                learning_rate=0.12
            )
        }
    
    def _initialize_embedding_model(self):
        """Initialize the sentence transformer model."""
        if SentenceTransformer is None:
            logger.warning("SentenceTransformer not available. Embedding features will be limited.")
            return
            
        try:
            self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            logger.info("Embedding model initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            self.embedding_model = None
    
    async def get_optimized_strategy(self, url: str, user_config: Optional[AdaptiveStrategyConfig] = None) -> AdaptiveStrategyConfig:
        """Get optimized strategy for a specific URL."""
        domain = urlparse(url).netloc.lower()
        
        # Check cache first
        if domain in self.strategies_cache:
            cached_strategy = self.strategies_cache[domain]
            if user_config:
                # Merge user preferences with cached optimizations
                return self._merge_strategies(cached_strategy, user_config)
            return cached_strategy
        
        # Determine content type from domain
        content_type = self._detect_content_type(domain)
        
        # Get base strategy from templates
        base_strategy = self._get_base_strategy(content_type)
        
        # Apply user customizations
        if user_config:
            strategy = self._merge_strategies(base_strategy, user_config)
        else:
            strategy = base_strategy
        
        # Apply learned optimizations
        if domain in self.learned_patterns:
            strategy = await self._apply_learned_optimizations(strategy, domain)
        
        # Cache the strategy
        self.strategies_cache[domain] = strategy
        
        return strategy
    
    def _detect_content_type(self, domain: str) -> ContentType:
        """Detect content type based on domain patterns."""
        domain_lower = domain.lower()
        
        # News sites
        news_indicators = ['news', 'cnn', 'bbc', 'reuters', 'bloomberg', 'techcrunch', 'verge']
        if any(indicator in domain_lower for indicator in news_indicators):
            return ContentType.NEWS
        
        # Social media
        social_indicators = ['twitter', 'facebook', 'instagram', 'linkedin', 'reddit', 'discord']
        if any(indicator in domain_lower for indicator in social_indicators):
            return ContentType.SOCIAL
        
        # Technical/Documentation
        tech_indicators = ['github', 'stackoverflow', 'docs', 'api', 'developer', 'technical']
        if any(indicator in domain_lower for indicator in tech_indicators):
            return ContentType.TECHNICAL
        
        # E-commerce
        ecommerce_indicators = ['shop', 'store', 'amazon', 'ebay', 'marketplace', 'buy']
        if any(indicator in domain_lower for indicator in ecommerce_indicators):
            return ContentType.ECOMMERCE
        
        # Default to blog
        return ContentType.BLOG
    
    def _get_base_strategy(self, content_type: ContentType) -> AdaptiveStrategyConfig:
        """Get base strategy configuration for content type."""
        type_mapping = {
            ContentType.NEWS: 'news',
            ContentType.SOCIAL: 'social',
            ContentType.TECHNICAL: 'technical',
            ContentType.ECOMMERCE: 'ecommerce'
        }
        
        template_key = type_mapping.get(content_type, 'news')
        return self.domain_templates[template_key].copy(deep=True)
    
    def _merge_strategies(self, base: AdaptiveStrategyConfig, user: AdaptiveStrategyConfig) -> AdaptiveStrategyConfig:
        """Merge user configuration with base strategy."""
        merged = base.copy(deep=True)
        
        # Override with user preferences
        for field, value in user.dict(exclude_unset=True).items():
            setattr(merged, field, value)
        
        return merged
    
    async def _apply_learned_optimizations(self, strategy: AdaptiveStrategyConfig, domain: str) -> AdaptiveStrategyConfig:
        """Apply learned optimizations for a specific domain."""
        patterns = self.learned_patterns.get(domain, [])
        if not patterns:
            return strategy
        
        # Calculate average effectiveness of patterns
        avg_effectiveness = sum(p.effectiveness_score for p in patterns) / len(patterns)
        
        # Adjust strategy based on learned patterns
        if avg_effectiveness > 0.8:
            # High effectiveness - be more aggressive
            strategy.learning_rate = min(strategy.learning_rate * 1.2, 0.5)
            strategy.content_quality_threshold = max(strategy.content_quality_threshold - 0.1, 0.1)
        elif avg_effectiveness < 0.5:
            # Low effectiveness - be more conservative
            strategy.learning_rate = max(strategy.learning_rate * 0.8, 0.01)
            strategy.content_quality_threshold = min(strategy.content_quality_threshold + 0.1, 1.0)
        
        return strategy
    
    def create_statistical_strategy(self, config: AdaptiveStrategyConfig) -> StatisticalStrategy:
        """Create a statistical-based adaptive strategy."""
        return StatisticalStrategy(
            min_word_count=config.min_word_count,
            max_word_count=config.max_word_count,
            content_quality_threshold=config.content_quality_threshold,
            duplicate_threshold=config.duplicate_threshold,
            enable_quality_scoring=True,
            statistical_filters=[
                'word_count', 'sentence_count', 'paragraph_count',
                'link_density', 'text_density', 'content_uniqueness',
                'readability_score', 'semantic_coherence'
            ]
        )
    
    def create_embedding_strategy(self, config: AdaptiveStrategyConfig) -> EmbeddingStrategy:
        """Create an embedding-based adaptive strategy."""
        return EmbeddingStrategy(
            model_name=config.embedding_model,
            similarity_threshold=config.similarity_threshold,
            cluster_content=config.cluster_content,
            semantic_filtering=config.semantic_filtering,
            content_embeddings=True,
            similarity_metrics=['cosine', 'euclidean', 'manhattan']
        )
    
    def create_adaptive_config(self, config: AdaptiveStrategyConfig) -> AdaptiveConfig:
        """Create adaptive configuration."""
        return AdaptiveConfig(
            learning_rate=config.learning_rate,
            pattern_memory_size=config.pattern_memory_size,
            adaptation_threshold=config.adaptation_threshold,
            enable_smart_stopping=config.enable_smart_stopping,
            learning_algorithms=[
                'pattern_recognition', 'content_classification',
                'structure_analysis', 'semantic_clustering'
            ],
            feedback_loop=True,
            performance_monitoring=True
        )
    
    async def learn_from_crawl_result(self, url: str, result: Dict, config: AdaptiveStrategyConfig) -> None:
        """Learn from crawl results to improve future performance."""
        domain = urlparse(url).netloc.lower()
        
        # Extract patterns from successful crawls
        if result.get('success', False):
            patterns = await self._extract_patterns(result, config)
            
            if domain not in self.learned_patterns:
                self.learned_patterns[domain] = []
            
            # Add new patterns
            for pattern in patterns:
                self.learned_patterns[domain].append(pattern)
            
            # Limit pattern memory
            if len(self.learned_patterns[domain]) > config.pattern_memory_size:
                # Keep only the most effective patterns
                self.learned_patterns[domain].sort(key=lambda p: p.effectiveness_score, reverse=True)
                self.learned_patterns[domain] = self.learned_patterns[domain][:config.pattern_memory_size]
        
        # Update domain metrics
        await self._update_domain_metrics(domain, result, config)
    
    async def _extract_patterns(self, result: Dict, config: AdaptiveStrategyConfig) -> List[LearnedPattern]:
        """Extract patterns from crawl results."""
        patterns = []
        
        # Extract content patterns
        if 'content' in result:
            content = result['content']
            
            # Pattern: Content length optimization
            word_count = len(content.split())
            if config.min_word_count <= word_count <= config.max_word_count:
                patterns.append(LearnedPattern(
                    selector='content_length',
                    confidence=0.8,
                    frequency=1,
                    content_type=config.content_type.value if config.content_type else 'unknown',
                    domain=urlparse(result.get('url', '')).netloc,
                    pattern_type='content',
                    effectiveness_score=0.8,
                    last_updated=datetime.now().isoformat(),
                    examples=[f"word_count:{word_count}"]
                ))
        
        # Extract metadata patterns
        if 'metadata' in result:
            metadata = result['metadata']
            
            # Pattern: Processing time optimization
            if 'extraction_time' in metadata:
                extraction_time = metadata['extraction_time']
                if extraction_time < 10:  # Fast extraction
                    patterns.append(LearnedPattern(
                        selector='fast_extraction',
                        confidence=0.9,
                        frequency=1,
                        content_type=config.content_type.value if config.content_type else 'unknown',
                        domain=urlparse(result.get('url', '')).netloc,
                        pattern_type='performance',
                        effectiveness_score=0.9,
                        last_updated=datetime.now().isoformat(),
                        examples=[f"extraction_time:{extraction_time}s"]
                    ))
        
        return patterns
    
    async def _update_domain_metrics(self, domain: str, result: Dict, config: AdaptiveStrategyConfig) -> None:
        """Update metrics for a specific domain."""
        if domain not in self.domain_metrics:
            self.domain_metrics[domain] = AdaptiveMetrics()
        
        metrics = self.domain_metrics[domain]
        
        # Update success rate
        if result.get('success', False):
            metrics.adaptation_success_rate = min(metrics.adaptation_success_rate + 0.1, 1.0)
        else:
            metrics.adaptation_success_rate = max(metrics.adaptation_success_rate - 0.05, 0.0)
        
        # Update processing time
        if 'metadata' in result and 'extraction_time' in result['metadata']:
            metrics.processing_time_ms = int(result['metadata']['extraction_time'] * 1000)
        
        # Update content quality score
        if 'content' in result:
            quality_score = await self._calculate_content_quality(result['content'])
            metrics.content_quality_score = quality_score
        
        # Update learning efficiency
        patterns_count = len(self.learned_patterns.get(domain, []))
        metrics.learning_efficiency = min(patterns_count / config.pattern_memory_size, 1.0)
    
    async def _calculate_content_quality(self, content: str) -> float:
        """Calculate content quality score."""
        if not content:
            return 0.0
        
        # Basic quality metrics
        word_count = len(content.split())
        sentence_count = content.count('.') + content.count('!') + content.count('?')
        paragraph_count = content.count('\n\n') + 1
        
        # Calculate quality score
        word_score = min(word_count / 1000, 1.0) * 0.3
        sentence_score = min(sentence_count / 50, 1.0) * 0.2
        paragraph_score = min(paragraph_count / 10, 1.0) * 0.2
        
        # Uniqueness score (simplified)
        unique_words = len(set(content.lower().split()))
        uniqueness_score = min(unique_words / word_count if word_count > 0 else 0, 1.0) * 0.3
        
        return word_score + sentence_score + paragraph_score + uniqueness_score
    
    def get_domain_insights(self, domain: str) -> DomainInsights:
        """Get insights and recommendations for a domain."""
        patterns = self.learned_patterns.get(domain, [])
        metrics = self.domain_metrics.get(domain)
        
        recommendations = []
        top_patterns = []
        
        if patterns:
            # Sort patterns by effectiveness
            sorted_patterns = sorted(patterns, key=lambda p: p.effectiveness_score, reverse=True)[:5]
            top_patterns = [{
                'selector': p.selector,
                'confidence': p.confidence,
                'effectiveness': p.effectiveness_score,
                'type': p.pattern_type
            } for p in sorted_patterns]
            
            # Generate recommendations
            avg_effectiveness = sum(p.effectiveness_score for p in patterns) / len(patterns)
            if avg_effectiveness > 0.8:
                recommendations.append("High pattern effectiveness - consider increasing learning rate")
            elif avg_effectiveness < 0.5:
                recommendations.append("Low pattern effectiveness - consider adjusting strategy parameters")
        
        if metrics:
            if metrics.adaptation_success_rate > 0.8:
                recommendations.append("High adaptation success rate - strategy is well-optimized")
            elif metrics.adaptation_success_rate < 0.5:
                recommendations.append("Low adaptation success rate - consider strategy review")
        
        return DomainInsights(
            domain=domain,
            patterns_learned=len(patterns),
            recommendations=recommendations,
            performance_metrics=metrics.__dict__ if metrics else {},
            top_patterns=top_patterns,
            success_rate=metrics.adaptation_success_rate if metrics else 0.0,
            avg_processing_time=metrics.processing_time_ms if metrics else 0.0,
            content_quality_avg=metrics.content_quality_score if metrics else 0.0
        )
    
    def get_pattern_analysis(self) -> PatternAnalysis:
        """Get comprehensive pattern analysis across all domains."""
        all_patterns = []
        for patterns in self.learned_patterns.values():
            all_patterns.extend(patterns)
        
        if not all_patterns:
            return PatternAnalysis(
                total_patterns=0,
                effective_patterns=0,
                pattern_types={},
                domain_coverage={},
                effectiveness_distribution={},
                learning_trends=[],
                optimization_opportunities=[]
            )
        
        # Calculate metrics
        effective_patterns = len([p for p in all_patterns if p.effectiveness_score > 0.7])
        
        pattern_types = {}
        domain_coverage = {}
        
        for pattern in all_patterns:
            pattern_types[pattern.pattern_type] = pattern_types.get(pattern.pattern_type, 0) + 1
            domain_coverage[pattern.domain] = domain_coverage.get(pattern.domain, 0) + 1
        
        # Effectiveness distribution
        effectiveness_ranges = {
            'high (0.8-1.0)': len([p for p in all_patterns if p.effectiveness_score >= 0.8]),
            'medium (0.5-0.8)': len([p for p in all_patterns if 0.5 <= p.effectiveness_score < 0.8]),
            'low (0.0-0.5)': len([p for p in all_patterns if p.effectiveness_score < 0.5])
        }
        
        # Optimization opportunities
        optimization_opportunities = []
        if effective_patterns / len(all_patterns) < 0.6:
            optimization_opportunities.append("Consider adjusting learning parameters to improve pattern effectiveness")
        if len(pattern_types) < 3:
            optimization_opportunities.append("Expand pattern recognition to cover more pattern types")
        
        return PatternAnalysis(
            total_patterns=len(all_patterns),
            effective_patterns=effective_patterns,
            pattern_types=pattern_types,
            domain_coverage=domain_coverage,
            effectiveness_distribution=effectiveness_ranges,
            learning_trends=[],  # Could be implemented with historical data
            optimization_opportunities=optimization_opportunities
        )
    
    def clear_domain_cache(self, domain: str) -> bool:
        """Clear cached data for a specific domain."""
        cleared = False
        
        if domain in self.strategies_cache:
            del self.strategies_cache[domain]
            cleared = True
        
        if domain in self.learned_patterns:
            del self.learned_patterns[domain]
            cleared = True
        
        if domain in self.domain_metrics:
            del self.domain_metrics[domain]
            cleared = True
        
        return cleared
    
    def export_learned_patterns(self, domain: Optional[str] = None) -> Dict:
        """Export learned patterns for backup or analysis."""
        if domain:
            patterns = self.learned_patterns.get(domain, [])
            return {
                'domain': domain,
                'patterns': [{
                    'selector': p.selector,
                    'confidence': p.confidence,
                    'frequency': p.frequency,
                    'content_type': p.content_type,
                    'pattern_type': p.pattern_type,
                    'effectiveness_score': p.effectiveness_score,
                    'last_updated': p.last_updated,
                    'examples': p.examples
                } for p in patterns]
            }
        else:
            return {
                'all_domains': {
                    domain: [{
                        'selector': p.selector,
                        'confidence': p.confidence,
                        'frequency': p.frequency,
                        'content_type': p.content_type,
                        'pattern_type': p.pattern_type,
                        'effectiveness_score': p.effectiveness_score,
                        'last_updated': p.last_updated,
                        'examples': p.examples
                    } for p in patterns]
                    for domain, patterns in self.learned_patterns.items()
                }
            }