# **CRITICAL PROJECT NOTES**

## **DO NOT CONFUSE THESE APPLICATIONS:**

### **simple_web_api.py IS FOR A COMPLETELY DIFFERENT APPLICATION**
- **simple_web_api.py** is NOT part of the URL mappings frontend
- **simple_web_api.py** has `/api/url-configs` endpoints - WRONG APP
- **DO NOT LOOK AT simple_web_api.py FOR URL MAPPINGS ISSUES**

### **CORRECT BACKEND FOR URL MAPPINGS:**
- The frontend expects `/api/url-mappings` endpoints
- The correct backend is in **web_api.py** (lines 735-790 confirmed)
- **web_api.py** has the proper FastAPI endpoints:
  - GET `/api/url-mappings`
  - POST `/api/url-mappings` 
  - GET `/api/url-mappings/{mapping_id}`
  - PUT `/api/url-mappings/{mapping_id}`
  - DELETE `/api/url-mappings/{mapping_id}`

## **START SCRIPT LOCATION**

**THE START SCRIPT IS LOCATED AT:**
**`/Users/soulmynd/Documents/Programming/Crypto AI platform/CRY-A-4MCP-Templates/start-dev.sh`**

- This script starts both frontend and backend servers
- Backend runs on port 4000 using `python -m src.cry_a_4mcp.web_api`
- Frontend runs on port 3000 (or alternative if needed)
- To use: `./start-dev.sh` from project root
- **STOP SEARCHING FOR HOW TO RUN WEB_API - USE THIS SCRIPT!**

### **CURRENT ISSUE:**
- Frontend shows "No URL mappings available"
- Need to check if **web_api.py** backend server is running
- Need to verify the correct startup process for **web_api.py**