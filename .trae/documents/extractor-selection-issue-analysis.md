# Extractor Selection Issue Analysis

## Issue Summary

The URL mapping system has a fundamental mismatch between the backend's support for multiple extractors and the frontend's single extractor selection implementation. This creates a limitation where users can only select one extractor per URL mapping, despite the backend being designed to handle multiple extractors.

## Root Cause Analysis

### Backend Architecture (Supports Multiple Extractors)

The backend is properly designed to handle multiple extractors per URL mapping:

1. **Database Schema**: Uses a junction table `URLMappingExtractor` for many-to-many relationships

   ```python
   class URLMappingExtractor(Base):
       __tablename__ = "url_mapping_extractors"
       id = Column(Integer, primary_key=True, autoincrement=True)
       url_mapping_id = Column(Integer, ForeignKey('url_mappings.id', ondelete='CASCADE'), nullable=False)
       extractor_id = Column(Integer, nullable=False)
   ```

2. **Service Layer**: The `create_url_mapping` method iterates through `extractor_ids` array

   ```python
   # Create extractor mappings
   for extractor_id in mapping_data.extractor_ids:
       extractor_mapping = URLMappingExtractor(
           url_mapping_id=db_mapping.id,
           extractor_id=extractor_id
       )
       self.db.add(extractor_mapping)
   ```

3. **Test Coverage**: Tests validate multiple extractor functionality

   ```python
   def test_url_mapping_create_model_empty_extractors(self):
       with pytest.raises(ValueError, match="At least one extractor must be specified"):
           URLMappingCreate(
               name="Test Mapping",
               url_config_id=1,
               extractor_ids=[]  # Array expected
           )
   ```

### Frontend Implementation (Single Extractor Only)

The frontend is implemented for single extractor selection:

1. **Form Data Structure**: Uses singular `extractorId`

   ```typescript
   export interface URLMappingFormData {
     extractorId: string | null;  // Single extractor only
     // ... other fields
   }
   ```

2. **UI Implementation**: Radio button behavior with checkboxes

   ```tsx
   <input
     type="checkbox"
     checked={formData.extractorId === extractor.id}  // Single selection logic
     onChange={(e) => {
       if (e.target.checked) {
         setFormData(prev => ({ ...prev, extractorId: extractor.id }));
       } else {
         setFormData(prev => ({ ...prev, extractorId: null }));
       }
     }}
   />
   ```

3. **Backend Transformation**: Converts single ID to single field

   ```typescript
   transformURLMappingToBackend(mapping: URLMappingFormData): URLMappingCreateRequest {
     return {
       extractor_id: mapping.extractorId!,  // Single extractor sent to backend
       // ... other fields
     };
   }
   ```

## Impact Assessment

### Current Limitations

1. **Functional Limitation**: Users cannot assign multiple extractors to a single URL mapping
2. **UI Confusion**: Checkboxes suggest multiple selection but behave as radio buttons
3. **Backend Underutilization**: The backend's multiple extractor capability is unused
4. **Data Model Mismatch**: Frontend expects single values while backend supports arrays

### Business Impact

1. **Reduced Flexibility**: Cannot apply multiple extraction strategies to the same URL
2. **Inefficient Workflows**: Users must create multiple mappings for the same URL with different extractors
3. **Inconsistent UX**: UI suggests functionality that doesn't work

## Technical Discrepancies

### API Model Mismatch

**Backend Expected (from tests and service):**

```python
class URLMappingCreate(BaseModel):
    extractor_ids: List[int]  # Array of extractor IDs
```

**Current Backend Model (cry\_a\_4mcp/models.py):**

```python
class URLMappingCreate(BaseModel):
    extractor_id: str  # Single extractor ID
```

**Frontend Implementation:**

```typescript
interface URLMappingFormData {
  extractorId: string | null;  // Single extractor
}
```

### Service Implementation Gap

The `url_mapping_service.py` expects `extractor_ids` array but the Pydantic model defines `extractor_id` as singular, creating a disconnect between the service logic and the API contract.

## Recommended Solution

### Phase 1: Backend Model Alignment

1. **Update Pydantic Models**: Change `extractor_id` to `extractor_ids` in URLMappingCreate

   ```python
   class URLMappingCreate(BaseModel):
       extractor_ids: List[str] = Field(..., description="List of extractor IDs to use")
       
       @validator('extractor_ids')
       def validate_extractor_ids(cls, v):
           if not v or len(v) == 0:
               raise ValueError('At least one extractor must be specified')
           return v
   ```

2. **Update API Endpoints**: Ensure all endpoints handle `extractor_ids` arrays

### Phase 2: Frontend Enhancement

1. **Update Form Data Structure**:

   ```typescript
   export interface URLMappingFormData {
     extractorIds: string[];  // Array of extractor IDs
     // ... other fields
   }
   ```

2. **Implement True Multiple Selection**:

   ```tsx
   <input
     type="checkbox"
     checked={formData.extractorIds.includes(extractor.id)}
     onChange={(e) => {
       if (e.target.checked) {
         setFormData(prev => ({
           ...prev,
           extractorIds: [...prev.extractorIds, extractor.id]
         }));
       } else {
         setFormData(prev => ({
           ...prev,
           extractorIds: prev.extractorIds.filter(id => id !== extractor.id)
         }));
       }
     }}
   />
   ```

3. **Update Service Transformation**:

   ```typescript
   transformURLMappingToBackend(mapping: URLMappingFormData): URLMappingCreateRequest {
     return {
       extractor_ids: mapping.extractorIds,  // Send array to backend
       // ... other fields
     };
   }
   ```

### Phase 3: UI/UX Improvements

1. **Selection Counter**: Display "X extractors selected" instead of "1 extractor selected"
2. **Validation**: Ensure at least one extractor is selected
3. **Visual Feedback**: Clear indication of multiple selections
4. **Bulk Operations**: Add "Select All" / "Clear All" functionality

## Migration Strategy

### Backward Compatibility

1. **API Versioning**: Support both single `extractor_id` and array `extractor_ids` during transition
2. **Data Migration**: Convert existing single extractor mappings to arrays
3. **Frontend Fallback**: Handle both response formats during migration

### Testing Requirements

1. **Backend Tests**: Verify multiple extractor creation and retrieval
2. **Frontend Tests**: Test multiple selection UI behavior
3. **Integration Tests**: End-to-end multiple extractor workflows
4. **Migration Tests**: Verify data conversion accuracy

## Conclusion

The extractor selection issue stems from an architectural mismatch where the backend supports multiple extractors but the frontend only implements single selection. The backend service layer and database schema are correctly designed for multiple extractors, but the Pydantic models and frontend implementation need to be updated to fully utilize this capability.

Implementing true multiple extractor selection will:

* Align frontend capabilities

