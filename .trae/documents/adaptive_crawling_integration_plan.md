# Adaptive Crawling Integration Plan

## 1. Current State Analysis

### Backend API Status
The adaptive crawling backend infrastructure exists with the following components:

- **Endpoint**: `/api/adaptive/crawl` (POST)
- **Models**: `AdaptiveCrawlRequest`, `AdaptiveCrawlResponse`
- **Service**: `adaptive_strategy_service.py`
- **Crawler**: `crawl_with_adaptive_intelligence()` method in `CryptoCrawler`

### Frontend Status
- **TestURL Component**: Currently uses `/api/test-url` endpoint only
- **Missing**: Adaptive crawling UI option and integration
- **Issue**: Lost adaptive crawling code due to git revert

## 2. Frontend Integration Requirements

### TestURL.tsx Modifications Needed

1. **State Variables**:
   ```typescript
   const [useAdaptiveCrawling, setUseAdaptiveCrawling] = useState(false);
   ```

2. **UI Components**:
   - Checkbox for "Enable Adaptive Crawling"
   - Conditional display based on adaptive crawling state
   - Strategy configuration options (when adaptive is enabled)

3. **API Integration**:
   - Modify `handleTest` function to use `/api/adaptive/crawl` when adaptive is enabled
   - Pass extractor information to adaptive endpoint
   - Handle adaptive-specific response format

## 3. Step-by-Step Implementation Plan

### Phase 1: UI Enhancement
1. Add adaptive crawling checkbox to TestURL form
2. Add conditional strategy configuration section
3. Update form validation logic

### Phase 2: API Integration
1. Modify `handleTest` function with conditional endpoint logic
2. Create adaptive crawling request payload
3. Handle adaptive crawling response format

### Phase 3: Backend Verification
1. Verify `/api/adaptive/crawl` endpoint accepts extractor_id
2. Ensure AdaptiveCrawlRequest model supports extractor integration
3. Test adaptive crawling with extractors

### Phase 4: Testing
1. Unit tests for UI components
2. Integration tests for API calls
3. End-to-end testing with real extractors

## 4. API Endpoint Modifications

### Current AdaptiveCrawlRequest Model
```python
class AdaptiveCrawlRequest(BaseModel):
    url: str
    strategy_type: StrategyType = StrategyType.STATISTICAL
    min_word_count: int = 100
    max_word_count: int = 5000
    content_quality_threshold: float = 0.7
    similarity_threshold: float = 0.8
    learning_rate: float = 0.1
    enable_smart_stopping: bool = True
    enable_pattern_learning: bool = True
```

### Required Additions
```python
# Add to AdaptiveCrawlRequest
extractor_id: Optional[str] = None
extractor_config: Optional[Dict[str, Any]] = None
llm_config: Optional[Dict[str, Any]] = None
```

### Endpoint Logic Update
```python
# In adaptive_crawling.py endpoint
if request.extractor_id:
    # Use extractor with adaptive crawling
    result = await crypto_crawler.crawl_with_adaptive_intelligence(
        url=request.url,
        strategy_config=strategy_config,
        extractor_id=request.extractor_id
    )
else:
    # Standard adaptive crawling
    result = await crypto_crawler.crawl_with_adaptive_intelligence(
        url=request.url,
        strategy_config=strategy_config
    )
```

## 5. Frontend Implementation Details

### handleTest Function Logic
```typescript
const handleTest = async (e: React.FormEvent) => {
  e.preventDefault();
  
  if (useAdaptiveCrawling) {
    // Use adaptive crawling endpoint
    const requestBody = {
      url: url,
      strategy_type: "statistical", // or user selection
      extractor_id: useLLM ? null : extractorId,
      llm_config: useLLM ? {
        provider: llmProvider,
        model: llmModel,
        api_key: llmApiKey,
        temperature: llmTemperature,
        max_tokens: llmMaxTokens,
        timeout: llmTimeout
      } : null,
      instruction: useLLM ? llmInstruction : null,
      schema: useLLM && llmSchema ? JSON.parse(llmSchema) : null
    };
    
    const response = await fetch(`${API_BASE_URL}/api/adaptive/crawl`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody)
    });
  } else {
    // Use existing test-url endpoint
    // ... existing logic
  }
};
```

### UI Component Structure
```typescript
{/* Adaptive Crawling Option */}
<div className="flex items-center gap-3 p-4 bg-gray-50 dark:bg-gray-700 rounded-md">
  <input
    type="checkbox"
    id="useAdaptive"
    checked={useAdaptiveCrawling}
    onChange={(e) => setUseAdaptiveCrawling(e.target.checked)}
    className="w-4 h-4 text-purple-600 bg-gray-100 border-gray-300 rounded focus:ring-purple-500"
  />
  <label htmlFor="useAdaptive" className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300">
    <Zap className="w-4 h-4" />
    Enable Adaptive Crawling
  </label>
</div>

{/* Strategy Configuration (when adaptive is enabled) */}
{useAdaptiveCrawling && (
  <div className="space-y-4 p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-md">
    <h3 className="font-medium text-blue-900 dark:text-blue-300 mb-3">
      Adaptive Strategy Configuration
    </h3>
    {/* Strategy options */}
  </div>
)}
```

## 6. Testing Strategy

### Unit Tests
- Test adaptive crawling checkbox functionality
- Test conditional rendering of strategy options
- Test API request payload construction

### Integration Tests
- Test `/api/adaptive/crawl` endpoint with extractor_id
- Test adaptive crawling with LLM configuration
- Test error handling for adaptive crawling failures

### End-to-End Tests
- Complete flow: URL input → adaptive crawling → extractor application → results display
- Test with different extractor types
- Test with different strategy configurations

## 7. Risk Mitigation

### Backward Compatibility
- Ensure existing `/api/test-url` functionality remains unchanged
- Default adaptive crawling to disabled state
- Graceful fallback if adaptive endpoint fails

### Error Handling
- Clear error messages for adaptive crawling failures
- Validation for strategy configuration parameters
- Timeout handling for long-running adaptive operations

## 8. Implementation Checklist

- [ ] Add adaptive crawling checkbox to TestURL UI
- [ ] Implement strategy configuration section
- [ ] Modify handleTest function for conditional endpoint usage
- [ ] Update AdaptiveCrawlRequest model to support extractors
- [ ] Test adaptive endpoint with extractor integration
- [ ] Add comprehensive error handling
- [ ] Create unit and integration tests
- [ ] Document new functionality
- [ ] Commit changes with proper git messages

## 9. Success Criteria

1. **Functional**: Users can enable adaptive crawling and use extractors
2. **Compatible**: Existing functionality remains unaffected
3. **Tested**: All new features have adequate test coverage
4. **Documented**: Clear documentation for new functionality
5. **Stable**: No breaking changes to existing workflows