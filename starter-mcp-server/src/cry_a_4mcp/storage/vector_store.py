"""
Vector store implementation for CRY-A-4MCP.

This module provides a vector database interface using Qdrant for
storing and retrieving cryptocurrency document embeddings.
"""

import asyncio
from typing import Any, Dict, List, Optional

import structlog
from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models
from sentence_transformers import SentenceTransformer

from ..config import Settings


class VectorStore:
    """Vector store for cryptocurrency document embeddings using Qdrant."""
    
    def __init__(self, settings: Settings) -> None:
        """Initialize the vector store."""
        self.settings = settings
        self.logger = structlog.get_logger(self.__class__.__name__)
        self.client: Optional[QdrantClient] = None
        self.embedding_model: Optional[SentenceTransformer] = None
        self.collection_name = settings.qdrant_collection_name
        self.vector_size = settings.qdrant_vector_size
    
    async def initialize(self) -> None:
        """Initialize the vector store."""
        self.logger.info("Initializing vector store")
        
        # Initialize Qdrant client
        self.client = QdrantClient(
            url=self.settings.qdrant_url,
            api_key=self.settings.qdrant_api_key,
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(
            self.settings.embedding_model,
            device=self.settings.embedding_device,
        )
        
        # Ensure collection exists
        await self._ensure_collection_exists()
        
        self.logger.info("Vector store initialized")
    
    async def _ensure_collection_exists(self) -> None:
        """Ensure the Qdrant collection exists, creating it if necessary."""
        # Run in a thread to avoid blocking
        loop = asyncio.get_event_loop()
        collections = await loop.run_in_executor(
            None, lambda: self.client.get_collections().collections
        )
        
        collection_names = [c.name for c in collections]
        if self.collection_name not in collection_names:
            self.logger.info("Creating vector collection", name=self.collection_name)
            
            # Create collection
            await loop.run_in_executor(
                None,
                lambda: self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=qdrant_models.VectorParams(
                        size=self.vector_size,
                        distance=qdrant_models.Distance.COSINE,
                    ),
                ),
            )
            
            # Create payload index for filtering
            await loop.run_in_executor(
                None,
                lambda: self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="timestamp",
                    field_schema=qdrant_models.PayloadSchemaType.DATETIME,
                ),
            )
    
    async def search(self, query: str, limit: int = 10, 
                    filter_params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for documents similar to the query.
        
        Args:
            query: Search query
            limit: Maximum number of results
            filter_params: Optional filter parameters
            
        Returns:
            List of search results with content and metadata
        """
        if not self.client or not self.embedding_model:
            raise RuntimeError("Vector store not initialized")
        
        self.logger.info("Performing vector search", query=query, limit=limit)
        
        # Generate query embedding
        loop = asyncio.get_event_loop()
        query_embedding = await loop.run_in_executor(
            None, lambda: self.embedding_model.encode(query).tolist()
        )
        
        # Convert filter params to Qdrant filter
        qdrant_filter = None
        if filter_params:
            qdrant_filter = self._build_filter(filter_params)
        
        # Perform search
        search_results = await loop.run_in_executor(
            None,
            lambda: self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                query_filter=qdrant_filter,
                with_payload=True,
            ),
        )
        
        # Format results
        results = []
        for result in search_results:
            # Extract payload
            payload = result.payload or {}
            
            # Create result dict
            result_dict = {
                "id": str(result.id),
                "score": result.score,
                "content": payload.get("content", ""),
                "title": payload.get("title", ""),
                "url": payload.get("url", ""),
                "timestamp": payload.get("timestamp"),
                "source": payload.get("source", ""),
            }
            
            results.append(result_dict)
        
        self.logger.info("Vector search completed", results_count=len(results))
        
        return results
    
    async def add_document(self, content: str, metadata: Dict[str, Any]) -> str:
        """Add a document to the vector store.
        
        Args:
            content: Document content
            metadata: Document metadata
            
        Returns:
            Document ID
        """
        if not self.client or not self.embedding_model:
            raise RuntimeError("Vector store not initialized")
        
        # Generate document embedding
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(
            None, lambda: self.embedding_model.encode(content).tolist()
        )
        
        # Prepare payload
        payload = {"content": content, **metadata}
        
        # Add to Qdrant
        result = await loop.run_in_executor(
            None,
            lambda: self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    qdrant_models.PointStruct(
                        id=metadata.get("id", self.client.http.generate_uuid()),
                        vector=embedding,
                        payload=payload,
                    )
                ],
            ),
        )
        
        return str(result.upserted_count)
    
    def _build_filter(self, filter_params: Dict[str, Any]) -> qdrant_models.Filter:
        """Build a Qdrant filter from filter parameters.
        
        Args:
            filter_params: Filter parameters
            
        Returns:
            Qdrant filter
        """
        conditions = []
        
        # Process date range filter
        if "date_from" in filter_params:
            conditions.append(
                qdrant_models.FieldCondition(
                    key="timestamp",
                    match=qdrant_models.MatchValue(
                        gte=filter_params["date_from"]
                    ),
                )
            )
        
        if "date_to" in filter_params:
            conditions.append(
                qdrant_models.FieldCondition(
                    key="timestamp",
                    match=qdrant_models.MatchValue(
                        lte=filter_params["date_to"]
                    ),
                )
            )
        
        # Process source filter
        if "source" in filter_params:
            conditions.append(
                qdrant_models.FieldCondition(
                    key="source",
                    match=qdrant_models.MatchValue(
                        value=filter_params["source"]
                    ),
                )
            )
        
        # Combine conditions
        if conditions:
            return qdrant_models.Filter(
                must=conditions
            )
        
        return None