# Edit Modal Debug - Data Loading Issue

## Most likely cause: 85% confidence
The edit modal validation requires both `urlMappings.length > 0` AND `extractors.length > 0`, but one or both arrays are empty when the edit button is clicked.

## Root Cause Analysis
**Location**: `/frontend/src/pages/Crawlers.tsx` lines 280-283

```typescript
if (urlMappings.length === 0 || extractors.length === 0) {
  console.warn('Cannot open edit modal: URL mappings or extractors not yet loaded');
  return;
}
```

**Data Loading Logic**: Lines 60-86
- `api.getMappings()` loads URL mappings
- `api.getExtractors()` loads extractors
- Error handling sets empty arrays on failure

## Debug Changes Made
Added comprehensive logging to `openEditModal()` function to capture:
- `urlMappingsCount` and `extractorsCount`
- Full `urlMappings` and `extractors` arrays
- Current state when validation fails

## Next step if this fails:
Manual browser testing required:
1. Open http://localhost:3000
2. Open browser console (F12)
3. Click any "Edit" button on a crawler
4. Check console for debug logs:
   - "Edit modal attempt:" with data counts
   - "Cannot open edit modal:" warning if blocked
   - "Current state:" with array lengths

## Expected Findings
One of these scenarios:
- `urlMappingsCount: 0` - API call failed or returned empty
- `extractorsCount: 0` - API call failed or returned empty  
- Both counts > 0 - Different validation issue

## Circuit Breaker
If same "Cannot open edit modal" error appears after this debug session, escalate to backend API investigation.