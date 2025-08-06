from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ...storage.url_configuration_db import URLConfigurationDatabase
from ..models_separated import URLManagerCreate, URLManagerUpdate, URLManagerResponse
from ...core.dependencies import get_url_config_db

router = APIRouter(prefix="/url-configurations", tags=["URL Configurations"])

@router.post("/", response_model=URLManagerResponse)
async def create_url_configuration(
    config: URLManagerCreate,
    db: URLConfigurationDatabase = Depends(get_url_config_db)
):
    """Create a new URL configuration."""
    try:
        # Map the priority field to business_priority for the database
        config_data = config.model_dump()
        if 'priority' in config_data:
            config_data['business_priority'] = config_data.pop('priority')
        
        result = await db.create_configuration(**config_data)
        return URLManagerResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create URL configuration: {str(e)}")

@router.get("/", response_model=List[URLManagerResponse])
async def get_url_configurations(
    db: URLConfigurationDatabase = Depends(get_url_config_db)
):
    """Get all URL configurations."""
    try:
        configs = await db.get_all_configurations()
        return [URLManagerResponse(**config) for config in configs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve URL configurations: {str(e)}")

@router.get("/{config_id}", response_model=URLManagerResponse)
async def get_url_configuration(
    config_id: str,
    db: URLConfigurationDatabase = Depends(get_url_config_db)
):
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

@router.put("/{config_id}", response_model=URLManagerResponse)
async def update_url_configuration(
    config_id: str,
    config: URLManagerUpdate,
    db: URLConfigurationDatabase = Depends(get_url_config_db)
):
    """Update a URL configuration."""
    try:
        # Map the priority field to business_priority for the database
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

@router.delete("/{config_id}")
async def delete_url_configuration(
    config_id: str,
    db: URLConfigurationDatabase = Depends(get_url_config_db)
):
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
