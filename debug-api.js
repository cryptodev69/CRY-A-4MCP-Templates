// Debug script to test API endpoints directly
const fetch = require('node-fetch');

const API_BASE_URL = 'http://localhost:4000';

async function testAPI() {
  console.log('Testing API endpoints...');
  
  try {
    // Test URL Configurations
    console.log('\n=== Testing URL Configurations ===');
    const configResponse = await fetch(`${API_BASE_URL}/api/url-configurations/?limit=1000`);
    const configData = await configResponse.json();
    console.log('URL Configurations Response:', JSON.stringify(configData, null, 2));
    
    // Test URL Mappings
    console.log('\n=== Testing URL Mappings ===');
    const mappingsResponse = await fetch(`${API_BASE_URL}/api/url-mappings/?limit=1000`);
    const mappingsData = await mappingsResponse.json();
    console.log('URL Mappings Response:', JSON.stringify(mappingsData, null, 2));
    
    // Test Extractors
    console.log('\n=== Testing Extractors ===');
    const extractorsResponse = await fetch(`${API_BASE_URL}/api/extractors/`);
    const extractorsData = await extractorsResponse.json();
    console.log('Extractors Response:', JSON.stringify(extractorsData, null, 2));
    
  } catch (error) {
    console.error('API Test Error:', error);
  }
}

testAPI();