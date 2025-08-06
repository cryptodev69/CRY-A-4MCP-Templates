# TODO:

- [x] fix_config_id_validation: Fix URL configuration ID type mismatch - backend models define url_config_id as string but validation expects integer (priority: High)
- [x] retrieve_url_from_config: Ensure backend retrieves actual URL from configuration service using the ID (priority: High)
- [x] update_database_insertion: Update database insertion to include the actual URL from configuration (priority: High)
- [x] align_frontend_backend_types: Align frontend URLMappingCreateRequest with backend URLMappingCreate model (url_config_id should be string) (priority: High)
- [x] test_backend_api_endpoints: Test backend API endpoints for URL configurations and extractors to ensure they return valid data (priority: High)
- [x] test_url_mapping_creation: Test URL mapping creation via API call with valid data to verify complete flow (priority: High)
- [x] fix_backend_extractor_array: Update backend URLMappingBase model to use extractor_ids: List[str] instead of extractor_id: str to match frontend (priority: High)
- [ ] test_frontend_form_submission: Test frontend form submission and verify it correctly sends data to backend (priority: High)
- [ ] verify_data_persistence: Verify that created URL mappings are properly stored and retrievable from database (priority: Medium)
- [ ] test_error_handling: Test error scenarios like invalid IDs and missing data to ensure proper validation (priority: Medium)
