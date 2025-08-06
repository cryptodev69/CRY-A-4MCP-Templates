# Unfixed Bugs List

## 1. TypeScript Bug - targetUrls Type Issue ❌

**Date:** 2024
**Status:** UNFIXED - Moving on per user request

### Issue
TypeScript error 2322: `targetUrls` property type mismatch in APICrawlerConfig array assignment.

### Root Cause
The `targetUrls` property can be undefined in some crawler objects, but the `APICrawlerConfig` type expects it to be a string array.

### Attempted Fix
Added fallback `|| []` to ensure `targetUrls` is always defined as an array in three locations in Crawlers.tsx.

### Current Status
- Fix applied but TypeScript error persists
- User requested to move on to extractor display functionality
- May require deeper type definition investigation

### Next Steps (if revisited)
1. Check APICrawlerConfig type definition
2. Verify crawler API response structure
3. Consider making targetUrls optional in type definition

## 2. Extractor Display Bug ❌

### Issue
Extractor names are not displaying on crawler cards despite the card showing "1 extractor(s)".

### Status
NOT FIXED - Previous fix attempt failed

### Root Cause - CONFIRMED VIA API ANALYSIS
**Backend Data Persistence Issue**: API response shows data loss during crawler creation:

```json
{
  "description": "Auto-generated crawler for `https://defipulse.com` using 4 extractor(s)",
  "url_mapping_id": null,
  "extraction_strategies": [],
  "url_mapping_ids": []
}
```

**Issues Identified:**
1. Description claims "4 extractor(s)" but `extraction_strategies` is empty
2. `url_mapping_id` is null (no URL mapping association)
3. `url_mapping_ids` is empty array
4. Data loss occurs during persistence, not frontend display

### Previous Fix Attempt
- Modified `getAppliedExtractors` function to handle mixed data formats
- Issue persists because the problem is in backend data persistence, not frontend

### Next Steps
- **BACKEND INVESTIGATION REQUIRED**
- Check crawler creation/persistence logic in backend
- Verify database schema relationships between crawlers, URL mappings, and extractors
- Fix data persistence to properly save `url_mapping_id` and `extraction_strategies`