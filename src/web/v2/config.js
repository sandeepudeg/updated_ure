// GramSetu Configuration
const CONFIG = {
    // API Configuration
    API_ENDPOINT: 'https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query',
    
    // AWS Configuration
    AWS_REGION: 'us-east-1',
    
    // Application Settings
    APP_NAME: 'GramSetu',
    APP_TAGLINE: 'AI-Powered Rural Assistant',
    
    // Default Location
    DEFAULT_LOCATION: {
        district: 'Nashik',
        state: 'Maharashtra',
        country: 'India'
    },
    
    // Language Options
    LANGUAGES: [
        { code: 'en', name: 'English', icon: '🌐' },
        { code: 'hi', name: 'हिंदी', icon: '🇮🇳' },
        { code: 'mr', name: 'मराठी', icon: '🇮🇳' },
        { code: 'te', name: 'తెలుగు', icon: '🇮🇳' },
        { code: 'ta', name: 'தமிழ்', icon: '🇮🇳' },
        { code: 'kn', name: 'ಕನ್ನಡ', icon: '🇮🇳' }
    ],
    
    // District Options
    DISTRICTS: [
        'Nashik',
        'Pune',
        'Ahmednagar',
        'Mumbai',
        'Nagpur',
        'Aurangabad',
        'Solapur',
        'Other'
    ],
    
    // State Options
    STATES: [
        'Maharashtra',
        'Karnataka',
        'Punjab',
        'Uttar Pradesh',
        'Gujarat',
        'Rajasthan',
        'Madhya Pradesh',
        'Tamil Nadu',
        'Telangana',
        'Andhra Pradesh',
        'Other'
    ],
    
    // Agent Configuration
    AGENTS: [
        {
            id: 'krishak-mitra',
            name: 'Krishak Mitra',
            role: 'Crop Specialist',
            icon: 'fa-seedling',
            description: 'Expert advice on crop selection, planting techniques, and cultivation practices.',
            color: '#43A047'
        },
        {
            id: 'rog-nivaarak',
            name: 'Rog Nivaarak',
            role: 'Disease Expert',
            icon: 'fa-bug',
            description: 'Identifies plant diseases and pests from images, recommends solutions.',
            color: '#E53935'
        },
        {
            id: 'bazaar-darshi',
            name: 'Bazaar Darshi',
            role: 'Market Analyst',
            icon: 'fa-chart-line',
            description: 'Real-time market prices, demand forecasts, and buyer connections.',
            color: '#FB8C00'
        },
        {
            id: 'sarkar-sahayak',
            name: 'Sarkar Sahayak',
            role: 'Scheme Advisor',
            icon: 'fa-file-invoice-dollar',
            description: 'Guides through government schemes, subsidies, and loan programs.',
            color: '#1E88E5'
        },
        {
            id: 'mausam-gyaata',
            name: 'Mausam Gyaata',
            role: 'Weather Expert',
            icon: 'fa-cloud-sun-rain',
            description: 'Hyperlocal weather forecasts, irrigation advice, and climate alerts.',
            color: '#00ACC1'
        },
        {
            id: 'krishi-bodh',
            name: 'Krishi Bodh',
            role: 'Knowledge Guide',
            icon: 'fa-book-open',
            description: 'Educational resources, new farming techniques, and expert connections.',
            color: '#8E24AA'
        }
    ],
    
    // Feature Flags
    FEATURES: {
        imageUpload: true,
        voiceInput: false,
        offlineMode: false,
        notifications: true,
        analytics: true
    },
    
    // UI Settings
    UI: {
        splashScreenDuration: 5000, // 5 seconds
        messageDelay: 1000, // 1 second
        maxFileSize: 5 * 1024 * 1024, // 5MB
        allowedImageTypes: ['image/jpeg', 'image/png', 'image/jpg', 'image/webp']
    },
    
    // Storage Keys
    STORAGE_KEYS: {
        userProfile: 'gramsetu_profile',
        chatHistory: 'gramsetu_chat_history',
        preferences: 'gramsetu_preferences'
    }
};

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}
