# TODO:

- [x] fix_llm_extraction_data_structure: Fix test_url_with_llm method to return LLM extracted data directly instead of nesting it under 'data.llm_extraction' (priority: High)
- [x] update_adaptive_endpoint_data_handling: Update adaptive crawling endpoint to properly handle the corrected LLM data structure (priority: High)
- [x] update_default_llm_schema_instruction: Updated TestURL.tsx with proper default JSON schema and instruction for structured LLM extraction (priority: High)
- [x] enhanced_llm_instruction_and_parsing: Enhanced LLM instruction to explicitly request JSON format and improved JSON parsing to handle markdown code blocks and extract JSON from mixed text responses (priority: High)
- [x] test_fixed_llm_extraction: Test the fixed LLM extraction to ensure structured data is returned correctly (priority: Medium)
- [x] verify_frontend_llm_extraction: Verify that the frontend now shows structured extracted_data instead of raw HTML when using LLM extraction (priority: Medium)
