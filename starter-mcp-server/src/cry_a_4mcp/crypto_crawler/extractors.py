"""Cryptocurrency entity and relationship extractors.

This module provides specialized extractors for cryptocurrency entities
and relationships from web content and other sources.
"""

from typing import Dict, List, Optional, Tuple

from .models import CryptoEntity, CryptoTriple


class CryptoEntityExtractor:
    """Extractor for cryptocurrency entities from text.
    
    This class implements methods to identify and extract cryptocurrency-specific
    entities like tokens, exchanges, protocols, addresses, etc. from text content.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the cryptocurrency entity extractor.
        
        Args:
            config: Optional configuration dictionary for the extractor
        """
        self.config = config or {}
    
    def extract(self, text: str) -> List[CryptoEntity]:
        """Extract cryptocurrency entities from text.
        
        Args:
            text: The text to analyze
            
        Returns:
            List of extracted CryptoEntity objects
        """
        entities = []
        
        # Common cryptocurrency tokens to look for
        crypto_tokens = {
            "Bitcoin": "BTC",
            "Ethereum": "ETH",
            "Binance Coin": "BNB",
            "Cardano": "ADA",
            "Solana": "SOL",
            "XRP": "XRP",
            "Polkadot": "DOT",
            "Dogecoin": "DOGE",
            "Avalanche": "AVAX",
            "Chainlink": "LINK"
        }
        
        # Look for token names and symbols in the text
        for token_name, symbol in crypto_tokens.items():
            if token_name.lower() in text.lower():
                entities.append(CryptoEntity(
                    name=token_name,
                    entity_type="token",
                    symbol=symbol,
                    confidence=0.9,
                    context=f"Found in crawled content"
                ))
            elif symbol.lower() in text.lower():
                entities.append(CryptoEntity(
                    name=token_name,
                    entity_type="token",
                    symbol=symbol,
                    confidence=0.8,
                    context=f"Symbol found in crawled content"
                ))
        
        # Look for specific terms related to Altcoin Season Index
        if "altcoin season" in text.lower() or "altseason" in text.lower():
            entities.append(CryptoEntity(
                name="Altcoin Season Index",
                entity_type="metric",
                confidence=0.95,
                context="Market indicator for altcoin performance"
            ))
        
        # Look for exchanges
        exchanges = ["Binance", "Coinbase", "Kraken", "FTX", "Huobi", "KuCoin"]
        for exchange in exchanges:
            if exchange.lower() in text.lower():
                entities.append(CryptoEntity(
                    name=exchange,
                    entity_type="exchange",
                    confidence=0.85,
                    context=f"Exchange mentioned in content"
                ))
        
        return entities


class CryptoTripleExtractor:
    """Extractor for cryptocurrency relationship triples from text.
    
    This class implements methods to identify and extract subject-predicate-object
    triples related to cryptocurrency from text content.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize the cryptocurrency triple extractor.
        
        Args:
            config: Optional configuration dictionary for the extractor
        """
        self.config = config or {}
        self.entity_extractor = CryptoEntityExtractor(config)
    
    def extract(self, text: str) -> List[CryptoTriple]:
        """Extract cryptocurrency relationship triples from text.
        
        Args:
            text: The text to analyze
            
        Returns:
            List of extracted CryptoTriple objects
        """
        triples = []
        
        # First extract entities to use as subjects and objects
        entities = self.entity_extractor.extract(text)
        
        # Create a mapping of entity names to their types
        entity_types = {entity.name: entity.entity_type for entity in entities}
        
        # Look for specific relationships in the Altcoin Season Index context
        if "Altcoin Season Index" in entity_types:
            # If Bitcoin is mentioned, create a relationship with Altcoin Season Index
            if "Bitcoin" in entity_types:
                triples.append(CryptoTriple(
                    subject="Altcoin Season Index",
                    predicate="compares_with",
                    object="Bitcoin",
                    confidence=0.9,
                    source="Altcoin Season Index page"
                ))
            
            # For each altcoin mentioned, create a relationship
            for entity in entities:
                if entity.entity_type == "token" and entity.name != "Bitcoin":
                    triples.append(CryptoTriple(
                        subject=entity.name,
                        predicate="measured_by",
                        object="Altcoin Season Index",
                        confidence=0.85,
                        source="Altcoin Season Index page"
                    ))
        
        # Look for exchange relationships
        for entity in entities:
            if entity.entity_type == "exchange":
                # For each token, create a relationship with the exchange
                for other_entity in entities:
                    if other_entity.entity_type == "token":
                        triples.append(CryptoTriple(
                            subject=other_entity.name,
                            predicate="trades_on",
                            object=entity.name,
                            confidence=0.7,
                            source="Inferred from content"
                        ))
        
        return triples