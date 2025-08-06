"""
Graph store implementation for CRY-A-4MCP.

This module provides a knowledge graph interface using Neo4j for
storing and retrieving cryptocurrency entity relationships.
"""

import asyncio
from typing import Any, Dict, List, Optional, Set

import structlog
from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession
from neo4j.exceptions import Neo4jError

from ..config import Settings


class GraphStore:
    """Knowledge graph store for cryptocurrency entities using Neo4j."""
    
    def __init__(self, settings: Settings) -> None:
        """Initialize the graph store."""
        self.settings = settings
        self.logger = structlog.get_logger(self.__class__.__name__)
        self.driver: Optional[AsyncDriver] = None
    
    async def initialize(self) -> None:
        """Initialize the graph store."""
        self.logger.info("Initializing graph store")
        
        # Initialize Neo4j driver
        self.driver = AsyncGraphDatabase.driver(
            self.settings.neo4j_uri,
            auth=(self.settings.neo4j_username, self.settings.neo4j_password),
            database=self.settings.neo4j_database,
        )
        
        # Test connection
        try:
            await self.driver.verify_connectivity()
            self.logger.info("Connected to Neo4j")
        except Neo4jError as e:
            self.logger.error("Failed to connect to Neo4j", error=str(e))
            raise
        
        # Ensure constraints and indexes
        await self._ensure_schema()
        
        self.logger.info("Graph store initialized")
    
    async def _ensure_schema(self) -> None:
        """Ensure Neo4j schema constraints and indexes exist."""
        async with self.driver.session() as session:
            # Create constraints for uniqueness
            await session.run(
                """
                CREATE CONSTRAINT crypto_symbol_unique IF NOT EXISTS
                FOR (c:Cryptocurrency) REQUIRE c.symbol IS UNIQUE
                """
            )
            
            await session.run(
                """
                CREATE CONSTRAINT exchange_name_unique IF NOT EXISTS
                FOR (e:Exchange) REQUIRE e.name IS UNIQUE
                """
            )
            
            # Create indexes for performance
            await session.run(
                """
                CREATE INDEX crypto_name IF NOT EXISTS
                FOR (c:Cryptocurrency) ON (c.name)
                """
            )
            
            await session.run(
                """
                CREATE INDEX entity_type IF NOT EXISTS
                FOR (e) ON (e:Entity)
                """
            )
    
    async def search(self, entities: List[str], limit: int = 10) -> List[Dict[str, Any]]:
        """Search for entity relationships in the knowledge graph.
        
        Args:
            entities: List of entity identifiers (e.g., crypto symbols)
            limit: Maximum number of results
            
        Returns:
            List of search results with content and metadata
        """
        if not self.driver:
            raise RuntimeError("Graph store not initialized")
        
        self.logger.info("Performing graph search", entities=entities, limit=limit)
        
        results = []
        
        # If no entities provided, return empty results
        if not entities:
            return results
        
        async with self.driver.session() as session:
            # Query for relationships involving the entities
            query = """
            MATCH path = (c:Cryptocurrency)-[r]-(related)
            WHERE c.symbol IN $entities
            RETURN path, c, r, related
            LIMIT $limit
            """
            
            result = await session.run(query, entities=entities, limit=limit)
            
            async for record in result:
                path = record["path"]
                crypto = record["c"]
                relation = record["r"]
                related = record["related"]
                
                # Extract path as a readable string
                path_description = self._format_path(crypto, relation, related)
                
                # Create result dict
                result_dict = {
                    "content": path_description,
                    "score": 0.9,  # Fixed score for now, can be improved
                    "entities": [crypto["symbol"]],
                    "path": [str(node) for node in path.nodes],
                    "relation_type": type(relation).__name__,
                }
                
                results.append(result_dict)
        
        self.logger.info("Graph search completed", results_count=len(results))
        
        return results
    
    def _format_path(self, crypto: Dict, relation: Dict, related: Dict) -> str:
        """Format a graph path as a readable string.
        
        Args:
            crypto: Cryptocurrency node
            relation: Relationship
            related: Related node
            
        Returns:
            Formatted path description
        """
        # Get relation type
        relation_type = type(relation).__name__.replace('_', ' ').title()
        
        # Format based on related node type
        if 'Exchange' in related.labels:
            return f"{crypto['name']} ({crypto['symbol']}) {relation_type} {related['name']}"
        elif 'Person' in related.labels:
            return f"{related['name']} {relation_type} {crypto['name']} ({crypto['symbol']})"
        elif 'Cryptocurrency' in related.labels:
            return f"{crypto['name']} ({crypto['symbol']}) {relation_type} {related['name']} ({related['symbol']})"
        else:
            return f"{crypto['name']} ({crypto['symbol']}) {relation_type} {related.get('name', 'Unknown')}"
    
    async def add_entity(self, entity_type: str, properties: Dict[str, Any]) -> None:
        """Add an entity to the knowledge graph.
        
        Args:
            entity_type: Type of entity (e.g., Cryptocurrency, Exchange)
            properties: Entity properties
        """
        if not self.driver:
            raise RuntimeError("Graph store not initialized")
        
        async with self.driver.session() as session:
            # Create Cypher query based on entity type
            if entity_type == "Cryptocurrency":
                query = """
                MERGE (c:Cryptocurrency:Entity {symbol: $symbol})
                SET c.name = $name,
                    c.description = $description,
                    c.updated_at = datetime()
                RETURN c
                """
            elif entity_type == "Exchange":
                query = """
                MERGE (e:Exchange:Entity {name: $name})
                SET e.url = $url,
                    e.country = $country,
                    e.updated_at = datetime()
                RETURN e
                """
            elif entity_type == "Person":
                query = """
                MERGE (p:Person:Entity {name: $name})
                SET p.role = $role,
                    p.updated_at = datetime()
                RETURN p
                """
            else:
                query = """
                MERGE (e:Entity {id: $id})
                SET e += $properties,
                    e.updated_at = datetime()
                RETURN e
                """
                properties = {"id": properties.get("id", "unknown"), "properties": properties}
            
            await session.run(query, **properties)
    
    async def add_relationship(self, from_entity: Dict[str, Any], 
                             relation_type: str,
                             to_entity: Dict[str, Any],
                             properties: Optional[Dict[str, Any]] = None) -> None:
        """Add a relationship between entities in the knowledge graph.
        
        Args:
            from_entity: Source entity {type, id_field, id_value}
            relation_type: Type of relationship
            to_entity: Target entity {type, id_field, id_value}
            properties: Optional relationship properties
        """
        if not self.driver:
            raise RuntimeError("Graph store not initialized")
        
        if properties is None:
            properties = {}
        
        # Prepare query parameters
        params = {
            "from_type": from_entity["type"],
            "from_id_field": from_entity["id_field"],
            "from_id_value": from_entity["id_value"],
            "to_type": to_entity["type"],
            "to_id_field": to_entity["id_field"],
            "to_id_value": to_entity["id_value"],
            "relation_type": relation_type,
            "properties": properties,
        }
        
        async with self.driver.session() as session:
            query = """
            MATCH (from:{from_type} {{{from_id_field}: $from_id_value}})
            MATCH (to:{to_type} {{{to_id_field}: $to_id_value}})
            MERGE (from)-[r:{relation_type}]->(to)
            SET r += $properties,
                r.updated_at = datetime()
            RETURN r
            """.format(
                from_type=params["from_type"],
                from_id_field=params["from_id_field"],
                to_type=params["to_type"],
                to_id_field=params["to_id_field"],
                relation_type=params["relation_type"],
            )
            
            await session.run(
                query,
                from_id_value=params["from_id_value"],
                to_id_value=params["to_id_value"],
                properties=params["properties"],
            )
    
    async def close(self) -> None:
        """Close the graph store connection."""
        if self.driver:
            await self.driver.close()
            self.driver = None