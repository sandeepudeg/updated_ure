// GramSetu AWS-Native Web UI - JavaScript

// Global state
let userId = generateUserId();
let currentLanguage = 'en';
let uploadedImage = null;
let conversationHistory = [];
let userProfile = null;

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Check if API URL is configured
    if (!window.API_GATEWAY_URL || window.API_GATEWAY_URL === 'YOUR_API_GATEWAY_URL_HERE') {
        showConfigModal();
        return;
    }
    
    // Load user profile from localStorage
    loadUserProfile();
    
    // Detect user location
    detectLocation();
    
    // Check and clear old chat history (older than 3 hours)
    clearOldChatHistory();
    
    // Setup event listeners
    setupEventListeners();
    
    // Load conversation history
    loadConversationHistory();
}

function setupEventListeners() {
    // Language selector
    document.getElementById('languageSelector').addEventListener('change', function(e) {
        currentLanguage = e.target.value;
        localStorage.setItem('language', currentLanguage);
    });
    
    // Quick action buttons
    document.querySelectorAll('.quick-action-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const query = this.getAttribute('data-query');
            document.getElementById('chatInput').value = query;
            sendMessage();
        });
    });
    
    // Profile form
    document.getElementById('profileForm').addEventListener('submit', function(e) {
        e.preventDefault();
        saveUserProfile();
    });
    
    // Chat input - Enter to send
    document.getElementById('chatInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}

// User ID generation
function generateUserId() {
    let userId = localStorage.getItem('userId');
    if (!userId) {
        userId = 'farmer_' + Date.now() + '_' + Math.random().toString(36).substring(2, 11);
        localStorage.setItem('userId', userId);
    }
    return userId;
}

// Location detection with IP-based cache clearing
async function detectLocation() {
    try {
        const response = await fetch('https://ipapi.co/json/');
        const data = await response.json();
        
        // Get current IP
        const currentIP = data.ip;
        
        // Check if IP has changed
        const savedIP = localStorage.getItem('lastKnownIP');
        
        if (savedIP && savedIP !== currentIP) {
            // New IP detected - clear old chat history
            console.log('New IP detected. Clearing old chat history...');
            console.log(`Previous IP: ${savedIP}, Current IP: ${currentIP}`);
            
            // Clear conversation history
            localStorage.removeItem('conversationHistory');
            conversationHistory = [];
            
            // Clear chat messages from UI
            const chatMessages = document.getElementById('chatMessages');
            chatMessages.innerHTML = `
                <div class="welcome-screen" id="welcomeScreen">
                    <div class="welcome-icon">🌾</div>
                    <h3>Welcome to GramSetu!</h3>
                    <p>Your AI-powered assistant for farming, market prices, government schemes, and more. Ask me anything or upload a crop image for disease identification.</p>

                    <div class="feature-grid">
                        <div class="feature-card">
                            <div class="feature-icon">🌱</div>
                            <h4>Crop Diseases</h4>
                            <p>Upload photos for instant disease identification</p>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">💰</div>
                            <h4>Market Prices</h4>
                            <p>Real-time prices in Indian Rupees</p>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">📋</div>
                            <h4>Govt Schemes</h4>
                            <p>PM-Kisan, PMFBY eligibility</p>
                        </div>
                        <div class="feature-card">
                            <div class="feature-icon">🌤️</div>
                            <h4>Weather</h4>
                            <p>Location-based forecasts</p>
                        </div>
                    </div>
                </div>
            `;
            
            // Show notification
            showNotification('🔄 New device detected. Chat history cleared for privacy.', 'info');
        }
        
        // Save current IP
        localStorage.setItem('lastKnownIP', currentIP);
        
        // Update location display
        document.getElementById('userDistrict').textContent = data.city || 'Unknown';
        document.getElementById('userState').textContent = data.region || 'Unknown';
        document.getElementById('userCountry').textContent = data.country_name || 'India';
        
        // Save location
        localStorage.setItem('location', JSON.stringify({
            city: data.city,
            region: data.region,
            country: data.country_name,
            ip: currentIP
        }));
    } catch (error) {
        console.error('Location detection failed:', error);
        document.getElementById('userDistrict').textContent = 'Nashik';
        document.getElementById('userState').textContent = 'Maharashtra';
    }
}

// Clear chat history older than 3 hours
function clearOldChatHistory() {
    const lastActivityTime = localStorage.getItem('lastActivityTime');
    const currentTime = new Date().getTime();
    const threeHoursInMs = 3 * 60 * 60 * 1000; // 3 hours in milliseconds
    
    if (lastActivityTime) {
        const timeSinceLastActivity = currentTime - parseInt(lastActivityTime);
        
        if (timeSinceLastActivity > threeHoursInMs) {
            console.log('Chat history older than 3 hours. Clearing...');
            
            // Clear conversation history
            localStorage.removeItem('conversationHistory');
            conversationHistory = [];
            
            // Show notification
            showNotification('🕐 Chat history cleared due to inactivity (3+ hours).', 'info');
        }
    }
    
    // Update last activity time
    localStorage.setItem('lastActivityTime', currentTime.toString());
}

// User profile management
function loadUserProfile() {
    const savedProfile = localStorage.getItem('userProfile');
    if (savedProfile) {
        userProfile = JSON.parse(savedProfile);
        displayUserProfile();
    }
}

function saveUserProfile() {
    const profile = {
        name: document.getElementById('inputName').value,
        village: document.getElementById('inputVillage').value,
        district: document.getElementById('inputDistrict').value,
        phone: document.getElementById('inputPhone').value,
        crops: document.getElementById('inputCrops').value,
        landSize: document.getElementById('inputLandSize').value
    };
    
    userProfile = profile;
    localStorage.setItem('userProfile', JSON.stringify(profile));
    displayUserProfile();
}

function displayUserProfile() {
    if (!userProfile) return;
    
    document.getElementById('userName').textContent = userProfile.name || 'Guest User';
    document.getElementById('profileName').textContent = userProfile.name;
    document.getElementById('profileVillage').textContent = userProfile.village;
    document.getElementById('profileCrops').textContent = userProfile.crops;
    
    document.getElementById('profileForm').style.display = 'none';
    document.getElementById('profileDisplay').style.display = 'block';
}

function showProfileForm() {
    document.getElementById('profileForm').style.display = 'flex';
    document.getElementById('profileDisplay').style.display = 'none';
    
    // Pre-fill form
    if (userProfile) {
        document.getElementById('inputName').value = userProfile.name || '';
        document.getElementById('inputVillage').value = userProfile.village || '';
        document.getElementById('inputDistrict').value = userProfile.district || 'Nashik';
        document.getElementById('inputPhone').value = userProfile.phone || '';
        document.getElementById('inputCrops').value = userProfile.crops || '';
        document.getElementById('inputLandSize').value = userProfile.landSize || '';
    }
}

// Image upload handling
function handleImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = function(e) {
        uploadedImage = e.target.result.split(',')[1]; // Get base64 data
        
        // Show preview
        document.getElementById('previewImage').src = e.target.result;
        document.getElementById('imageName').textContent = file.name;
        document.getElementById('imagePreview').style.display = 'flex';
    };
    reader.readAsDataURL(file);
}

function removeImage() {
    uploadedImage = null;
    document.getElementById('imagePreview').style.display = 'none';
    document.getElementById('imageInput').value = '';
}

// Message sending
async function sendMessage() {
    const input = document.getElementById('chatInput');
    const query = input.value.trim();
    
    if (!query && !uploadedImage) return;
    
    // Hide welcome screen
    const welcomeScreen = document.getElementById('welcomeScreen');
    if (welcomeScreen) {
        welcomeScreen.style.display = 'none';
    }
    
    // Add user message to chat
    addMessageToChat('user', query);
    
    // Clear input
    input.value = '';
    
    // Show loading
    showLoading();
    
    try {
        // Prepare request
        const location = JSON.parse(localStorage.getItem('location') || '{}');
        const requestBody = {
            user_id: userId,
            query: query,
            language: currentLanguage,
            location: `${location.city || 'Unknown'}, ${location.region || 'Unknown'}, ${location.country || 'India'}`
        };
        
        // Add image if uploaded
        if (uploadedImage) {
            requestBody.image = uploadedImage;
        }
        
        // Send to API Gateway
        const response = await fetch(window.API_GATEWAY_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Add assistant response to chat (with PDF links if available)
        addMessageToChat('assistant', data.response, data.agent_used, data.metadata);
        
        // Save to conversation history
        conversationHistory.push({
            query: query,
            response: data.response,
            agent: data.agent_used,
            metadata: data.metadata,
            timestamp: new Date().toISOString()
        });
        saveConversationHistory();
        
        // Clear uploaded image
        if (uploadedImage) {
            removeImage();
        }
        
    } catch (error) {
        console.error('Error sending message:', error);
        addMessageToChat('assistant', 'Sorry, I encountered an error processing your request. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

// Chat UI functions
function addMessageToChat(role, content, agent = null, metadata = null) {
    const chatMessages = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${role}`;
    
    if (role === 'user') {
        messageDiv.innerHTML = `
            <div class="message-content">
                <strong>You:</strong><br>${escapeHtml(content)}
            </div>
        `;
    } else {
        const agentBadge = getAgentBadge(agent);
        let messageContent = formatResponse(content);
        
        // Add PDF download links if available
        if (metadata && metadata.pdf_links && metadata.pdf_links.length > 0) {
            messageContent += '<div class="pdf-links-container">';
            messageContent += '<div class="pdf-links-header">📄 Available Documents:</div>';
            metadata.pdf_links.forEach(pdf => {
                messageContent += `
                    <a href="${pdf.url}" target="_blank" class="pdf-download-link" download>
                        <span class="pdf-icon">📥</span>
                        <span class="pdf-name">${pdf.scheme_name}</span>
                        <span class="pdf-action">Download PDF</span>
                    </a>
                `;
            });
            messageContent += '</div>';
        }
        
        // Add website links if available
        if (metadata && metadata.website_links && metadata.website_links.length > 0) {
            messageContent += '<div class="website-links-container">';
            messageContent += '<div class="website-links-header">🌐 Official Resources:</div>';
            metadata.website_links.forEach(link => {
                messageContent += `
                    <a href="${link.url}" target="_blank" class="website-link" rel="noopener noreferrer">
                        <span class="website-icon">🔗</span>
                        <span class="website-name">${link.scheme_name} - ${link.link_type}</span>
                        <span class="website-action">Visit Website</span>
                    </a>
                `;
            });
            messageContent += '</div>';
        }
        
        messageDiv.innerHTML = `
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                ${agentBadge}
                ${messageContent}
            </div>
        `;
    }
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function getAgentBadge(agent) {
    const badges = {
        'vision-model': '<span class="agent-badge badge-vision">🔍 Vision AI</span>',
        'agri-expert': '<span class="agent-badge badge-agri">🌱 Agri Expert</span>',
        'policy-navigator': '<span class="agent-badge badge-policy">📋 Policy Navigator</span>',
        'resource-optimizer': '<span class="agent-badge badge-resource">⚡ Resource Optimizer</span>',
        'rural-tourism': '<span class="agent-badge badge-tourism">🏞️ Rural Tourism</span>',
        'supervisor': '<span class="agent-badge badge-supervisor">🎯 Supervisor</span>',
        'error': '<span class="agent-badge badge-supervisor">❌ Error</span>'
    };
    return badges[agent] || badges['supervisor'];
}

function formatResponse(text) {
    // Convert markdown-style formatting to HTML
    text = escapeHtml(text);
    
    // Bold text
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Line breaks
    text = text.replace(/\n/g, '<br>');
    
    // Lists
    text = text.replace(/^- (.+)$/gm, '<li>$1</li>');
    if (text.includes('<li>')) {
        text = text.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
    }
    
    return text;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Loading overlay
function showLoading() {
    document.getElementById('loadingOverlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

// Conversation history
function loadConversationHistory() {
    const saved = localStorage.getItem('conversationHistory');
    if (saved) {
        conversationHistory = JSON.parse(saved);
        
        // Display last 5 messages
        conversationHistory.slice(-5).forEach(msg => {
            addMessageToChat('user', msg.query);
            addMessageToChat('assistant', msg.response, msg.agent, msg.metadata);
        });
    }
}

function saveConversationHistory() {
    // Keep only last 50 messages
    if (conversationHistory.length > 50) {
        conversationHistory = conversationHistory.slice(-50);
    }
    localStorage.setItem('conversationHistory', JSON.stringify(conversationHistory));
}

// Configuration modal
function showConfigModal() {
    document.getElementById('configModal').style.display = 'flex';
}

function saveApiUrl() {
    const apiUrl = document.getElementById('apiUrlInput').value.trim();
    if (!apiUrl) {
        alert('Please enter a valid API Gateway URL');
        return;
    }
    
    // Save to config.js (user needs to update manually)
    alert('Please update the API_GATEWAY_URL in config.js file with:\n\n' + apiUrl);
    
    // For now, set it in window object
    window.API_GATEWAY_URL = apiUrl;
    document.getElementById('configModal').style.display = 'none';
    
    // Initialize app
    initializeApp();
}

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

// Notification system
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <span class="notification-icon">${type === 'info' ? 'ℹ️' : type === 'success' ? '✅' : '⚠️'}</span>
        <span class="notification-message">${message}</span>
    `;
    
    // Add to body
    document.body.appendChild(notification);
    
    // Show notification
    setTimeout(() => {
        notification.classList.add('notification-show');
    }, 100);
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        notification.classList.remove('notification-show');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 5000);
}

// Export functions for HTML onclick handlers
window.sendMessage = sendMessage;
window.handleImageUpload = handleImageUpload;
window.removeImage = removeImage;
window.showProfileForm = showProfileForm;
window.saveApiUrl = saveApiUrl;
