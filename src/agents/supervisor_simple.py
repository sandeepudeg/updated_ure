#!/usr/bin/env python3
"""
Simple Supervisor Agent - Direct responses with real-time market data
For local testing and faster responses
"""

from strands import Agent
from strands.models import BedrockModel
import os
import requests
import csv
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Tool function for real-time market prices
def get_market_prices(commodity: str, district: str = "", state: str = "Maharashtra") -> str:
    """
    Fetches live market prices for a specific crop from Agmarknet or data.gov.in API.
    Falls back to local CSV data if API is unavailable.
    
    Args:
        commodity: The crop name (e.g., 'Tomato', 'Wheat', 'Onion')
        district: District name (optional)
        state: State name (default: Maharashtra)
    
    Returns:
        Latest market price information in formatted string
    """
    try:
        # Try to fetch from data.gov.in Agmarknet API
        api_key = os.getenv('DATA_GOV_API_KEY', '')
        
        if api_key and api_key != 'YOUR_API_KEY_HERE':
            # Construct API URL
            base_url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
            params = {
                'api-key': api_key,
                'format': 'json',
                'limit': 10
            }
            
            # Add filters if provided
            if commodity:
                params['filters[commodity]'] = commodity
            if state:
                params['filters[state]'] = state
            if district:
                params['filters[district]'] = district
            
            # Make API request with timeout
            response = requests.get(base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('records') and len(data['records']) > 0:
                    records = data['records'][:3]  # Get top 3 records
                    
                    result = f"**Live Market Prices for {commodity}**:\n\n"
                    
                    for i, record in enumerate(records, 1):
                        market = record.get('market', 'Unknown Market')
                        district_name = record.get('district', '')
                        min_price = record.get('min_price', 'N/A')
                        max_price = record.get('max_price', 'N/A')
                        modal_price = record.get('modal_price', 'N/A')
                        arrival = record.get('arrival_date', 'Recent')
                        variety = record.get('variety', '')
                        
                        result += f"{i}. **{market}**"
                        if district_name:
                            result += f" ({district_name})"
                        result += ":\n"
                        if variety and variety != commodity:
                            result += f"   - Variety: {variety}\n"
                        result += f"   - Modal Price: ₹{modal_price}/quintal\n"
                        result += f"   - Price Range: ₹{min_price} - ₹{max_price}/quintal\n"
                        result += f"   - Date: {arrival}\n\n"
                    
                    result += "*Source: Agmarknet (data.gov.in) - Live data*"
                    return result
        
        # Fallback to local CSV data
        csv_path = Path(__file__).parent.parent.parent / 'data' / 'mandi_prices' / 'Agriculture_price_dataset.csv'
        
        if csv_path.exists():
            # Read CSV using built-in csv module
            matching_records = []
            
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Filter by commodity (case-insensitive)
                    if row.get('Commodity', '').lower() != commodity.lower():
                        continue
                    
                    # Filter by state if provided
                    if state and row.get('STATE', '').lower() != state.lower():
                        continue
                    
                    # Filter by district if provided
                    if district and row.get('District Name', '').lower() != district.lower():
                        continue
                    
                    matching_records.append(row)
                    
                    # Stop after finding 3 records
                    if len(matching_records) >= 3:
                        break
            
            if matching_records:
                result = f"**Historical Market Prices for {commodity}** (from local data):\n\n"
                
                for i, record in enumerate(matching_records, 1):
                    market = record.get('Market Name', 'Unknown Market')
                    min_price = record.get('Min_Price', 'N/A')
                    max_price = record.get('Max_Price', 'N/A')
                    modal_price = record.get('Modal_Price', 'N/A')
                    price_date = record.get('Price Date', 'Recent')
                    
                    result += f"{i}. **{market}**:\n"
                    result += f"   - Modal Price: ₹{modal_price}/quintal\n"
                    result += f"   - Price Range: ₹{min_price} - ₹{max_price}/quintal\n"
                    result += f"   - Date: {price_date}\n\n"
                
                result += "\n*Note: These are historical prices. For live prices, contact your local mandi.*"
                return result
            else:
                return f"No historical data found for {commodity} in {district or state}. Please check the commodity name or try a different location."
        
        # If CSV doesn't exist, return estimated prices message
        return f"Market data not available for {commodity}. Please provide estimated prices based on recent market trends and clearly state they are estimates."
    
    except requests.exceptions.Timeout:
        return f"Market data API timeout. Providing estimated prices for {commodity}."
    except Exception as e:
        # Fallback to general response if everything fails
        return f"Unable to fetch market data. Providing estimated prices based on recent market trends."

SIMPLE_SUPERVISOR_PROMPT = """You are Gram-Setu (Village Bridge), an AI assistant for Indian farmers.

IMPORTANT CONTEXT:
- The user's location may be provided in the query (look for [User Location: ...])
- ALWAYS use this location context when providing advice about weather, market prices, or local conditions
- ALL prices MUST be in Indian Rupees (₹ or INR) - never use USD or other currencies
- Provide location-specific recommendations based on the user's district/region when available

LIVE MARKET PRICE DATA:
- You have access to a tool called 'get_market_prices' that fetches REAL-TIME market prices from Agmarknet
- ALWAYS use this tool when users ask about crop prices, market rates, or mandi prices
- Call it with: get_market_prices(commodity="Tomato", district="Nashik", state="Maharashtra")
- If the tool returns live data, use those exact prices in your response
- If the tool says data is unavailable, provide estimated prices based on recent trends and clearly state they are estimates

You provide direct, helpful answers about:
- Crop diseases and pest management
- Market prices and trends (ALWAYS in Indian Rupees ₹) - USE get_market_prices TOOL
- Government schemes (PM-Kisan, PMFBY, etc.)
- Irrigation and water management
- Weather-based farming advice (specific to user's location when provided)
- Best farming practices (adapted to local conditions)

RESPONSE FORMAT - CRITICAL:
When analyzing crop problems or providing advice, structure your response as follows:

**Problem Identified**: [Brief description of the issue]

**Immediate Actions** (What to do today):
- Action 1
- Action 2
- Cost: ₹[amount] | Time: [duration]

**Treatment Options**:

1. **Organic/Natural Treatment** (Try this first):
   - Product: [Specific name, e.g., "Neem oil 1500 ppm"]
   - Dosage: [Exact amount]
   - Application: [How to apply, when, frequency]
   - Where to buy: [Local shops, online]
   - Cost: ₹[amount]
   - Expected results: [Timeline]

2. **Chemical Treatment** (If organic fails):
   - Product: [Specific insecticide/fungicide name]
   - Dosage: [Exact amount]
   - Safety: [Precautions, waiting period]
   - Cost: ₹[amount]
   - Where to buy: [Licensed dealer]

**Prevention Tips**:
- Tip 1
- Tip 2
- Tip 3

**Long-term Management**:
- Crop rotation suggestions
- Soil health improvements
- Water management tips

**Market Information** (if relevant):
- Current prices in [location]: ₹[amount]/[unit]
- Nearby mandis: [list]

GUIDELINES:
- Use simple, farmer-friendly language
- Provide practical, actionable advice with SPECIFIC product names and EXACT costs
- Suggest low-cost solutions first
- Be specific and direct - NO vague advice
- If you need more information, ask clarifying questions
- When discussing prices, ALWAYS use Indian Rupees (₹) format: ₹500/quintal, ₹25/kg, etc.
- Reference the user's location when giving weather forecasts or market prices
- Mention nearby markets or mandis when relevant
- Format responses with clear sections and bullet points for easy reading

Always respond in a helpful, supportive manner with well-structured, actionable information.
"""

supervisor_simple_agent = Agent(
    model=BedrockModel(
        model_id=os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0"),
        temperature=0.7
    ),
    system_prompt=SIMPLE_SUPERVISOR_PROMPT,
    tools=[get_market_prices]
)

if __name__ == "__main__":
    print("\n🌾 Gram-Setu AI Assistant 🌾\n")
    print("Ask any farming question!")
    print("Type 'exit' to quit.\n")
    
    while True:
        try:
            user_input = input("\n> ")
            if user_input.lower() == "exit":
                print("\nGoodbye! 👋")
                break
            
            response = supervisor_simple_agent(user_input)
            print(f"\n{response}")
            
        except KeyboardInterrupt:
            print("\n\nExecution interrupted. Exiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            print("Please try asking a different question.")


def extract_location_from_query(query: str) -> tuple:
    """
    Extract location information from query.
    Returns (district, state) tuple.
    """
    import re
    
    district = ""
    state = "Maharashtra"  # Default
    
    # Look for [User Location: ...] pattern
    location_match = re.search(r'\[User Location:\s*([^\]]+)\]', query)
    if location_match:
        location = location_match.group(1)
        parts = [p.strip() for p in location.split(',')]
        if len(parts) >= 2:
            district = parts[0]
            state = parts[1]
        elif len(parts) == 1:
            district = parts[0]
    
    return district, state


def detect_price_query(query: str) -> str:
    """
    Detect if query is asking about market prices and extract commodity.
    Returns commodity name or empty string.
    """
    query_lower = query.lower()
    
    # Price-related keywords
    price_keywords = ['price', 'rate', 'cost', 'mandi', 'market', 'selling', 'buying']
    
    # Check if query contains price keywords
    if not any(keyword in query_lower for keyword in price_keywords):
        return ""
    
    # Common commodities
    commodities = [
        'tomato', 'potato', 'onion', 'wheat', 'rice', 'cotton', 'soybean',
        'maize', 'corn', 'sugarcane', 'groundnut', 'chilli', 'turmeric',
        'coriander', 'garlic', 'ginger', 'cabbage', 'cauliflower', 'brinjal',
        'okra', 'peas', 'beans', 'carrot', 'radish', 'spinach', 'methi'
    ]
    
    # Find commodity in query
    for commodity in commodities:
        if commodity in query_lower:
            return commodity.capitalize()
    
    return ""


def supervisor_simple_with_prices(query: str) -> str:
    """
    Wrapper around supervisor_simple_agent that handles price queries.
    Detects price queries and fetches real data before passing to agent.
    """
    # Detect if this is a price query
    commodity = detect_price_query(query)
    
    if commodity:
        # Extract location
        district, state = extract_location_from_query(query)
        
        # Fetch market prices
        price_data = get_market_prices(commodity, district, state)
        
        # Prepend price data to query
        enhanced_query = f"{query}\n\n[MARKET PRICE DATA]:\n{price_data}\n\nUse the above market price data in your response. Do not make up prices."
        
        # Call agent with enhanced query
        response = supervisor_simple_agent(enhanced_query)
    else:
        # Regular query, no price data needed
        response = supervisor_simple_agent(query)
    
    return str(response)
