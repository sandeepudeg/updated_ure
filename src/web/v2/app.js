// GramSetu - Main Application JavaScript

// Configuration
const CONFIG = {
    API_ENDPOINT: 'https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query',
    MAX_RETRIES: 3,
    RETRY_DELAY: 1000
};

// State management
const state = {
    userId: generateUserId(),
    conversationHistory: [],
    isLoading: false,
    selectedImage: null,
    userProfile: loadUserProfile() || {}
};

// DOM Elements
const elements = {
    userInput: document.getElementById('userInput'),
    sendButton: document.getElementById('sendButton'),
    chatContainer: document.getElementById('chatContainer'),
    imageInput: document.getElementById('imageInput'),
    uploadImageButton: document.getElementById('uploadImageButton'),
    selectedImageName: document.getElementById('selectedImageName')
};

// Initialize application
function init() {
    setupEventListeners();
    loadConversationHistory();
    displayWelcomeMessage();
    initSplashScreen();
}

// Initialize splash screen
function initSplashScreen() {
    const splash = document.getElementById('welcomeSplash');
    const onboarding = document.getElementById('onboardingOverlay');
    
    // Auto-hide splash after 5 seconds and show onboarding
    setTimeout(() => {
        if (splash) {
            splash.style.animation = 'fadeOut 0.5s ease-in-out forwards';
            setTimeout(() => {
                splash.remove();
                // Show onboarding if user hasn't completed it
                if (!state.userProfile.name) {
                    showOnboarding();
                }
            }, 500);
        }
    }, 5000);
    
    // Allow click to skip splash
    if (splash) {
        splash.addEventListener('click', () => {
            splash.style.animation = 'fadeOut 0.3s ease-in-out forwards';
            setTimeout(() => {
                splash.remove();
                if (!state.userProfile.name) {
                    showOnboarding();
                }
            }, 300);
        });
    }
}

// Show onboarding form
function showOnboarding() {
    const onboarding = document.getElementById('onboardingOverlay');
    if (onboarding) {
        onboarding.classList.remove('hidden');
    }
}

// Hide onboarding form
function hideOnboarding() {
    const onboarding = document.getElementById('onboardingOverlay');
    if (onboarding) {
        onboarding.classList.add('hidden');
    }
}

// Skip onboarding
function skipOnboarding() {
    hideOnboarding();
    displayWelcomeMessage();
}

// Handle onboarding form submission
function handleOnboardingSubmit(event) {
    event.preventDefault();
    
    const formData = {
        name: document.getElementById('userName').value.trim(),
        state: document.getElementById('userState').value,
        district: document.getElementById('userDistrict').value.trim(),
        language: document.getElementById('userLanguage').value,
        crops: document.getElementById('userCrops').value.trim(),
        farmSize: document.getElementById('userFarmSize').value,
        saveData: document.getElementById('saveData').checked,
        createdAt: Date.now()
    };
    
    // Validate required fields
    if (!formData.name || !formData.state || !formData.language) {
        alert('Please fill in all required fields');
        return;
    }
    
    // Save to state and localStorage
    state.userProfile = formData;
    if (formData.saveData) {
        localStorage.setItem('gramsetu_profile', JSON.stringify(formData));
    }
    
    // Update UI
    updateUserBadge(formData.name);
    updateLocationDisplay(formData.state, formData.district);
    
    // Hide onboarding
    hideOnboarding();
    
    // Display personalized welcome message
    displayPersonalizedWelcome(formData);
}

// Load user profile from localStorage
function loadUserProfile() {
    const stored = localStorage.getItem('gramsetu_profile');
    if (stored) {
        try {
            return JSON.parse(stored);
        } catch (e) {
            console.error('Error loading profile:', e);
            return null;
        }
    }
    return null;
}

// Update user badge in header
function updateUserBadge(name) {
    const badge = document.querySelector('.user-badge');
    if (badge && name) {
        badge.textContent = `👤 ${name}`;
    }
}

// Update location display
function updateLocationDisplay(state, district) {
    const locationCard = document.querySelector('.left-panel .info-card');
    if (locationCard) {
        locationCard.innerHTML = `
            <strong>Your Location</strong><br>
            ${district ? `District: ${district}<br>` : ''}
            State: ${state}<br>
            Country: India
        `;
    }
}

// Display personalized welcome message
function displayPersonalizedWelcome(profile) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';
    
    const greeting = getGreeting();
    const cropsText = profile.crops ? ` I see you grow ${profile.crops}.` : '';
    
    messageDiv.innerHTML = `
        <div class="chat-message assistant-message">
            <span class="agent-badge badge-supervisor">GramSetu</span><br>
            <strong>${greeting}, ${profile.name}! 🌾</strong><br><br>
            Welcome to GramSetu!${cropsText} I'm here to help you with:<br>
            • 🌱 Crop disease identification and treatment<br>
            • 💰 Real-time market prices for ${profile.state}<br>
            • 📋 Government schemes and eligibility<br>
            • 💧 Irrigation and water management tips<br>
            • 🌤️ Weather forecasts for your area<br>
            • 🏞️ Rural tourism opportunities<br><br>
            How can I assist you today?
        </div>
    `;
    
    elements.chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Get time-based greeting
function getGreeting() {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
}

// Setup event listeners
function setupEventListeners() {
    // Send button click
    elements.sendButton.addEventListener('click', handleSendMessage);

    // Enter key press
    elements.userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    });

    // Image upload
    elements.uploadImageButton.addEventListener('click', () => {
        elements.imageInput.click();
    });

    elements.imageInput.addEventListener('change', handleImageSelect);

    // Quick action buttons
    document.querySelectorAll('.quick-action').forEach(button => {
        button.addEventListener('click', (e) => {
            const query = e.currentTarget.dataset.query;
            suggestQuery(query);
        });
    });

    // Agent cards
    document.querySelectorAll('.agent-card').forEach(card => {
        card.addEventListener('click', (e) => {
            const query = e.currentTarget.dataset.query;
            suggestQuery(query);
        });
    });

    // Onboarding form
    const onboardingForm = document.getElementById('onboardingForm');
    if (onboardingForm) {
        onboardingForm.addEventListener('submit', handleOnboardingSubmit);
    }
}

// Generate unique user ID
function generateUserId() {
    const stored = localStorage.getItem('gramsetu_user_id');
    if (stored) return stored;
    
    const newId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('gramsetu_user_id', newId);
    return newId;
}

// Suggest query (fill input field)
function suggestQuery(query) {
    elements.userInput.value = query;
    elements.userInput.focus();
}

// Handle image selection
function handleImageSelect(event) {
    const file = event.target.files[0];
    if (file) {
        state.selectedImage = file;
        elements.selectedImageName.textContent = file.name;
    } else {
        state.selectedImage = null;
        elements.selectedImageName.textContent = 'No image selected';
    }
}

// Handle send message
async function handleSendMessage() {
    const message = elements.userInput.value.trim();
    
    if (!message && !state.selectedImage) {
        return;
    }

    if (state.isLoading) {
        return;
    }

    // Display user message
    displayUserMessage(message, state.selectedImage);

    // Clear input
    elements.userInput.value = '';
    state.selectedImage = null;
    elements.selectedImageName.textContent = 'No image selected';
    elements.imageInput.value = '';

    // Set loading state
    setLoadingState(true);

    try {
        // Send to API
        const response = await sendToAPI(message, state.selectedImage);
        
        // Display assistant response
        displayAssistantMessage(response);
        
        // Save to history
        saveToHistory(message, response);
    } catch (error) {
        console.error('Error sending message:', error);
        displayErrorMessage('Sorry, I encountered an error. Please try again.');
    } finally {
        setLoadingState(false);
    }
}

// Send message to API
async function sendToAPI(message, image = null) {
    const payload = {
        user_id: state.userId,
        query: message,
        user_profile: state.userProfile  // Include user profile for personalization
    };

    // If image is provided, convert to base64
    if (image) {
        const base64Image = await fileToBase64(image);
        payload.image = base64Image;
    }

    const response = await fetch(CONFIG.API_ENDPOINT, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    });

    if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();
    return data;
}

// Convert file to base64
function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result.split(',')[1]);
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

// Display user message
function displayUserMessage(text, image = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';
    
    let imageHTML = '';
    if (image) {
        const imageUrl = URL.createObjectURL(image);
        imageHTML = `<img src="${imageUrl}" alt="Uploaded image" style="max-width: 200px; border-radius: 0.5rem; margin-top: 0.5rem;">`;
    }
    
    messageDiv.innerHTML = `
        <div class="chat-message user-message">
            <strong>You:</strong><br>
            ${escapeHtml(text)}
            ${imageHTML}
        </div>
    `;
    
    elements.chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Display assistant message
function displayAssistantMessage(response) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';
    
    // Extract agent and response text
    const agentName = response.agent || 'Assistant';
    const responseText = response.response || response.message || 'No response';
    
    // Determine badge class
    const badgeClass = getBadgeClass(agentName);
    
    messageDiv.innerHTML = `
        <div class="chat-message assistant-message">
            <span class="agent-badge ${badgeClass}">${agentName}</span><br>
            ${formatResponse(responseText)}
        </div>
    `;
    
    elements.chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Display error message
function displayErrorMessage(errorText) {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';
    
    messageDiv.innerHTML = `
        <div class="error">
            <strong>Error:</strong> ${escapeHtml(errorText)}
        </div>
    `;
    
    elements.chatContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Display welcome message
function displayWelcomeMessage() {
    if (elements.chatContainer.children.length === 0) {
        const welcomeDiv = document.createElement('div');
        welcomeDiv.className = 'message';
        welcomeDiv.innerHTML = `
            <div class="chat-message assistant-message">
                <span class="agent-badge badge-supervisor">GramSetu</span><br>
                <strong>Welcome to GramSetu!</strong><br><br>
                I'm your AI-powered rural assistant. I can help you with:<br>
                • 🌱 Crop disease identification<br>
                • 💰 Market prices and trends<br>
                • 📋 Government schemes<br>
                • 💧 Irrigation tips<br>
                • 🌤️ Weather forecasts<br>
                • 🏞️ Rural tourism opportunities<br><br>
                Click on any agent card or quick action to get started!
            </div>
        `;
        elements.chatContainer.appendChild(welcomeDiv);
    }
}

// Get badge class based on agent name
function getBadgeClass(agentName) {
    const name = agentName.toLowerCase();
    if (name.includes('supervisor')) return 'badge-supervisor';
    if (name.includes('agri') || name.includes('crop')) return 'badge-agri-expert';
    if (name.includes('policy') || name.includes('scheme')) return 'badge-policy';
    if (name.includes('resource')) return 'badge-resource';
    return 'badge-supervisor';
}

// Format response text (convert markdown-like syntax to HTML)
function formatResponse(text) {
    let formatted = escapeHtml(text);
    
    // Convert line breaks
    formatted = formatted.replace(/\n/g, '<br>');
    
    // Convert bold **text**
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Convert bullet points
    formatted = formatted.replace(/^• /gm, '&bull; ');
    
    return formatted;
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Set loading state
function setLoadingState(isLoading) {
    state.isLoading = isLoading;
    elements.sendButton.disabled = isLoading;
    elements.userInput.disabled = isLoading;
    
    if (isLoading) {
        // Show loading indicator
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'loading';
        loadingDiv.id = 'loadingIndicator';
        loadingDiv.innerHTML = '<span></span><span></span><span></span>';
        elements.chatContainer.appendChild(loadingDiv);
        scrollToBottom();
    } else {
        // Remove loading indicator
        const loadingDiv = document.getElementById('loadingIndicator');
        if (loadingDiv) {
            loadingDiv.remove();
        }
    }
}

// Scroll chat to bottom
function scrollToBottom() {
    elements.chatContainer.scrollTop = elements.chatContainer.scrollHeight;
}

// Save conversation to history
function saveToHistory(userMessage, assistantResponse) {
    const entry = {
        timestamp: Date.now(),
        user: userMessage,
        assistant: assistantResponse
    };
    
    state.conversationHistory.push(entry);
    
    // Save to localStorage (keep last 50 messages)
    const history = state.conversationHistory.slice(-50);
    localStorage.setItem('gramsetu_history', JSON.stringify(history));
}

// Load conversation history
function loadConversationHistory() {
    const stored = localStorage.getItem('gramsetu_history');
    if (stored) {
        try {
            state.conversationHistory = JSON.parse(stored);
        } catch (e) {
            console.error('Error loading history:', e);
            state.conversationHistory = [];
        }
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// Export for debugging (optional)
window.GramSetu = {
    state,
    config: CONFIG,
    sendMessage: handleSendMessage,
    clearHistory: () => {
        state.conversationHistory = [];
        localStorage.removeItem('gramsetu_history');
        elements.chatContainer.innerHTML = '';
        displayWelcomeMessage();
    }
};
