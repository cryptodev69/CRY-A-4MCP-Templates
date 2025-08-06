/**
 * Test script for URL mapping creation
 * This script tests the URL mapping API endpoint to ensure it works properly
 */

const testURLMappingCreation = async () => {
  const baseUrl = 'http://localhost:4000';
  
  console.log('🧪 Testing URL Mapping Creation...');
  
  // Test data for creating a URL mapping
  const testMapping = {
    name: `Test Mapping ${Date.now()}`,
    url_config_id: 1,
    extractor_ids: [1, 2], // Multiple extractors
    rate_limit: 60,
    priority: 5,
    is_active: true,
    metadata: {},
    validation_rules: {},
    crawler_settings: {
      timeout: 30000,
      retryAttempts: 3,
      retryDelay: 1000
    },
    tags: ['test'],
    notes: 'Test mapping created by script',
    category: 'test'
  };
  
  try {
    console.log('📤 Sending POST request to create URL mapping...');
    console.log('Data:', JSON.stringify(testMapping, null, 2));
    
    const response = await fetch(`${baseUrl}/api/url-mappings`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(testMapping)
    });
    
    console.log('📥 Response status:', response.status);
    console.log('📥 Response headers:', Object.fromEntries(response.headers.entries()));
    
    const responseText = await response.text();
    console.log('📥 Response body:', responseText);
    
    if (response.ok) {
      console.log('✅ URL mapping creation successful!');
      try {
        const responseData = JSON.parse(responseText);
        console.log('📋 Created mapping:', responseData);
      } catch (e) {
        console.log('⚠️ Response is not JSON:', responseText);
      }
    } else {
      console.log('❌ URL mapping creation failed!');
      console.log('Error details:', responseText);
    }
    
  } catch (error) {
    console.error('❌ Network error:', error.message);
  }
};

// Test extractors endpoint
const testExtractorsEndpoint = async () => {
  const baseUrl = 'http://localhost:4000';
  
  console.log('\n🧪 Testing Extractors Endpoint...');
  
  try {
    const response = await fetch(`${baseUrl}/api/extractors`);
    console.log('📥 Extractors response status:', response.status);
    
    const responseText = await response.text();
    console.log('📥 Extractors response:', responseText);
    
    if (response.ok && responseText) {
      try {
        const extractors = JSON.parse(responseText);
        console.log('✅ Extractors loaded:', extractors.length, 'items');
        console.log('📋 Sample extractors:', extractors.slice(0, 2));
      } catch (e) {
        console.log('⚠️ Extractors response is not JSON:', responseText);
      }
    } else {
      console.log('❌ Extractors endpoint failed or returned empty');
    }
    
  } catch (error) {
    console.error('❌ Extractors network error:', error.message);
  }
};

// Test URL configurations endpoint
const testURLConfigsEndpoint = async () => {
  const baseUrl = 'http://localhost:4000';
  
  console.log('\n🧪 Testing URL Configurations Endpoint...');
  
  try {
    const response = await fetch(`${baseUrl}/api/url-configurations`);
    console.log('📥 URL configs response status:', response.status);
    
    const responseText = await response.text();
    console.log('📥 URL configs response:', responseText);
    
    if (response.ok && responseText) {
      try {
        const configs = JSON.parse(responseText);
        console.log('✅ URL configs loaded:', configs.length, 'items');
        console.log('📋 Sample configs:', configs.slice(0, 2));
      } catch (e) {
        console.log('⚠️ URL configs response is not JSON:', responseText);
      }
    } else {
      console.log('❌ URL configs endpoint failed or returned empty');
    }
    
  } catch (error) {
    console.error('❌ URL configs network error:', error.message);
  }
};

// Run all tests
const runAllTests = async () => {
  console.log('🚀 Starting URL Mapping API Tests\n');
  
  await testExtractorsEndpoint();
  await testURLConfigsEndpoint();
  await testURLMappingCreation();
  
  console.log('\n🏁 Tests completed!');
};

// Check if running in Node.js environment
if (typeof window === 'undefined') {
  // Node.js environment - fetch is built-in in Node.js 18+
  runAllTests();
} else {
  // Browser environment
  console.log('Run this in Node.js or browser console');
  window.testURLMapping = runAllTests;
}