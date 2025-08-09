# Debugging Principles for UI-API Communication

## MANDATORY DEBUGGING PROTOCOL

**READ THIS DOCUMENT BEFORE ANY DEBUGGING SESSION**

### Rule #1: Frontend First, Backend Second

When debugging UI issues with API calls:

1. **ALWAYS CHECK FRONTEND API ENDPOINTS FIRST**
   - Verify the frontend is calling the correct API endpoint URLs
   - Check HTTP methods (GET, POST, PUT, DELETE)
   - Validate request payload structure
   - Confirm API base URL configuration

2. **THEN CHECK BACKEND IMPLEMENTATION**
   - Only after confirming frontend endpoints are correct
   - Verify backend route definitions
   - Check backend service initialization
   - Test backend endpoints independently

### Common Frontend-Backend Mismatches

- **Endpoint URL mismatch**: Frontend calls `/api/crawl/adaptive` but backend expects `/api/adaptive/crawl`
- **HTTP method mismatch**: Frontend sends GET but backend expects POST
- **Payload structure**: Frontend sends different JSON structure than backend expects
- **Base URL configuration**: Frontend uses wrong API base URL

### Debugging Workflow

```
1. UI Issue Reported
   ↓
2. Check Frontend API Calls
   - Inspect network tab in browser dev tools
   - Verify endpoint URLs in frontend code
   - Check request methods and payloads
   ↓
3. Compare with Backend Routes
   - Match frontend endpoints with backend route definitions
   - Verify HTTP methods align
   - Confirm payload expectations
   ↓
4. Fix Mismatches (if any)
   - Update frontend endpoint URLs
   - Align HTTP methods
   - Fix payload structures
   ↓
5. Test Backend (only if frontend is correct)
   - Test backend endpoints independently
   - Check service initialization
   - Verify backend logs
```

### Anti-Patterns to Avoid

❌ **DON'T**: Test backend repeatedly without checking frontend endpoints
❌ **DON'T**: Assume backend is the problem when UI shows errors
❌ **DON'T**: Skip frontend verification when debugging API issues

✅ **DO**: Always start with frontend endpoint verification
✅ **DO**: Use browser dev tools to inspect actual API calls
✅ **DO**: Compare frontend and backend endpoint definitions side-by-side

### Tools for Frontend API Debugging

1. **Browser Developer Tools**
   - Network tab to see actual API calls
   - Console for JavaScript errors
   - Sources tab to check frontend code

2. **Code Inspection**
   - Search for API endpoint strings in frontend code
   - Check API configuration files
   - Verify environment variables for API URLs

### Example: Adaptive Crawler Issue

**Problem**: UI shows 404 error when testing adaptive crawler

**Wrong Approach**: Test backend `/api/adaptive/crawl` endpoint repeatedly

**Correct Approach**:
1. Check frontend code for API call
2. Found: Frontend calls `/api/crawl/adaptive`
3. Check backend routes
4. Found: Backend expects `/api/adaptive/crawl`
5. Fix: Update frontend to use correct endpoint
6. Result: Issue resolved

---

**REMEMBER: Frontend endpoint verification is the foundation of effective UI-API debugging. Always start there.**