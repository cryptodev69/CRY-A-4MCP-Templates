# Extraction Strategies Fix - Debug Report

## Issue Identified
**Most likely cause: Missing extractionStrategies field in handleEditCrawler function (90% confidence)**

The `url_mapping_id` and `extraction_strategies` fields were empty because:

1. **handleCreateCrawler**: Was correctly setting `extractionStrategies` but with wrong data type
2. **handleEditCrawler**: Was completely missing the `extractionStrategies` field
3. **Type mismatch**: Frontend expected `ExtractorMapping[]` but was sending `string[]`

## Root Cause Analysis

### Backend (web_api.py)
- ✅ Correctly extracts `extractionStrategies` from request body
- ✅ Properly stores in database as JSON
- ✅ Handles both create and update operations

### Frontend Issues Found
1. **Missing field in edit**: `handleEditCrawler` didn't include `extractionStrategies`
2. **Type mismatch**: Sending strings instead of `ExtractorMapping` objects
3. **Inconsistent data structure**: Create vs Edit had different field handling

## Fix Applied

### Changes Made to `/frontend/src/pages/Crawlers.tsx`

1. **Added extractionStrategies to handleEditCrawler**:
```typescript
extractionStrategies: formData.extractionStrategies || [{
  id: `${formData.crawlerType}_default`,
  name: formData.crawlerType === 'basic' ? 'CSS Extractor' : 'LLM Extractor',
  type: formData.crawlerType === 'basic' ? 'css' : 'llm',
  config: formData.crawlerType === 'basic' ? { selector: 'body' } : { instruction: 'Extract relevant data' },
  priority: 1,
  isActive: true
}]
```

2. **Fixed type structure in handleCreateCrawler**: Same structure as above

3. **Added extractionStrategies field to CrawlerFormData interface** (already done previously)

## Expected Outcome

- ✅ `extraction_strategies` field will now be populated with proper ExtractorMapping objects
- ✅ Both create and edit operations will consistently handle extraction strategies
- ✅ `url_mapping_id` should also be properly set (was already working in backend)

## Next step if this fails:
Check the actual API request payload being sent to verify the data structure matches backend expectations.

## Test Plan
1. Create a new crawler - verify `extraction_strategies` is populated
2. Edit an existing crawler - verify `extraction_strategies` is maintained/updated
3. Check database directly to confirm JSON structure is correct

---
*Fix completed: Frontend now sends proper ExtractorMapping objects instead of strings*