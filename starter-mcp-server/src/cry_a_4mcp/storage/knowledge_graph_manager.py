"""
Knowledge Graph Manager for CRY-A-4MCP.

This module provides a Neo4j-based knowledge graph manager for storing and
querying cryptocurrency entities and their relationships.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import structlog
from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession
from neo4j.exceptions import Neo4jError

from ..config import Settings


class EntityType(str, Enum):
    """Type of entity in the knowledge graph."""
    CRYPTOCURRENCY = "Cryptocurrency"
    EXCHANGE = "Exchange"
    PERSON = "Person"
    ORGANIZATION = "Organization"
    TECHNOLOGY = "Technology"
    EVENT = "Event"
    CONCEPT = "Concept"


class RelationshipType(str, Enum):
    """Type of relationship in the knowledge graph."""
    TRADES_ON = "TRADES_ON"  # Cryptocurrency -> Exchange
    FOUNDED_BY = "FOUNDED_BY"  # Cryptocurrency -> Person
    DEVELOPED_BY = "DEVELOPED_BY"  # Cryptocurrency -> Organization
    USES = "USES"  # Cryptocurrency -> Technology
    AFFECTED_BY = "AFFECTED_BY"  # Cryptocurrency -> Event
    RELATED_TO = "RELATED_TO"  # Generic relationship
    COMPETES_WITH = "COMPETES_WITH"  # Cryptocurrency -> Cryptocurrency
    FORKED_FROM = "FORKED_FROM"  # Cryptocurrency -> Cryptocurrency
    INVESTED_IN = "INVESTED_IN"  # Person/Organization -> Cryptocurrency


@dataclass
class GraphEntity:
    """Entity in the knowledge graph."""
    id: str
    name: str
    type: EntityType
    properties: Dict[str, Any] = None

    def __post_init__(self):
        if self.properties is None:
            self.properties = {}


@dataclass
class GraphRelationship:
    """Relationship in the knowledge graph."""
    source_id: str
    target_id: str
    type: RelationshipType
    properties: Dict[str, Any] = None

    def __post_init__(self):
        if self.properties is None:
            self.properties = {}


@dataclass
class GraphPath:
    """Path in the knowledge graph."""
    entities: List[GraphEntity]
    relationships: List[GraphRelationship]
    score: float = 0.0


class KnowledgeGraphManager:
    """Neo4j-based knowledge graph manager for cryptocurrency entities and relationships."""
    
    def __init__(self, settings: Settings) -> None:
        """Initialize the knowledge graph manager.
        
        Args:
            settings: Application settings
        """
        self.settings = settings
        self.logger = structlog.get_logger(self.__class__.__name__)
        self.driver: Optional[AsyncDriver] = None
    
    async def initialize(self) -> None:
        """Initialize the knowledge graph manager."""
        self.logger.info("Initializing knowledge graph manager")
        
        # Connect to Neo4j
        try:
            self.driver = AsyncGraphDatabase.driver(
                self.settings.neo4j_uri,
                auth=(self.settings.neo4j_username, self.settings.neo4j_password)
            )
            
            # Test connection
            async with self.driver.session(database=self.settings.neo4j_database) as session:
                result = await session.run("RETURN 1 AS test")
                record = await result.single()
                if record and record.get("test") == 1:
                    self.logger.info("Successfully connected to Neo4j")
                else:
                    self.logger.error("Failed to verify Neo4j connection")
                    raise RuntimeError("Failed to verify Neo4j connection")
            
            # Create constraints and indexes
            await self._create_constraints_and_indexes()
            
            self.logger.info("Knowledge graph manager initialized")
        except Exception as e:
            self.logger.error("Failed to initialize knowledge graph manager", error=str(e))
            if self.driver:
                await self.driver.close()
                self.driver = None
            raise
    
    async def close(self) -> None:
        """Close the knowledge graph manager."""
        if self.driver:
            await self.driver.close()
            self.driver = None
            self.logger.info("Knowledge graph manager closed")
    
    async def _create_constraints_and_indexes(self) -> None:
        """Create constraints and indexes in Neo4j."""
        async with self.driver.session(database=self.settings.neo4j_database) as session:
            # Create constraints for entity types
            for entity_type in EntityType:
                # Create constraint on id property
                try:
                    await session.run(
                        f"CREATE CONSTRAINT {entity_type.value}_id_constraint IF NOT EXISTS "
                        f"FOR (n:{entity_type.value}) REQUIRE n.id IS UNIQUE"
                    )
                    self.logger.info(f"Created constraint for {entity_type.value} id")
                except Neo4jError as e:
                    self.logger.warning(f"Failed to create constraint for {entity_type.value}", error=str(e))
                
                # Create index on name property
                try:
                    await session.run(
                        f"CREATE INDEX {entity_type.value}_name_index IF NOT EXISTS "
                        f"FOR (n:{entity_type.value}) ON (n.name)"
                    )
                    self.logger.info(f"Created index for {entity_type.value} name")
                except Neo4jError as e:
                    self.logger.warning(f"Failed to create index for {entity_type.value}", error=str(e))
    
    async def add_entity(self, entity: GraphEntity) -> bool:
        """Add an entity to the knowledge graph.
        
        Args:
            entity: Entity to add
            
        Returns:
            True if successful, False otherwise
        """
        if not self.driver:
            self.logger.error("Knowledge graph manager not initialized")
            return False
        
        try:
            async with self.driver.session(database=self.settings.neo4j_database) as session:
                # Prepare properties
                properties = {"id": entity.id, "name": entity.name}
                if entity.properties:
                    properties.update(entity.properties)
                
                # Add timestamp if not present
                if "created_at" not in properties:
                    properties["created_at"] = datetime.now().isoformat()
                
                # Create entity
                result = await session.run(
                    f"MERGE (n:{entity.type.value} {{id: $id}}) "
                    "ON CREATE SET n = $properties "
                    "ON MATCH SET n += $updated_properties "
                    "RETURN n",
                    id=entity.id,
                    properties=properties,
                    updated_properties={"updated_at": datetime.now().isoformat()}
                )
                
                record = await result.single()
                return record is not None
        except Exception as e:
            self.logger.error("Failed to add entity", error=str(e), entity_id=entity.id)
            return False
    
    async def add_relationship(self, relationship: GraphRelationship) -> bool:
        """Add a relationship to the knowledge graph.
        
        Args:
            relationship: Relationship to add
            
        Returns:
            True if successful, False otherwise
        """
        if not self.driver:
            self.logger.error("Knowledge graph manager not initialized")
            return False
        
        try:
            async with self.driver.session(database=self.settings.neo4j_database) as session:
                # Prepare properties
                properties = {}
                if relationship.properties:
                    properties.update(relationship.properties)
                
                # Add timestamp if not present
                if "created_at" not in properties:
                    properties["created_at"] = datetime.now().isoformat()
                
                # Create relationship
                result = await session.run(
                    "MATCH (a {id: $source_id}), (b {id: $target_id}) "
                    f"MERGE (a)-[r:{relationship.type.value}]->(b) "
                    "ON CREATE SET r = $properties "
                    "ON MATCH SET r += $updated_properties "
                    "RETURN r",
                    source_id=relationship.source_id,
                    target_id=relationship.target_id,
                    properties=properties,
                    updated_properties={"updated_at": datetime.now().isoformat()}
                )
                
                record = await result.single()
                return record is not None
        except Exception as e:
            self.logger.error("Failed to add relationship", error=str(e), 
                            source=relationship.source_id, target=relationship.target_id)
            return False
    
    async def get_entity(self, entity_id: str) -> Optional[GraphEntity]:
        """Get an entity from the knowledge graph.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            Entity if found, None otherwise
        """
        if not self.driver:
            self.logger.error("Knowledge graph manager not initialized")
            return None
        
        try:
            async with self.driver.session(database=self.settings.neo4j_database) as session:
                result = await session.run(
                    "MATCH (n {id: $id}) RETURN n",
                    id=entity_id
                )
                
                record = await result.single()
                if not record:
                    return None
                
                node = record.get("n")
                properties = dict(node.items())
                entity_id = properties.pop("id")
                entity_name = properties.pop("name")
                
                # Determine entity type from labels
                entity_type = None
                for label in node.labels:
                    try:
                        entity_type = EntityType(label)
                        break
                    except ValueError:
                        continue
                
                if not entity_type:
                    self.logger.warning("Unknown entity type", labels=list(node.labels))
                    return None
                
                return GraphEntity(
                    id=entity_id,
                    name=entity_name,
                    type=entity_type,
                    properties=properties
                )
        except Exception as e:
            self.logger.error("Failed to get entity", error=str(e), entity_id=entity_id)
            return None
    
    async def search_entities(self, query: str, entity_types: Optional[List[EntityType]] = None, 
                             limit: int = 10) -> List[GraphEntity]:
        """Search for entities in the knowledge graph.
        
        Args:
            query: Search query
            entity_types: Optional list of entity types to filter by
            limit: Maximum number of results
            
        Returns:
            List of matching entities
        """
        if not self.driver:
            self.logger.error("Knowledge graph manager not initialized")
            return []
        
        try:
            async with self.driver.session(database=self.settings.neo4j_database) as session:
                # Build query
                cypher_query = "MATCH (n)"
                
                # Add entity type filter if provided
                if entity_types:
                    labels = [f"n:{t.value}" for t in entity_types]
                    cypher_query += f" WHERE {' OR '.join(labels)}"
                
                # Add name search
                if entity_types:
                    cypher_query += " AND "
                else:
                    cypher_query += " WHERE "
                
                cypher_query += "n.name =~ $name_pattern OR n.id =~ $id_pattern"
                
                # Add return and limit
                cypher_query += " RETURN n LIMIT $limit"
                
                # Execute query
                result = await session.run(
                    cypher_query,
                    name_pattern=f"(?i).*{query}.*",
                    id_pattern=f"(?i).*{query}.*",
                    limit=limit
                )
                
                entities = []
                async for record in result:
                    node = record.get("n")
                    properties = dict(node.items())
                    entity_id = properties.pop("id")
                    entity_name = properties.pop("name")
                    
                    # Determine entity type from labels
                    entity_type = None
                    for label in node.labels:
                        try:
                            entity_type = EntityType(label)
                            break
                        except ValueError:
                            continue
                    
                    if not entity_type:
                        self.logger.warning("Unknown entity type", labels=list(node.labels))
                        continue
                    
                    entities.append(GraphEntity(
                        id=entity_id,
                        name=entity_name,
                        type=entity_type,
                        properties=properties
                    ))
                
                return entities
        except Exception as e:
            self.logger.error("Failed to search entities", error=str(e), query=query)
            return []
    
    async def find_paths(self, source_id: str, target_id: str, max_depth: int = 3, 
                        relationship_types: Optional[List[RelationshipType]] = None) -> List[GraphPath]:
        """Find paths between two entities in the knowledge graph.
        
        Args:
            source_id: Source entity ID
            target_id: Target entity ID
            max_depth: Maximum path depth
            relationship_types: Optional list of relationship types to filter by
            
        Returns:
            List of paths
        """
        if not self.driver:
            self.logger.error("Knowledge graph manager not initialized")
            return []
        
        try:
            async with self.driver.session(database=self.settings.neo4j_database) as session:
                # Build query
                cypher_query = "MATCH path = (source {id: $source_id})-"
                
                # Add relationship filter if provided
                if relationship_types:
                    rel_types = "|".join([t.value for t in relationship_types])
                    cypher_query += f"[:{rel_types}*1..{max_depth}]"
                else:
                    cypher_query += f"[*1..{max_depth}]"
                
                cypher_query += "-(target {id: $target_id}) "
                cypher_query += "RETURN path ORDER BY length(path) LIMIT 10"
                
                # Execute query
                result = await session.run(
                    cypher_query,
                    source_id=source_id,
                    target_id=target_id
                )
                
                paths = []
                async for record in result:
                    path = record.get("path")
                    
                    # Extract entities
                    entities = []
                    for node in path.nodes:
                        properties = dict(node.items())
                        entity_id = properties.pop("id")
                        entity_name = properties.pop("name")
                        
                        # Determine entity type from labels
                        entity_type = None
                        for label in node.labels:
                            try:
                                entity_type = EntityType(label)
                                break
                            except ValueError:
                                continue
                        
                        if not entity_type:
                            self.logger.warning("Unknown entity type", labels=list(node.labels))
                            continue
                        
                        entities.append(GraphEntity(
                            id=entity_id,
                            name=entity_name,
                            type=entity_type,
                            properties=properties
                        ))
                    
                    # Extract relationships
                    relationships = []
                    for rel in path.relationships:
                        properties = dict(rel.items())
                        
                        # Determine relationship type
                        try:
                            rel_type = RelationshipType(rel.type)
                        except ValueError:
                            self.logger.warning("Unknown relationship type", type=rel.type)
                            continue
                        
                        relationships.append(GraphRelationship(
                            source_id=rel.start_node["id"],
                            target_id=rel.end_node["id"],
                            type=rel_type,
                            properties=properties
                        ))
                    
                    # Calculate path score (inverse of path length for now)
                    score = 1.0 / len(relationships) if relationships else 0.0
                    
                    paths.append(GraphPath(
                        entities=entities,
                        relationships=relationships,
                        score=score
                    ))
                
                return paths
        except Exception as e:
            self.logger.error("Failed to find paths", error=str(e), 
                            source=source_id, target=target_id)
            return []
    
    async def find_related_entities(self, entity_id: str, relationship_types: Optional[List[RelationshipType]] = None,
                                  entity_types: Optional[List[EntityType]] = None, 
                                  limit: int = 10) -> List[Tuple[GraphEntity, RelationshipType]]:
        """Find entities related to a given entity.
        
        Args:
            entity_id: Entity ID
            relationship_types: Optional list of relationship types to filter by
            entity_types: Optional list of entity types to filter by
            limit: Maximum number of results
            
        Returns:
            List of (entity, relationship_type) tuples
        """
        if not self.driver:
            self.logger.error("Knowledge graph manager not initialized")
            return []
        
        try:
            async with self.driver.session(database=self.settings.neo4j_database) as session:
                # Build query
                cypher_query = "MATCH (source {id: $entity_id})-[r]->(target)"
                
                # Add filters
                filters = []                
                if relationship_types:
                    rel_types = [t.value for t in relationship_types]
                    rel_types_str = ', '.join([f"'{t}'" for t in rel_types])
                    filters.append(f"type(r) IN [{rel_types_str}]")
                
                if entity_types:
                    entity_filters = []
                    for t in entity_types:
                        entity_filters.append(f"target:{t.value}")
                    filters.append(f"({' OR '.join(entity_filters)})")
                
                if filters:
                    cypher_query += " WHERE " + " AND ".join(filters)
                
                # Add return and limit
                cypher_query += " RETURN target, type(r) LIMIT $limit"
                
                # Execute query
                result = await session.run(
                    cypher_query,
                    entity_id=entity_id,
                    limit=limit
                )
                
                related = []
                async for record in result:
                    node = record.get("target")
                    rel_type_str = record.get("type(r)")
                    
                    properties = dict(node.items())
                    entity_id = properties.pop("id")
                    entity_name = properties.pop("name")
                    
                    # Determine entity type from labels
                    entity_type = None
                    for label in node.labels:
                        try:
                            entity_type = EntityType(label)
                            break
                        except ValueError:
                            continue
                    
                    if not entity_type:
                        self.logger.warning("Unknown entity type", labels=list(node.labels))
                        continue
                    
                    # Determine relationship type
                    try:
                        rel_type = RelationshipType(rel_type_str)
                    except ValueError:
                        self.logger.warning("Unknown relationship type", type=rel_type_str)
                        continue
                    
                    related.append((
                        GraphEntity(
                            id=entity_id,
                            name=entity_name,
                            type=entity_type,
                            properties=properties
                        ),
                        rel_type
                    ))
                
                return related
        except Exception as e:
            self.logger.error("Failed to find related entities", error=str(e), entity_id=entity_id)
            return []
    
    async def execute_cypher(self, query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute a custom Cypher query.
        
        Args:
            query: Cypher query
            params: Query parameters
            
        Returns:
            List of result records as dictionaries
        """
        if not self.driver:
            self.logger.error("Knowledge graph manager not initialized")
            return []
        
        try:
            async with self.driver.session(database=self.settings.neo4j_database) as session:
                result = await session.run(query, params or {})
                
                records = []
                async for record in result:
                    record_dict = {}
                    for key, value in record.items():
                        record_dict[key] = value
                    records.append(record_dict)
                
                return records
        except Exception as e:
            self.logger.error("Failed to execute Cypher query", error=str(e), query=query)
            return []