#!/usr/bin/env python3
"""
GramSetu Enterprise UI - Streamlit Implementation
Enterprise-grade interface with enhanced features
"""

import streamlit as st
import sys
import os
from pathlib import Path
import base64
from datetime import datetime
import json
import uuid
import requests
import time
import logging
import boto3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Streamlit secrets -> AWS credentials
try:
    if "aws" in st.secrets:
        aws_secrets = st.secrets["aws"]
        os.environ.setdefault("AWS_ACCESS_KEY_ID", aws_secrets.get("AWS_ACCESS_KEY_ID", ""))
        os.environ.setdefault("AWS_SECRET_ACCESS_KEY", aws_secrets.get("AWS_SECRET_ACCESS_KEY", ""))
        if aws_secrets.get("AWS_SESSION_TOKEN"):
            os.environ.setdefault("AWS_SESSION_TOKEN", aws_secrets["AWS_SESSION_TOKEN"])
        os.environ.setdefault("AWS_DEFAULT_REGION", aws_secrets.get("AWS_DEFAULT_REGION", "us-east-1"))
        boto3.setup_default_session(
            aws_access_key_id=aws_secrets.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=aws_secrets.get("AWS_SECRET_ACCESS_KEY"),
            aws_session_token=aws_secrets.get("AWS_SESSION_TOKEN"),
            region_name=aws_secrets.get("AWS_DEFAULT_REGION", "us-east-1"),
        )
except:
    pass

# Configuration
USE_API_MODE = os.getenv('USE_API_MODE', 'false').lower() == 'true'
API_ENDPOINT = os.getenv('API_ENDPOINT', 'https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query')

# Page configuration
st.set_page_config(
    page_title="GramSetu - Enterprise AI Assistant",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enterprise CSS with gradient backgrounds and modern design
st.markdown("""
<style>
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container */
    .main {
        padding: 0 !important;
        background: linear-gradient(135deg, #E8F5E9 0%, #F1F8E9 100%);
    }
    
    /* Custom header */
    .custom-header {
        background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%);
        color: white;
        padding: 1.5rem 2rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        margin: -1rem -1rem 2rem -1rem;
    }
    
    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 1400px;
        margin: 0 auto;
    }
    
    .logo-section {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .logo-icon {
        font-size: 2.5rem;
    }
    
    .logo-text h1 {
        font-size: 1.8rem;
        margin: 0;
        font-weight: 700;
    }
    
    .logo-text p {
        font-size: 0.9rem;
        margin: 0;
        opacity: 0.9;
    }

    
    /* Chat messages */
    .chat-message {
        padding: 1.2rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        animation: fadeIn 0.3s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .user-message {
        background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
        color: white;
        margin-left: 20%;
        border-radius: 18px 18px 4px 18px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .assistant-message {
        background: white;
        border: 1px solid #E0E0E0;
        border-left: 4px solid #4CAF50;
        margin-right: 20%;
        border-radius: 18px 18px 18px 4px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .agent-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .badge-vision { background: #E1BEE7; color: #6A1B9A; }
    .badge-agri { background: #C8E6C9; color: #2E7D32; }
    .badge-policy { background: #BBDEFB; color: #1565C0; }
    .badge-resource { background: #FFE0B2; color: #E65100; }
    .badge-supervisor { background: #CE93D8; color: #6A1B9A; }
    
    /* Info cards */
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .info-card-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2E7D32;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .location-card {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        border-left: 4px solid #2196F3;
    }
    
    .weather-card {
        background: linear-gradient(135deg, #E1F5FE 0%, #B3E5FC 100%);
        text-align: center;
    }
    
    .weather-icon {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    
    .weather-temp {
        font-size: 2rem;
        font-weight: 700;
        color: #2196F3;
    }
    
    .market-card {
        background: linear-gradient(135deg, #F3E5F5 0%, #E1BEE7 100%);
    }
    
    .price-item {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid rgba(0,0,0,0.1);
    }
    
    .price-value {
        font-weight: 700;
        color: #4CAF50;
    }
    
    /* Quick action buttons */
    .quick-action-btn {
        width: 100%;
        padding: 0.8rem;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        font-size: 0.9rem;
        transition: transform 0.2s;
    }
    
    .quick-action-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    /* Welcome screen */
    .welcome-screen {
        text-align: center;
        padding: 3rem 2rem;
    }
    
    .welcome-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    
    /* Streamlit specific overrides */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    .stTextInput>div>div>input {
        border-radius: 8px;
    }
    
    .stSelectbox>div>div>select {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if 'language' not in st.session_state:
    st.session_state.language = 'en'
if 'location' not in st.session_state:
    if not USE_API_MODE:
        try:
            from utils.location_detector import get_location_detector
            detector = get_location_detector()
            st.session_state.location = detector.get_location_from_ip()
        except:
            st.session_state.location = {
                'city': 'Nashik', 'region': 'Maharashtra',
                'country': 'India', 'district': 'Nashik'
            }
    else:
        st.session_state.location = {
            'city': 'Nashik', 'region': 'Maharashtra',
            'country': 'India', 'district': 'Nashik'
        }
if 'user_profile' not in st.session_state:
    detected_district = st.session_state.location.get('district', 'Nashik')
    st.session_state.user_profile = {
        'name': '', 'village': '', 'district': detected_district,
        'phone': '', 'crops': [], 'land_size_acres': 0.0
    }
if 'profile_saved' not in st.session_state:
    st.session_state.profile_saved = False
if 'feedback_submitted' not in st.session_state:
    st.session_state.feedback_submitted = set()
if 'quick_action_query' not in st.session_state:
    st.session_state.quick_action_query = ""

# Helper functions (keeping all existing functionality)
def get_agent_badge(agent_name: str) -> str:
    """Generate HTML badge for agent"""
    badges = {
        'vision-model': ('badge-vision', '🔍 Vision AI'),
        'agri-expert': ('badge-agri', '🌱 Agri Expert'),
        'policy-navigator': ('badge-policy', '📋 Policy Navigator'),
        'resource-optimizer': ('badge-resource', '⚡ Resource Optimizer'),
        'supervisor': ('badge-supervisor', '🎯 Supervisor')
    }
    css_class, label = badges.get(agent_name, ('badge-supervisor', '🤖 Assistant'))
    return f'<span class="agent-badge {css_class}">{label}</span>'

def encode_image(image_file) -> str:
    """Encode image to base64"""
    return base64.b64encode(image_file.read()).decode('utf-8')
