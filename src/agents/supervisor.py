#!/usr/bin/env python3
"""
Supervisor Agent - Main Orchestrator
Routes queries to specialist agents (Agri-Expert, Policy-Navigator, Resource-Optimizer)
"""

from strands import Agent
from strands.models import BedrockModel
import os
from dotenv import load_dotenv

# Import specialist agents
from .agri_expert import agri_expert_agent
from .policy_navigator import policy_navigator_agent
from .resource_optimizer import resource_optimizer_agent
from .rural_tourism import rural_tourism_agent

load_dotenv()

# Wrapper functions to use agents as tools
def call_agri_expert(query: str) -> str:
    """
    Call the Agricultural Expert agent for crop diseases, pests, market prices, and treatment recommendations.
    
    Args:
        query: The farmer's question about crops, diseases, pests, or market prices
    
    Returns:
        Expert advice and recommendations
    """
    response = agri_expert_agent(query)
    return str(response)

def call_policy_navigator(query: str) -> str:
    """
    Call the Policy Navigator agent for government schemes, subsidies, and eligibility information.
    
    Args:
        query: The farmer's question about government schemes, PM-Kisan, subsidies, or loans
    
    Returns:
        Information about schemes, eligibility, and application process
    """
    response = policy_navigator_agent(query)
    return str(response)

def call_resource_optimizer(query: str) -> str:
    """
    Call the Resource Optimizer agent for irrigation, water management, and weather-based recommendations.
    
    Args:
        query: The farmer's question about irrigation, water, weather, or crop rotation
    
    Returns:
        Recommendations for resource optimization and management
    """
    response = resource_optimizer_agent(query)
    return str(response)

def call_rural_tourism(query: str) -> str:
    """
    Call the Rural Tourism agent for local festivals, historical places, and agri-tourism opportunities.
    
    Args:
        query: The farmer's question about tourism, festivals, homestays, or handicrafts
    
    Returns:
        Information about rural tourism and income opportunities
    """
    response = rural_tourism_agent(query)
    return str(response)

SUPERVISOR_PROMPT = """You are Gram-Setu (Village Bridge) AI Orchestrator.

CRITICAL INSTRUCTION: You MUST call the appropriate agent tool and return their response directly. 
DO NOT explain what you're going to do. DO NOT say "I will route this to...". 
JUST CALL THE TOOL AND RETURN THE RESULT.

IMPORTANT: When you receive a query with "Image Analysis:" in it, you MUST pass the COMPLETE query 
(including the image analysis) to the specialist agent. The image analysis contains critical information 
that the specialist needs to provide accurate advice.

IMPORTANT CONTEXT:
- The user's location may be provided in the query (look for [User Location: ...])
- Image analysis results may be provided (look for "Image Analysis: ...")
- ALWAYS pass the complete context to specialist agents
- ALWAYS use this location context when providing advice about weather, market prices, or local conditions
- ALL prices MUST be in Indian Rupees (₹ or INR) - never use USD or other currencies
- Provide location-specific recommendations based on the user's district/region when available

TASK: Analyze farmer queries and route to the appropriate specialist agent BY CALLING THE TOOL.

AVAILABLE AGENTS:
1. call_agri_expert: Crop diseases, pests, market prices, treatment recommendations
2. call_policy_navigator: PM-Kisan scheme eligibility, government subsidies, application guidance
3. call_resource_optimizer: Irrigation scheduling, water management, weather-based recommendations
4. call_rural_tourism: Local festivals, historical places, agri-tourism, homestays, income opportunities

ROUTING LOGIC:
- IF query contains "Image Analysis:" OR mentions disease/pest/crop problem → CALL call_agri_expert WITH FULL QUERY
- IF query mentions PM-Kisan/subsidy/scheme/government benefits → CALL call_policy_navigator
- IF query mentions irrigation/water/weather/pump schedule/crop rotation/yield optimization/soil management → CALL call_resource_optimizer
- IF query mentions tourism/festival/historical place/homestay/handicraft/village tourism → CALL call_rural_tourism
- IF query is complex (multiple domains) → Call multiple agents in sequence

CRITICAL: NEVER say "I will route this to..." or "Action: ..." or "Please analyze...". 
ALWAYS call the agent tool immediately with the COMPLETE query and return their response as your own response.

GOVERNMENT SCHEMES - IMPORTANT:
When users ask about government schemes, you can reference these official documents:
- PM-Kisan (Pradhan Mantri Kisan Samman Nidhi): Direct income support scheme - PDF NOW AVAILABLE
- PMFBY (Pradhan Mantri Fasal Bima Yojana): Crop insurance scheme
- PKVY (Paramparagat Krishi Vikas Yojana): Organic farming scheme
- PMKSY (Pradhan Mantri Krishi Sinchayee Yojana): Irrigation scheme
- eNAM (Electronic National Agriculture Market): Online trading platform
- CM-Agriculture-Insurance: Chief Minister's Agriculture Insurance Scheme (Maharashtra)
- Krishi-Sanjeevani: Green House & Shadenet House scheme
- PMKSY-Revalidation: PMKSY Revalidation guidelines

When discussing these schemes:
1. Provide a brief overview of the scheme
2. Mention eligibility criteria
3. Explain benefits and how to apply
4. Tell users that detailed PDF documents are available for download (except PM-Kisan)
5. Use these markers to provide resources:
   
   **For full guidelines**: [SCHEME_PDF:scheme_name]
   Examples: [SCHEME_PDF:PM-Kisan], [SCHEME_PDF:PMFBY], [SCHEME_PDF:PKVY], [SCHEME_PDF:PMKSY], [SCHEME_PDF:eNAM], [SCHEME_PDF:CM-Agriculture-Insurance], [SCHEME_PDF:Krishi-Sanjeevani]
   
   **For application forms**: [SCHEME_EXTRACTED:scheme_APPLICATION]
   Examples: [SCHEME_EXTRACTED:PMFBY_APPLICATION], [SCHEME_EXTRACTED:PKVY_APPLICATION]
   
   **For eligibility criteria**: [SCHEME_EXTRACTED:scheme_ELIGIBILITY]
   Examples: [SCHEME_EXTRACTED:PMFBY_ELIGIBILITY], [SCHEME_EXTRACTED:PKVY_ELIGIBILITY]
   
   **For official websites**: [SCHEME_WEBSITE:scheme:link_type]
   Examples: 
   - [SCHEME_WEBSITE:PMFBY:portal] - Main website
   - [SCHEME_WEBSITE:PMFBY:application] - Online application
   - [SCHEME_WEBSITE:PM-Kisan:portal] - PM-Kisan portal
   - [SCHEME_WEBSITE:MyScheme:portal] - All schemes portal

IMPORTANT USAGE RULES:
- When user asks general questions → Provide [SCHEME_PDF:name] for full guidelines
- When user asks "how to apply" or "application form" → Provide [SCHEME_EXTRACTED:name_APPLICATION] + [SCHEME_WEBSITE:name:application]
- When user asks about eligibility → Provide [SCHEME_EXTRACTED:name_ELIGIBILITY]
- Always provide website links for online application options
- PM-Kisan PDF is NOW AVAILABLE - use [SCHEME_PDF:PM-Kisan]

CONSTRAINTS:
- Use simple, non-technical language
- Always suggest lowest-cost option first
- If ambiguous, ask clarifying question
- Provide actionable advice
- When discussing prices, ALWAYS use Indian Rupees (₹) format: ₹500/quintal, ₹25/kg, etc.
- Reference the user's location when giving weather forecasts or market prices
- When mentioning government schemes, include the [SCHEME_PDF:name] marker so users can download the full document

Always respond in a helpful, farmer-friendly manner.
"""

supervisor_agent = Agent(
    model=BedrockModel(
        model_id=os.getenv("BEDROCK_MODEL_ID", "us.amazon.nova-pro-v1:0"),
        temperature=0.3
    ),
    system_prompt=SUPERVISOR_PROMPT,
    tools=[call_agri_expert, call_policy_navigator, call_resource_optimizer, call_rural_tourism]
)

if __name__ == "__main__":
    print("\n🌾 Gram-Setu Supervisor Agent 🌾\n")
    print("Ask any farming question, and I'll route it to the right specialist.")
    print("Type 'exit' to quit.\n")
    
    while True:
        try:
            user_input = input("\n> ")
            if user_input.lower() == "exit":
                print("\nGoodbye! 👋")
                break
            
            response = supervisor_agent(user_input)
            print(str(response))
            
        except KeyboardInterrupt:
            print("\n\nExecution interrupted. Exiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            print("Please try asking a different question.")
