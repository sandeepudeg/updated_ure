// GramSetu Configuration
// Update this file with your API Gateway URL after deployment

// API Gateway URL (configured for production)
window.API_GATEWAY_URL = 'https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query';

// AWS Region (optional, for future use)
window.AWS_REGION = 'us-east-1';

// Feature flags
window.FEATURES = {
    imageUpload: true,
    multiLanguage: true,
    locationDetection: true,
    conversationHistory: true
};

// Debug mode (set to false in production)
window.DEBUG_MODE = true;

if (window.DEBUG_MODE) {
    console.log('GramSetu Configuration Loaded');
    console.log('API Gateway URL:', window.API_GATEWAY_URL);
}
