/**
 * CORS Connection Test Script for N8N
 *
 * This script tests the N8N connection and CORS configuration
 * from the perspective of the Liquid Audio Agent.
 *
 * Usage: node test-cors-connection.js [n8n-url] [api-key]
 */

const https = require('https');
const http = require('http');
const { URL } = require('url');

// Configuration - can be overridden by command line arguments
const N8N_URL = process.argv[2] || 'http://localhost:5678';
const N8N_API_KEY = process.argv[3] || null;

/**
 * Make HTTP request to N8N API
 */
async function makeRequest(url, options = {}) {
    return new Promise((resolve, reject) => {
        const urlObj = new URL(url);
        const isHttps = urlObj.protocol === 'https:';
        const client = isHttps ? https : http;

        const requestOptions = {
            hostname: urlObj.hostname,
            port: urlObj.port || (isHttps ? 443 : 80),
            path: urlObj.pathname + urlObj.search,
            method: options.method || 'GET',
            headers: {
                'Content-Type': 'application/json',
                'User-Agent': 'Liquid-Audio-Agent/1.0 CORS-Test',
                ...options.headers
            }
        };

        const req = client.request(requestOptions, (res) => {
            let data = '';

            res.on('data', (chunk) => {
                data += chunk;
            });

            res.on('end', () => {
                resolve({
                    statusCode: res.statusCode,
                    statusMessage: res.statusMessage,
                    headers: res.headers,
                    data: data ? JSON.parse(data) : null
                });
            });
        });

        req.on('error', (error) => {
            reject(error);
        });

        if (options.body) {
            req.write(options.body);
        }

        req.end();
    });
}

/**
 * Test basic N8N connectivity
 */
async function testBasicConnectivity() {
    console.log('🔍 Testing basic N8N connectivity...');
    try {
        const response = await makeRequest(`${N8N_URL}/healthz`);

        if (response.statusCode === 200) {
            console.log('✅ Basic connectivity: SUCCESS');
            console.log(`   Status: ${response.statusCode} ${response.statusMessage}`);
            return true;
        } else {
            console.log('⚠️  Basic connectivity: UNEXPECTED RESPONSE');
            console.log(`   Status: ${response.statusCode} ${response.statusMessage}`);
            return false;
        }
    } catch (error) {
        console.log('❌ Basic connectivity: FAILED');
        console.log(`   Error: ${error.message}`);

        if (error.code === 'ECONNREFUSED') {
            console.log('   💡 N8N is not running or not accessible at this URL');
        } else if (error.code === 'ENOTFOUND') {
            console.log('   💡 Hostname could not be resolved');
        }
        return false;
    }
}

/**
 * Test N8N API access
 */
async function testAPIAccess() {
    if (!N8N_API_KEY) {
        console.log('⚠️  No API key provided - skipping API access test');
        console.log('   Usage: node test-cors-connection.js <n8n-url> <api-key>');
        return false;
    }

    console.log('🔍 Testing N8N API access...');
    try {
        const response = await makeRequest(`${N8N_URL}/api/v1/workflows`, {
            headers: {
                'X-N8N-API-KEY': N8N_API_KEY
            }
        });

        if (response.statusCode === 200) {
            console.log('✅ API access: SUCCESS');
            console.log(`   Status: ${response.statusCode} ${response.statusMessage}`);
            console.log(`   Workflows found: ${response.data?.data?.length || 0}`);

            if (response.data?.data?.length > 0) {
                console.log('   Available workflows:');
                response.data.data.forEach((wf, index) => {
                    console.log(`     ${index + 1}. ${wf.name} (ID: ${wf.id})`);
                });
            }
            return true;
        } else if (response.statusCode === 401) {
            console.log('❌ API access: AUTHENTICATION FAILED');
            console.log('   💡 Invalid API key. Check your N8N API key in Settings > API');
            return false;
        } else if (response.statusCode === 404) {
            console.log('❌ API access: NOT FOUND');
            console.log('   💡 N8N API endpoint not found. Is this a valid N8N instance?');
            return false;
        } else {
            console.log('⚠️  API access: UNEXPECTED RESPONSE');
            console.log(`   Status: ${response.statusCode} ${response.statusMessage}`);
            console.log('   Response:', response.data);
            return false;
        }
    } catch (error) {
        console.log('❌ API access: FAILED');
        console.log(`   Error: ${error.message}`);

        if (error.message.includes('CORS') || error.message.includes('cross-origin')) {
            console.log('   🔒 CORS Issue detected!');
            console.log('   💡 Run the fix-cors script or restart N8N with CORS configuration');
        }
        return false;
    }
}

/**
 * Test CORS headers
 */
async function testCORSHeaders() {
    console.log('🔍 Testing CORS headers...');
    try {
        const response = await makeRequest(`${N8N_URL}/api/v1/workflows`, {
            method: 'OPTIONS',
            headers: {
                'Origin': 'http://localhost:3000',
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'X-N8N-API-KEY'
            }
        });

        const corsHeaders = {
            'Access-Control-Allow-Origin': response.headers['access-control-allow-origin'],
            'Access-Control-Allow-Methods': response.headers['access-control-allow-methods'],
            'Access-Control-Allow-Headers': response.headers['access-control-allow-headers'],
            'Access-Control-Allow-Credentials': response.headers['access-control-allow-credentials']
        };

        console.log('📋 CORS Headers found:');
        Object.entries(corsHeaders).forEach(([key, value]) => {
            if (value) {
                console.log(`   ✅ ${key}: ${value}`);
            } else {
                console.log(`   ❌ ${key}: Not set`);
            }
        });

        // Check essential CORS headers
        const hasCorrectOrigin = corsHeaders['Access-Control-Allow-Origin'] === '*' ||
                                corsHeaders['Access-Control-Allow-Origin'] === 'http://localhost:3000';
        const hasMethods = corsHeaders['Access-Control-Allow-Methods']?.includes('GET');
        const hasHeaders = corsHeaders['Access-Control-Allow-Headers']?.includes('X-N8N-API-KEY');

        if (hasCorrectOrigin && hasMethods && hasHeaders) {
            console.log('✅ CORS configuration: LOOKS GOOD');
            return true;
        } else {
            console.log('⚠️  CORS configuration: INCOMPLETE');
            console.log('   💡 Some required CORS headers are missing');
            console.log('   💡 Restart N8N with: N8N_CORS_ALLOW_ORIGIN=* npx n8n start');
            return false;
        }
    } catch (error) {
        console.log('❌ CORS headers test: FAILED');
        console.log(`   Error: ${error.message}`);
        return false;
    }
}

/**
 * Main test execution
 */
async function runTests() {
    console.log('🚀 N8N CORS Connection Test');
    console.log(`   Target URL: ${N8N_URL}`);
    console.log(`   API Key: ${N8N_API_KEY ? 'Provided' : 'Not provided'}`);
    console.log('');

    const results = {
        connectivity: await testBasicConnectivity(),
        cors: await testCORSHeaders(),
        api: await testAPIAccess()
    };

    console.log('');
    console.log('📊 Test Results Summary:');
    console.log(`   Basic Connectivity: ${results.connectivity ? '✅ PASS' : '❌ FAIL'}`);
    console.log(`   CORS Configuration: ${results.cors ? '✅ PASS' : '❌ FAIL'}`);
    console.log(`   API Access: ${results.api ? '✅ PASS' : '❌ FAIL'}`);

    const allPassed = Object.values(results).every(result => result);

    console.log('');
    if (allPassed) {
        console.log('🎉 All tests passed! Your N8N CORS configuration is working correctly.');
    } else {
        console.log('⚠️  Some tests failed. See details above for troubleshooting steps.');
        console.log('');
        console.log('🔧 Quick fixes:');
        console.log('   1. Run: fix-cors.bat (Windows) or ./fix-cors.sh (Linux/Mac)');
        console.log('   2. Or restart N8N with: N8N_CORS_ALLOW_ORIGIN=* npx n8n start');
        console.log('   3. Make sure N8N is running on http://localhost:5678');
        console.log('   4. Check that your API key is valid');
    }

    process.exit(allPassed ? 0 : 1);
}

// Run the tests
if (require.main === module) {
    runTests().catch(error => {
        console.error('❌ Test execution failed:', error);
        process.exit(1);
    });
}

module.exports = { runTests, testBasicConnectivity, testAPIAccess, testCORSHeaders };