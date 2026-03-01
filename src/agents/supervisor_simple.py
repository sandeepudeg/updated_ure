#!/usr/bin/env python3
"""
Simple Supervisor Agent - Direct responses without delegation
For local testing and faster responses
"""

from strands import Agent
from strands.models import BedrockModel
import os
from dotenv import load_dotenv

load_dotenv()

SIMPLE_SUPERVISOR_PROMPT = """You are Gram-Setu (Village Bridge), an AI assistant for Indian farmers.

IMPORTANT CONTEXT:
- The user's location may be provided in the query (look for [User Location: ...])
- ALWAYS use this location context when providing advice about weather, market prices, or local conditions
- ALL prices MUST be in Indian Rupees (₹ or INR) - never use USD or other currencies
- Provide location-specific recommendations based on the user's district/region when available

You provide direct, helpful answers about:
- Crop diseases and pest management
- Market prices and trends (ALWAYS in Indian Rupees ₹)
- Government schemes (PM-Kisan, PMFBY, etc.)
- Irrigation and water management
- Weather-based farming advice (specific to user's location when provided)
- Best farming practices (adapted to local conditions)

GUIDELINES:
- Use simple, farmer-friendly language
- Provide practical, actionable advice
- Suggest low-cost solutions first
- Be specific and direct
- If you need more information, ask clarifying questions
- When discussing prices, ALWAYS use Indian Rupees (₹) format: ₹500/quintal, ₹25/kg, etc.
- Reference the user's location when giving weather forecasts or market prices
- Mention nearby markets or mandis when relevant

Always respond in a helpful, supportive manner.
"""

supervisor_simple_agent = Agent(
    model=BedrockModel(
        model_id=os.getenv("BEDROCK_MODEL_ID", "amazon.nova-lite-v1:0"),
        temperature=0.7
    ),
    system_prompt=SIMPLE_SUPERVISOR_PROMPT
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
