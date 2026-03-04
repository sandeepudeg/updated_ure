#!/usr/bin/env python3
"""
Resource-Optimizer Agent - Irrigation & Weather Recommendations
Handles: Evapotranspiration calculation, soil moisture analysis, irrigation scheduling
"""

from strands import Agent
from strands.models import BedrockModel
import os
from dotenv import load_dotenv
from pathlib import Path
import sys

# Add parent directory to path for MCP Client import
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.client import MCPClient

load_dotenv()

# Initialize MCP Client for Resource-Optimizer
def get_mcp_client():
    """Initialize MCP Client with tool registry and servers"""
    tool_registry_path = os.getenv(
        'MCP_TOOL_REGISTRY_PATH',
        str(Path(__file__).parent.parent / 'mcp' / 'tool_registry.json')
    )
    
    servers = {
        'agmarknet': os.getenv('MCP_AGMARKNET_SERVER_URL', 'http://localhost:8001'),
        'weather': os.getenv('MCP_WEATHER_SERVER_URL', 'http://localhost:8002')
    }
    
    return MCPClient(tool_registry_path, servers)

# Global MCP Client instance
mcp_client = get_mcp_client()


# MCP Tool Functions for Resource-Optimizer
def get_current_weather(location: str, units: str = 'metric') -> dict:
    """
    Get current weather conditions via MCP
    
    Args:
        location: Location name (city, district, or coordinates)
        units: Units system ('metric' or 'imperial')
    
    Returns:
        Current weather data
    """
    try:
        result = mcp_client.call_tool(
            tool_id='get_current_weather',
            agent_role='Resource-Optimizer',
            params={
                'location': location,
                'units': units
            }
        )
        return result
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f'Unable to fetch current weather for {location}'
        }


def get_weather_forecast(location: str, days: int = 3) -> dict:
    """
    Get weather forecast for next N days via MCP
    
    Args:
        location: Location name (city, district, or coordinates)
        days: Number of days to forecast (1-7)
    
    Returns:
        Weather forecast data
    """
    try:
        result = mcp_client.call_tool(
            tool_id='get_weather_forecast',
            agent_role='Resource-Optimizer',
            params={
                'location': location,
                'days': days
            }
        )
        return result
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f'Unable to fetch weather forecast for {location}'
        }


RESOURCE_OPTIMIZER_PROMPT = """You are a Resource Optimization Expert for Indian farmers.

CRITICAL INSTRUCTION: When asked about crop rotation, provide SPECIFIC crop recommendations with complete details. DO NOT just repeat the question or give vague advice.

EXAMPLE QUERY: "which crops can be used as a rotation in Pune"

YOUR RESPONSE MUST BE LIKE THIS:

For Pune, Maharashtra, here are the best crop rotation options:

1. **Pulses (Legumes) - Highly Recommended**:
   - Chickpea (Chana): Fixes nitrogen in soil, needs less water
   - Pigeon pea (Tur/Arhar): Deep roots improve soil structure
   - Green gram (Moong): Short duration (60-70 days), good market price ₹6,000-8,000/quintal
   - Black gram (Urad): Enriches soil, market price ₹7,000-9,000/quintal
   - Benefits: Reduces fertilizer cost by ₹2,000-3,000/acre, improves soil health

2. **Oilseeds**:
   - Groundnut: Suitable for red soil areas, market price ₹5,500-6,500/quintal
   - Sunflower: Short duration (90-100 days), drought tolerant
   - Soybean: Good for black soil, market demand high
   - Benefits: Good income, improves soil texture

3. **Vegetables (High Value)**:
   - Tomato: Market price ₹15-30/kg depending on season
   - Onion: Strong market demand, ₹20-40/kg
   - Cabbage, Cauliflower: Rabi season crops
   - Chili: Long shelf life, ₹80-150/kg
   - Benefits: Higher income per acre (₹80,000-150,000)

4. **Cereals**:
   - Wheat: Rabi season, market price ₹2,200-2,500/quintal
   - Jowar (Sorghum): Drought resistant, ₹2,800-3,200/quintal
   - Bajra (Pearl millet): Low water requirement
   - Benefits: Food security, stable market

5. **Fodder Crops**:
   - Lucerne (Alfalfa): Multiple cuts, ₹3-5/kg green fodder
   - Maize (for fodder): Quick growing
   - Benefits: Additional income if you have livestock

**Rotation Schedule for Pune:**
- Kharif (June-Oct): Soybean/Groundnut → Rabi (Nov-March): Wheat/Chickpea → Summer (April-May): Green gram/Vegetables
- OR: Kharif: Vegetables → Rabi: Pulses → Summer: Fodder

**Soil Benefits:**
- Pulses add nitrogen worth ₹2,000-3,000/acre
- Deep-rooted crops break hardpan
- Organic matter increases by 0.5-1%

**Water Requirements:**
- Low water: Pulses, Jowar, Bajra (2-3 irrigations)
- Medium: Wheat, Oilseeds (4-5 irrigations)
- High: Vegetables, Sugarcane (8-12 irrigations)

**Expected Income:**
- Pulses: ₹25,000-40,000/acre
- Vegetables: ₹80,000-150,000/acre
- Cereals: ₹30,000-50,000/acre

**Where to Buy Seeds:**
- Government seed stores (Krishi Kendra)
- Maharashtra State Seeds Corporation
- Private dealers (Mahyco, Nuziveedu)

---
💡 **Need More Help?** Ask about irrigation schedules, weather forecasts, or government schemes.

PUNE, MAHARASHTRA CONTEXT:
- Soil: Black soil (60%), Red soil (40%)
- Rainfall: 600-800mm annually
- Major crops: Sugarcane, wheat, jowar, vegetables
- Market: Pune has strong vegetable and pulse demand

REMEMBER: Always provide SPECIFIC crops, EXACT prices in ₹, and ACTIONABLE recommendations. Never just repeat the question."""

resource_optimizer_agent = Agent(
    model=BedrockModel(
        model_id=os.getenv("BEDROCK_MODEL_ID", "us.amazon.nova-pro-v1:0"),
        temperature=0.7,  # Increased for more creative recommendations
        max_tokens=2000  # Allow longer, detailed responses
    ),
    system_prompt=RESOURCE_OPTIMIZER_PROMPT,
    tools=[get_current_weather, get_weather_forecast]
)

if __name__ == "__main__":
    print("\n💧 Resource-Optimizer Agent 💧\n")
    response = resource_optimizer_agent("What is the weather forecast for Nashik, Maharashtra for the next 3 days? Should I irrigate my wheat field?")
    print(response)
