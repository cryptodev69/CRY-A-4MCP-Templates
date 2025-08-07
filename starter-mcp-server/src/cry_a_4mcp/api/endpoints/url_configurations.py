from fastapi import APIRouter, HTTPException
from typing import List
from ...storage.url_configuration_db import URLConfigurationDatabase
from ..models_separated import URLManagerCreate, URLManagerUpdate, URLManagerResponse

router = APIRouter(prefix="/url-configurations", tags=["URL Configurations"])

@router.post("/", response_model=URLManagerResponse)
async def create_url_configuration(
    config: URLManagerCreate
):
    """Create a new URL configuration."""
    # This will be overridden by the setup function
    raise HTTPException(status_code=501, detail="Not implemented")

@router.get("/", response_model=List[URLManagerResponse])
async def get_url_configurations():
    """Get all URL configurations."""
    # This will be overridden by the setup function
    raise HTTPException(status_code=501, detail="Not implemented")

@router.get("/{config_id}", response_model=URLManagerResponse)
async def get_url_configuration(
    config_id: str
):
    """Get a specific URL configuration by ID."""
    # This will be overridden by the setup function
    raise HTTPException(status_code=501, detail="Not implemented")

@router.put("/{config_id}", response_model=URLManagerResponse)
async def update_url_configuration(
    config_id: str,
    config: URLManagerUpdate
):
    """Update a URL configuration."""
    # This will be overridden by the setup function
    raise HTTPException(status_code=501, detail="Not implemented")

@router.delete("/{config_id}")
async def delete_url_configuration(
    config_id: str
):
    """Delete a URL configuration."""
    # This will be overridden by the setup function
    raise HTTPException(status_code=501, detail="Not implemented")


def setup_url_configuration_routes(db: URLConfigurationDatabase) -> APIRouter:
    """Setup URL configuration routes with database dependency.
    
    Args:
        db: URLConfigurationDatabase instance
        
    Returns:
        APIRouter: Configured router with URL configuration endpoints
    """
    # Create a new router instance
    config_router = APIRouter(prefix="/url-configurations", tags=["URL Configurations"])
    
    # Override the dependency to use the provided database instance
    def get_db():
        return db
    
    @config_router.post("/", response_model=URLManagerResponse)
    async def create_url_configuration(config: URLManagerCreate):
        """Create a new URL configuration."""
        try:
            config_data = config.model_dump()
            if 'priority' in config_data:
                config_data['business_priority'] = config_data.pop('priority')
            
            result = await db.create_configuration(**config_data)
            return URLManagerResponse(**result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create URL configuration: {str(e)}")
    
    @config_router.get("/", response_model=List[URLManagerResponse])
    async def get_url_configurations():
        """Get all URL configurations."""
        try:
            configs = await db.get_all_configurations()
            return [URLManagerResponse(**config) for config in configs]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve URL configurations: {str(e)}")
    
    @config_router.get("/{config_id}", response_model=URLManagerResponse)
    async def get_url_configuration(config_id: str):
        """Get a specific URL configuration by ID."""
        try:
            config = await db.get_configuration(config_id)
            if not config:
                raise HTTPException(status_code=404, detail="URL configuration not found")
            return URLManagerResponse(**config)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to retrieve URL configuration: {str(e)}")
    
    @config_router.put("/{config_id}", response_model=URLManagerResponse)
    async def update_url_configuration(config_id: str, config: URLManagerUpdate):
        """Update a URL configuration."""
        try:
            config_data = config.model_dump(exclude_unset=True)
            if 'priority' in config_data:
                config_data['business_priority'] = config_data.pop('priority')
            
            result = await db.update_configuration(config_id, **config_data)
            if not result:
                raise HTTPException(status_code=404, detail="URL configuration not found")
            return URLManagerResponse(**result)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update URL configuration: {str(e)}")
    
    @config_router.delete("/{config_id}")
    async def delete_url_configuration(config_id: str):
        """Delete a URL configuration."""
        try:
            success = await db.delete_configuration(config_id)
            if not success:
                raise HTTPException(status_code=404, detail="URL configuration not found")
            return {"message": "URL configuration deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete URL configuration: {str(e)}")
    
    return config_router
