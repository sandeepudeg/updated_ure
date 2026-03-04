#!/usr/bin/env python3
"""
GramSetu Enterprise UI - Clean Implementation
Three-column layout matching gramsetu_enterprise_ui_mockup.html
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
import imghdr

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# AWS credentials from secrets
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

# Force wide layout with custom CSS
st.markdown("""
<style>
    .main .block-container {
        max-width: 100% !important;
        padding-left: 5rem !important;
        padding-right: 5rem !important;
    }
</style>
""", unsafe_allow_html=True)


# Enterprise CSS
st.markdown("""
<style>
    /* Hide Streamlit defaults */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Main styling */
    .main {
        background: linear-gradient(135deg, #E8F5E9 0%, #F1F8E9 100%);
        padding: 0 !important;
        min-height: 100vh;
    }
    
    .block-container {
        padding: 2rem !important;
        max-width: 1400px !important;
        margin: 0 auto !important;
    }
    
    /* Chat messages */
    .chat-message {
        padding: 1rem 1.5rem;
        border-radius: 18px;
        margin-bottom: 1rem;
        animation: fadeIn 0.3s ease-in;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        max-width: 70%;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .user-message {
        background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
        color: white;
        border-radius: 18px 18px 4px 18px;
        margin-left: auto;
    }
    
    .assistant-message {
        background: white;
        border: 1px solid #E0E0E0;
        border-radius: 18px 18px 18px 4px;
        margin-right: auto;
    }
    
    /* Agent badges */
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
    .badge-supervisor { background: #E1BEE7; color: #4A148C; }
    
    /* Info cards */
    .info-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
    }
    
    .info-card h3 {
        margin: 0 0 1rem 0;
        font-size: 1.1rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .info-card h3 span {
        font-size: 1.2rem;
        line-height: 1;
    }
    
    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        width: 100%;
        background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);
        color: white;
        border: none;
        padding: 0.8rem 1rem;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        justify-content: flex-start;
        gap: 0.5rem;
        font-size: 0.9rem;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    /* Icon sizing in buttons */
    .stButton>button span {
        font-size: 1rem;
        line-height: 1;
    }
    
    /* Inputs */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        border-radius: 8px;
        border: 2px solid #E0E0E0;
    }
    
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #4CAF50;
        box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.1);
    }
    
    /* Column styling */
    [data-testid="column"] {
        padding: 0.5rem;
    }
    
    /* Selectbox styling for header */
    .stSelectbox {
        margin-top: 0;
    }
    
    /* Hide selectbox label in header */
    div[data-testid="stSelectbox"] label {
        display: none;
    }
    
    /* Scrollbar styling for chat messages */
    div[style*="overflow-y: auto"]::-webkit-scrollbar {
        width: 8px;
    }
    
    div[style*="overflow-y: auto"]::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    
    div[style*="overflow-y: auto"]::-webkit-scrollbar-thumb {
        background: #2E7D32;
        border-radius: 4px;
    }
    
    div[style*="overflow-y: auto"]::-webkit-scrollbar-thumb:hover {
        background: #1B5E20;
    }
    
    /* Inputs */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        border-radius: 8px;
        border: 2px solid #E0E0E0;
    }
    
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #4CAF50;
        box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.1);
    }
    
    /* Column styling */
    [data-testid="column"] {
        padding: 0 0.5rem !important;
    }
    
    /* First and last column no extra padding */
    [data-testid="column"]:first-child {
        padding-left: 0 !important;
    }
    
    [data-testid="column"]:last-child {
        padding-right: 0 !important;
    }
    
    /* Remove default Streamlit column backgrounds */
    [data-testid="column"] > div {
        background: transparent !important;
        box-shadow: none !important;
    }
    
    /* File uploader styling */
    .stFileUploader {
        margin-bottom: 1rem;
    }
    
    .stFileUploader > div {
        padding: 1rem;
        border: 2px dashed #E0E0E0;
        border-radius: 12px;
        background: #FAFAFA;
    }
    
    .stFileUploader > div:hover {
        border-color: #4CAF50;
        background: #F1F8E9;
    }
    
    /* Chat input area styling */
    .stChatInput {
        border-radius: 12px;
        border: 2px solid #E0E0E0;
    }
    
    .stChatInput:focus-within {
        border-color: #4CAF50;
        box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.1);
    }
    
    /* Info/success/warning boxes */
    .stAlert {
        border-radius: 8px;
        padding: 0.8rem 1rem;
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
            st.session_state.location = {'city': 'Nashik', 'region': 'Maharashtra', 'country': 'India', 'district': 'Nashik'}
    else:
        st.session_state.location = {'city': 'Nashik', 'region': 'Maharashtra', 'country': 'India', 'district': 'Nashik'}
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        'name': '', 'village': '', 'district': st.session_state.location.get('district', 'Nashik'),
        'phone': '', 'crops': [], 'land_size_acres': 0.0
    }
if 'profile_saved' not in st.session_state:
    st.session_state.profile_saved = False
if 'quick_action_query' not in st.session_state:
    st.session_state.quick_action_query = ""

# Helper functions
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

def process_query_local(query: str, image_data: str = None, location: dict = None) -> dict:
    """Process query using local agents"""
    try:
        if location:
            try:
                from utils.location_detector import get_location_detector
                detector = get_location_detector()
                location_str = detector.get_location_string(location)
                query_with_context = f"[User Location: {location_str}] {query}"
            except:
                query_with_context = query
        else:
            query_with_context = query
        
        if image_data:
            logger.info("Processing with image using Bedrock vision")
            bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
            
            image_bytes = base64.b64decode(image_data)
            image_format = imghdr.what(None, h=image_bytes)
            bedrock_format = 'jpeg' if image_format in ['jpeg', 'jpg'] else image_format or 'jpeg'
            
            messages = [{
                "role": "user",
                "content": [
                    {"image": {"format": bedrock_format, "source": {"bytes": image_bytes}}},
                    {"text": query_with_context}
                ]
            }]
            
            response = bedrock_runtime.converse(
                modelId="amazon.nova-lite-v1:0",
                messages=messages,
                inferenceConfig={"temperature": 0.7, "maxTokens": 2000},
                system=[{"text": """You are Gram-Setu (Village Bridge), an AI assistant for Indian farmers.

IMPORTANT CONTEXT:
- The user's location is provided in the query (look for [User Location: ...])
- ALWAYS use this location context when providing advice
- ALL prices MUST be in Indian Rupees (₹ or INR)
- Provide location-specific recommendations

You provide direct, helpful answers about:
- Crop diseases and pest management (analyze images)
- Market prices and trends (ALWAYS in Indian Rupees ₹)
- Government schemes (PM-Kisan, PMFBY, etc.)
- Irrigation and water management
- Weather-based farming advice (specific to user's location)
- Best farming practices

GUIDELINES:
- Use simple, farmer-friendly language
- Provide practical, actionable advice
- When discussing prices, ALWAYS use Indian Rupees (₹): ₹500/quintal, ₹25/kg
- Reference the user's location when giving weather forecasts or market prices
- When analyzing crop images, identify the crop, diseases/pests, and provide treatment recommendations

Always respond in a helpful, supportive manner."""}]
            )
            
            response_text = response['output']['message']['content'][0]['text']
            return {'success': True, 'response': response_text, 'agent_used': 'vision-model', 'metadata': {'location': location, 'has_image': True}}
        else:
            from agents.supervisor_simple import supervisor_simple_agent
            response = supervisor_simple_agent(query_with_context)
            return {'success': True, 'response': str(response), 'agent_used': 'supervisor', 'metadata': {'location': location}}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {'success': False, 'response': f"Error: {str(e)}", 'agent_used': 'error', 'metadata': {}}


# Initialize language in session state if not present
if 'language' not in st.session_state:
    st.session_state.language = 'en'

# Language selector BEFORE header (will be positioned into header with CSS)
# Using a unique container ID for precise targeting
st.markdown('<div id="lang-selector-wrapper">', unsafe_allow_html=True)
language = st.selectbox(
    "Language",
    options=['en', 'hi', 'mr'],
    format_func=lambda x: {'en': '🇬🇧 English', 'hi': '🇮🇳 हिंदी', 'mr': '🇮🇳 मराठी'}[x],
    index=['en', 'hi', 'mr'].index(st.session_state.language),
    key="lang_select_header",
    label_visibility="collapsed"
)
st.session_state.language = language
st.markdown('</div>', unsafe_allow_html=True)

# Custom Enterprise Header
header_html = f"""
<div id="gramsetu-header" style="background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%); 
            color: white; 
            padding: 1rem 0; 
            margin: -2rem calc(-50vw + 50%) 2rem calc(-50vw + 50%);
            width: 100vw;
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
            position: sticky;
            top: 0;
            z-index: 999;">
    <div style="max-width: 1400px; margin: 0 auto; padding: 0 2rem; display: flex; justify-content: space-between; align-items: center;">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="font-size: 2.5rem; line-height: 1;">🌾</div>
            <div>
                <h1 style="margin: 0; font-size: 1.8rem; font-weight: 700; line-height: 1.2;">GramSetu</h1>
                <p style="margin: 0; font-size: 0.9rem; opacity: 0.9; line-height: 1.2;">AI-Powered Rural Assistant</p>
            </div>
        </div>
        <div id="header-right-section" style="display: flex; gap: 1rem; align-items: center;">
            <div style="background: rgba(255,255,255,0.2); padding: 0.5rem 1rem; border-radius: 20px; display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 1.2rem;">👤</span>
                <span>{st.session_state.user_profile.get('name', 'Guest User')}</span>
            </div>
        </div>
    </div>
</div>
"""

st.markdown(header_html, unsafe_allow_html=True)

# CSS to position language selector into header
st.markdown("""
<style>
    /* Position the language selector wrapper into the header */
    #lang-selector-wrapper {
        position: fixed !important;
        top: 1.5rem !important;
        right: 15rem !important;
        z-index: 1001 !important;
        width: 150px !important;
    }
    
    /* Style the selectbox to match header theme */
    #lang-selector-wrapper div[data-baseweb="select"] {
        background: rgba(255,255,255,0.2) !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
        border-radius: 8px !important;
    }
    
    #lang-selector-wrapper select {
        color: white !important;
        background: transparent !important;
        border: none !important;
        font-size: 0.9rem !important;
        padding: 0.5rem 1rem !important;
    }
    
    #lang-selector-wrapper option {
        color: black !important;
        background: white !important;
    }
    
    /* Hide the label */
    #lang-selector-wrapper label {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Three-Column Enterprise Layout with proper spacing
left_col, main_col, right_col = st.columns([1.2, 2.5, 1.2], gap="large")

# ============================================================================
# LEFT COLUMN - Quick Actions & Location
# ============================================================================
with left_col:
    # Quick Actions Card
    st.markdown("""
    <div style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 1rem;">
        <h3 style="margin: 0 0 1rem 0; color: #2E7D32; font-size: 1.1rem; font-weight: 600;">🚀 Quick Actions</h3>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🌱 Crop Disease Help", use_container_width=True, key="qa_disease"):
        st.session_state.quick_action_query = 'I need help identifying a crop disease'
        st.rerun()
    
    if st.button("� Government Schemes", use_container_width=True, key="qa_schemes"):
        st.session_state.quick_action_query = 'What government schemes are available for farmers?'
        st.rerun()
    
    if st.button("💰 Market Prices", use_container_width=True, key="qa_prices"):
        st.session_state.quick_action_query = 'What are the current market prices for crops?'
        st.rerun()
    
    if st.button("💧 Irrigation Tips", use_container_width=True, key="qa_irrigation"):
        st.session_state.quick_action_query = 'When should I irrigate my crops?'
        st.rerun()
    
    if st.button("🌤️ Weather Forecast", use_container_width=True, key="qa_weather"):
        st.session_state.quick_action_query = 'What is the weather forecast for the next few days?'
        st.rerun()
    
    # Location Card
    st.markdown("""
    <div style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin: 1.5rem 0;">
        <h3 style="margin: 0 0 1rem 0; color: #2196F3; font-size: 1.1rem; font-weight: 600;">📍 Your Location</h3>
        <div style="background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%); padding: 1rem; border-radius: 8px; border-left: 4px solid #2196F3;">
            <h4 style="margin: 0 0 0.5rem 0; color: #2196F3; font-size: 0.9rem;">Auto-Detected</h4>
    """, unsafe_allow_html=True)
    
    if st.session_state.location:
        location_str = f"<p style='margin: 0.3rem 0; font-size: 0.9rem;'><strong>District:</strong> {st.session_state.location.get('city', 'Unknown')}</p>"
        location_str += f"<p style='margin: 0.3rem 0; font-size: 0.9rem;'><strong>State:</strong> {st.session_state.location.get('region', 'Unknown')}</p>"
        location_str += f"<p style='margin: 0.3rem 0; font-size: 0.9rem;'><strong>Country:</strong> {st.session_state.location.get('country', 'India')}</p>"
        st.markdown(location_str + "</div></div>", unsafe_allow_html=True)
    else:
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # User Profile Card
    st.markdown("""
    <div style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-top: 1.5rem;">
        <h3 style="margin: 0 0 1rem 0; color: #2E7D32; font-size: 1.1rem; display: flex; align-items: center; gap: 0.5rem;">
            <span>👤</span> User Profile
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.profile_saved:
        # Profile Creation Form
        with st.form("profile_form"):
            name = st.text_input("Name / नाव", value=st.session_state.user_profile.get('name', ''))
            village = st.text_input("Village / गाव", value=st.session_state.user_profile.get('village', ''))
            
            # District dropdown with auto-detected value
            districts = ['Nashik', 'Pune', 'Ahmednagar', 'Dhule', 'Jalgaon', 'Aurangabad', 'Mumbai', 'Nagpur', 'Solapur', 'Kolhapur', 'Other']
            current_district = st.session_state.user_profile.get('district', 'Nashik')
            
            # Find index of current district
            try:
                district_index = districts.index(current_district)
            except ValueError:
                district_index = 0  # Default to Nashik
            
            district = st.selectbox(
                "District / जिल्हा",
                options=districts,
                index=district_index,
                help="Auto-detected from your location. Change if incorrect."
            )
            
            phone = st.text_input("Phone / फोन", value=st.session_state.user_profile.get('phone', ''), placeholder="+91XXXXXXXXXX")
            
            crops_options = ['Wheat', 'Rice', 'Cotton', 'Sugarcane', 'Onion', 'Tomato', 'Grapes', 'Other']
            crops = st.multiselect("Crops / पिके", options=crops_options, default=st.session_state.user_profile.get('crops', []))
            
            land_size = st.number_input("Land Size (acres) / जमीन (एकर)", min_value=0.0, max_value=1000.0, value=st.session_state.user_profile.get('land_size_acres', 0.0), step=0.5)
            
            submitted = st.form_submit_button("💾 Save Profile", use_container_width=True)
            
            if submitted:
                profile = {
                    'name': name,
                    'village': village,
                    'district': district,
                    'phone': phone,
                    'crops': crops,
                    'land_size_acres': land_size
                }
                
                # Save profile locally
                st.session_state.user_profile = profile
                st.session_state.profile_saved = True
                st.success("✅ Profile saved successfully!")
                st.rerun()
    else:
        # Display saved profile
        st.success("✅ Profile Saved")
        profile = st.session_state.user_profile
        st.text(f"Name: {profile.get('name', 'N/A')}")
        st.text(f"Village: {profile.get('village', 'N/A')}")
        st.text(f"District: {profile.get('district', 'N/A')}")
        if profile.get('crops'):
            st.text(f"Crops: {', '.join(profile.get('crops', []))}")
        st.text(f"Land: {profile.get('land_size_acres', 0)} acres")
        
        if st.button("✏️ Edit Profile", use_container_width=True):
            st.session_state.profile_saved = False
            st.rerun()


# ============================================================================
# MAIN COLUMN - Chat Interface
# ============================================================================
with main_col:
    # Chat container with white background
    st.markdown("""
    <div style="background: white; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 0; overflow: hidden;">
        <div style="background: linear-gradient(135deg, #F1F8E9 0%, #DCEDC8 100%); padding: 1.5rem; border-bottom: 2px solid #C5E1A5;">
            <h2 style="margin: 0; color: #2E7D32; display: flex; align-items: center; gap: 0.5rem; font-size: 1.5rem;">
                <span>💬</span> Chat with GramSetu
            </h2>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Welcome message
    if len(st.session_state.messages) == 0:
        st.markdown("""
        <div style="text-align: center; padding: 3rem 2rem; background: white; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="font-size: 4rem; margin-bottom: 1rem;">🌾</div>
            <h3 style="color: #2E7D32; font-size: 1.8rem; margin-bottom: 1rem;">Welcome to GramSetu!</h3>
            <p style="color: #757575; margin-bottom: 2rem; max-width: 600px; margin-left: auto; margin-right: auto;">
                Your AI-powered assistant for farming, market prices, government schemes, and more. 
                Ask me anything or upload a crop image for disease identification.
            </p>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-top: 2rem;">
                <div style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); transition: transform 0.2s;">
                    <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🌱</div>
                    <h4 style="color: #2E7D32; margin-bottom: 0.5rem;">Crop Diseases</h4>
                    <p style="font-size: 0.85rem; color: #757575;">Upload photos for instant disease identification</p>
                </div>
                <div style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); transition: transform 0.2s;">
                    <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">💰</div>
                    <h4 style="color: #2E7D32; margin-bottom: 0.5rem;">Market Prices</h4>
                    <p style="font-size: 0.85rem; color: #757575;">Real-time prices in Indian Rupees</p>
                </div>
                <div style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); transition: transform 0.2s;">
                    <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📋</div>
                    <h4 style="color: #2E7D32; margin-bottom: 0.5rem;">Govt Schemes</h4>
                    <p style="font-size: 0.85rem; color: #757575;">PM-Kisan, PMFBY eligibility</p>
                </div>
                <div style="background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); transition: transform 0.2s;">
                    <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🌤️</div>
                    <h4 style="color: #2E7D32; margin-bottom: 0.5rem;">Weather</h4>
                    <p style="font-size: 0.85rem; color: #757575;">Location-based forecasts</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Chat messages container with scrolling
    st.markdown('<div style="background: #FAFAFA; padding: 1.5rem; border-radius: 12px; min-height: 400px; max-height: 600px; overflow-y: auto; margin-bottom: 1rem;">', unsafe_allow_html=True)
    
    # Display chat messages
    for idx, message in enumerate(st.session_state.messages):
        role = message['role']
        content = message['content']
        
        if role == 'user':
            st.markdown(f'<div class="chat-message user-message"><strong>You:</strong><br>{content}</div>', unsafe_allow_html=True)
        else:
            agent_used = message.get('agent_used', 'supervisor')
            badge_html = get_agent_badge(agent_used)
            st.markdown(f'<div class="chat-message assistant-message">{badge_html}<br>{content}</div>', unsafe_allow_html=True)
            
            # Feedback buttons
            message_id = message.get('id', f"msg_{idx}")
            col1, col2, col3 = st.columns([1, 1, 8])
            with col1:
                if st.button("�", key=f"like_{message_id}"):
                    st.success("Thanks for your feedback!")
            with col2:
                if st.button("�👎", key=f"dislike_{message_id}"):
                    st.info("We'll work on improving!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Image upload
    uploaded_image = st.file_uploader(
        "📷 Upload crop image (optional)",
        type=['jpg', 'jpeg', 'png'],
        help="Upload a clear photo of your crop for disease identification",
        key="image_upload"
    )
    
    # Store image in session state
    if uploaded_image is not None:
        st.session_state.uploaded_image_bytes = uploaded_image.getvalue()
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(uploaded_image, caption="Uploaded Image", use_container_width=True)
        with col2:
            st.info("✅ Image uploaded! Ask a question about this crop.")
            if st.button("🗑️ Remove image", key="remove_img"):
                if 'uploaded_image_bytes' in st.session_state:
                    del st.session_state.uploaded_image_bytes
                st.rerun()
    elif 'uploaded_image_bytes' in st.session_state:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(st.session_state.uploaded_image_bytes, caption="Uploaded Image", use_container_width=True)
        with col2:
            st.info("✅ Image ready for analysis.")
            if st.button("🗑️ Remove image", key="remove_img2"):
                del st.session_state.uploaded_image_bytes
                st.rerun()
    
    # Chat input
    user_input = st.chat_input("Ask me anything about farming, schemes, or resources...")
    
    # Add icon buttons below chat input to match mockup
    st.markdown("""
    <div style="display: flex; gap: 0.5rem; justify-content: flex-end; margin-top: -0.5rem; padding: 0 1rem;">
        <span style="font-size: 0.85rem; color: #757575;">💡 Tip: Upload images with 📷 button or use 🎤 for voice</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Handle quick action query
    if st.session_state.quick_action_query and not user_input:
        st.info(f"💡 Quick Action: {st.session_state.quick_action_query}")
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button("✅ Send this query", use_container_width=True, key="send_qa"):
                user_input = st.session_state.quick_action_query
                st.session_state.quick_action_query = ""
        with col2:
            if st.button("❌ Clear", use_container_width=True, key="clear_qa"):
                st.session_state.quick_action_query = ""
                st.rerun()
    
    # Process user input
    if user_input:
        if st.session_state.quick_action_query:
            st.session_state.quick_action_query = ""
        
        st.session_state.messages.append({'role': 'user', 'content': user_input})
        
        with st.spinner("🤔 Thinking..."):
            image_data = None
            if 'uploaded_image_bytes' in st.session_state:
                image_data = base64.b64encode(st.session_state.uploaded_image_bytes).decode('utf-8')
            
            result = process_query_local(user_input, image_data, st.session_state.location)
            
            st.session_state.messages.append({
                'role': 'assistant',
                'content': result['response'],
                'agent_used': result['agent_used'],
                'id': str(uuid.uuid4())
            })
        
        st.rerun()


# ============================================================================
# RIGHT COLUMN - Widgets (Weather, Market Prices, Tips)
# ============================================================================
with right_col:
    # Weather Widget
    st.markdown("""
    <div style="background: linear-gradient(135deg, #E1F5FE 0%, #B3E5FC 100%); 
                padding: 1.5rem; border-radius: 12px; text-align: center; margin-bottom: 1rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">☀️</div>
        <div style="font-size: 2rem; font-weight: 700; color: #2196F3;">28°C</div>
        <p style="margin: 0.5rem 0; color: #0277BD;">Sunny, Nashik</p>
        <p style="font-size: 0.85rem; margin-top: 0.5rem; color: #01579B;">
            <strong>Next 3 days:</strong> Clear skies<br>
            Good for irrigation
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Market Prices Widget
    st.markdown("""
    <div style="background: linear-gradient(135deg, #F3E5F5 0%, #E1BEE7 100%); 
                padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h3 style="margin: 0 0 1rem 0; color: #6A1B9A;">💰 Today's Prices (Nashik)</h3>
        <div style="background: white; padding: 1rem; border-radius: 8px;">
            <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid rgba(0,0,0,0.1);">
                <span>Onion</span>
                <span style="font-weight: 700; color: #4CAF50;">₹3,000/q</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid rgba(0,0,0,0.1);">
                <span>Wheat</span>
                <span style="font-weight: 700; color: #4CAF50;">₹2,125/q</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 0.5rem 0; border-bottom: 1px solid rgba(0,0,0,0.1);">
                <span>Tomato</span>
                <span style="font-weight: 700; color: #4CAF50;">₹1,800/q</span>
            </div>
            <div style="display: flex; justify-content: space-between; padding: 0.5rem 0;">
                <span>Cotton</span>
                <span style="font-weight: 700; color: #4CAF50;">₹6,500/q</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Daily Tip Widget
    st.markdown("""
    <div style="background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%); 
                padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                border-left: 4px solid #FF9800;">
        <h3 style="margin: 0 0 1rem 0; color: #E65100;">💡 Today's Tip</h3>
        <p style="font-size: 0.9rem; margin: 0; color: #424242;">
            <strong>Irrigation Alert:</strong> With clear weather expected, plan your irrigation for early morning or evening to minimize water loss.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Government Scheme Alert
    st.markdown("""
    <div style="background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%); 
                padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                border-left: 4px solid #4CAF50;">
        <h3 style="margin: 0 0 1rem 0; color: #2E7D32;">📢 New Scheme</h3>
        <p style="font-size: 0.9rem; margin: 0; color: #424242;">
            <strong>PM-Kisan 16th Installment</strong> is now available. Check your eligibility and apply today!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem; padding: 1rem 0;">
    <p>🌾 GramSetu - Empowering Rural India with AI</p>
    <p style="font-size: 0.8rem;">Powered by Amazon Bedrock Nova Lite | Location-aware | Prices in ₹</p>
</div>
""", unsafe_allow_html=True)
