# Dropdown Selection Issue Debug Log

## Problem
URL Mapping dropdown not showing selected value when editing a crawler.

## Root Cause Analysis

### Issue Found
In `Crawlers.tsx`, the data transformation logic has a flaw:

```typescript
const apiCrawlers: APICrawlerConfig[] = (crawlersResponse.data.items || []).map(crawler => ({
  ...crawler,
  urlMappingIds: crawler.urlMappings?.map(mapping => mapping.id) || [],
  // ...
}));
```

When the API response doesn't include populated `urlMappings` (which appears to be the case), `urlMappingIds` becomes an empty array `[]`.

Then in `getInitialFormData`:
```typescript
const activeUrlMappingId = crawler.urlMappingIds?.[0]; // This becomes undefined
```

This causes the dropdown to not show any selection because `selectedMappingId` is empty.

## Console Evidence
From browser console logs:
- `selectedMappingId` is empty
- `dropdownOptions` has length 3 (URL mappings are loaded)
- `urlMappings` and `extractors` objects are properly loaded

## Solution
Need to check the actual API response structure and ensure `urlMappingIds` is properly populated from the backend data.

## Confidence: 90%
This explains why the dropdown options are available but no selection is shown.