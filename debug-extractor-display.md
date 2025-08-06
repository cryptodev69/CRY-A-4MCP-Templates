# Debug: Extractor Names Not Displaying

## Problem
Extractor names are not displaying on crawler cards despite the card showing "1 extractor(s)".

## Status: NOT FIXED ❌

**Root Cause Confirmed:** Data discrepancy between crawler creation and display
- The "1 extractor(s)" text comes from `URLMappingIntegrationService.ts` at creation time
- `getAppliedExtractors` returns empty array due to mismatch in `extractionStrategies` format
- Expected data structure vs actual data structure mismatch

**Evidence:**
- `URLMappingIntegrationService.ts:274` - generates description with extractor count
- `Crawlers.tsx:495,556-570` - displays this description
- `getAppliedExtractors` function returns empty array despite description showing "1 extractor(s)"

**Code Locations:**
- Description generation: `URLMappingIntegrationService.ts` line 274
- Display logic: `Crawlers.tsx` line 495 (description) and lines 556-570 (extractors)
- Applied extractors logic: `Crawlers.tsx` `getAppliedExtractors` function (lines 282-326)

**Previous Fix Attempt:**
- Modified `getAppliedExtractors` function to handle mixed data formats
- Issue persists - extractor names still not displaying correctly

**CRITICAL FINDING - API Response Analysis:**
The API response from `http://localhost:4000/api/crawlers` reveals the root cause:

```json
{
  "description": "Auto-generated crawler for `https://defipulse.com` using 4 extractor(s)",
  "url_mapping_id": null,
  "extraction_strategies": [],
  "url_mapping_ids": []
}
```

**Root Cause Confirmed:**
1. **Description vs Reality Mismatch**: Description claims "4 extractor(s)" but actual data shows:
   - `url_mapping_id`: null
   - `extraction_strategies`: empty array
   - `url_mapping_ids`: empty array

2. **Data Loss During Persistence**: The extractors are counted during creation but not properly saved to the database

3. **Missing URL Mapping Association**: `url_mapping_id` is null, which means no URL mapping is associated with this crawler

**Next Steps:**
- Investigate the crawler creation/persistence logic in the backend
- Check why `url_mapping_id` and `extraction_strategies` are not being saved
- Verify the relationship between crawlers, URL mappings, and extractors in the database schema

## Expected Fix
Ensure proper data flow from API → crawler.urlMappingIds → URL mappings → extractorIds → extractor names