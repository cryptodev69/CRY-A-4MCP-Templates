# URL Mapping Persistence Issue Analysis

## Problem Summary
- URL mapping selection in crawler form doesn't persist after save/refresh
- Form fields auto-populated from URL mapping are lost
- Data not properly stored/retrieved from database

## Root Cause Analysis

### Data Flow Issues Identified:

1. **Frontend-Backend Field Mapping Mismatch**
   - Frontend sends: `urlMappingId` (singular)
   - Backend expects: `url_mapping_id` AND `url_mapping_ids` (both formats)
   - Database stores: `url_mapping_id` (singular) and `url_mapping_ids` (JSON array)

2. **Form Initialization Problem**
   - `getInitialFormData()` in Crawlers.tsx only uses first URL mapping ID
   - Doesn't properly reconstruct form state when editing
   - URL mapping dropdown not pre-selected when editing

3. **Data Persistence Gap**
   - Backend correctly handles both formats in API endpoints
   - Database schema supports both singular and array formats
   - Frontend form doesn't maintain URL mapping state properly

## Files Requiring Fixes:

1. **Frontend: `/frontend/src/pages/Crawlers.tsx`**
   - Fix `getInitialFormData()` to properly set URL mapping selection
   - Ensure form state includes URL mapping ID for editing

2. **Frontend: `/frontend/src/components/CrawlerFormWithURLMapping.tsx`**
   - Fix initialization logic for editing mode
   - Ensure URL mapping selection persists through form lifecycle

## Next Steps:
1. Fix frontend data transformation
2. Test create/edit/reload cycle
3. Verify URL mapping dropdown pre-selection