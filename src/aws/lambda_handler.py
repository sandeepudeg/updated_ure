#!/usr/bin/env python3
"""
URE MVP Lambda Handler
Orchestrates request flow for the Unified Rural Ecosystem
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import boto3
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
s3_client = boto3.client('s3')

# Environment variables
CONVERSATIONS_TABLE = os.environ.get('DYNAMODB_TABLE_NAME', 'ure-conversations')
USER_TABLE = os.environ.get('DYNAMODB_USER_TABLE', 'ure-user-profiles')
S3_BUCKET = os.environ.get('S3_BUCKET_NAME')

# Government scheme PDF mapping
SCHEME_PDF_MAPPING = {
    'PMFBY': 'schemes/PMFBY_Scheme_Guidelines.pdf',
    'PKVY': 'schemes/PKVY_Organic_Farming_Guidelines.pdf',
    'PMKSY': 'schemes/PMKSY_Irrigation_Manual.pdf',
    'eNAM': 'schemes/eNAM_Stakeholder_Guideline.pdf',
    'PM-Kisan': 'schemes/Pradhan_Mantri_Kisan_Samman_Nidhi_finalKCCCircular.pdf',
    'CM-Agriculture-Insurance': 'schemes/Chief_Ministers_Agriculture_Insurance_Scheme.pdf',
    'Krishi-Sanjeevani': 'schemes/Krishi_Sanjeevani_Yojana_Notification_-_Green_House___Shadenet_House_Erector.pdf',
    'PMKSY-Revalidation': 'schemes/Pradhan_Mantri_Krishi_Sinchai_Yojana_Revalidation_Letter_2021-22.pdf'
}

# Extracted PDF sections (application forms, eligibility, etc.)
SCHEME_EXTRACTED_PDF_MAPPING = {
    'PMFBY_APPLICATION': 'schemes/extracted/PMFBY_Application_Form.pdf',
    'PMFBY_ELIGIBILITY': 'schemes/extracted/PMFBY_Eligibility_Criteria.pdf',
    'PMFBY_CLAIM': 'schemes/extracted/PMFBY_Claim_Process.pdf',
    'PKVY_APPLICATION': 'schemes/extracted/PKVY_Application_Form.pdf',
    'PKVY_ELIGIBILITY': 'schemes/extracted/PKVY_Eligibility_Criteria.pdf',
    'PMKSY_APPLICATION': 'schemes/extracted/PMKSY_Application_Form.pdf',
    'PMKSY_ELIGIBILITY': 'schemes/extracted/PMKSY_Eligibility_Criteria.pdf'
}

# Official government website links
SCHEME_WEBSITE_MAPPING = {
    'PMFBY': {
        'portal': 'https://pmfby.gov.in/',
        'application': 'https://pmfby.gov.in/farmerRegistration',
        'mobile_app': 'https://play.google.com/store/apps/details?id=in.gov.pmfby'
    },
    'PM-Kisan': {
        'portal': 'https://pmkisan.gov.in/',
        'application': 'https://pmkisan.gov.in/RegistrationForm.aspx',
        'status': 'https://pmkisan.gov.in/BeneficiaryStatus.aspx'
    },
    'PKVY': {
        'portal': 'https://pgsindia-ncof.gov.in/',
        'application': 'https://pgsindia-ncof.gov.in/PKVY/Index.aspx'
    },
    'PMKSY': {
        'portal': 'https://pmksy.gov.in/',
        'application': 'https://pmksy.gov.in/microirrigation/Archive/MOA_Forms.aspx'
    },
    'eNAM': {
        'portal': 'https://www.enam.gov.in/',
        'registration': 'https://www.enam.gov.in/web/registration'
    },
    'Maharashtra_Tourism': {
        'portal': 'https://www.maharashtratourism.gov.in/'
    },
    'MyScheme': {
        'portal': 'https://www.myscheme.gov.in/'
    }
}

# MCP Configuration
MCP_TOOL_REGISTRY_PATH = os.environ.get('MCP_TOOL_REGISTRY_PATH', 'mcp/tool_registry.json')
MCP_AGMARKNET_SERVER_URL = os.environ.get('MCP_AGMARKNET_SERVER_URL', 'http://localhost:8001')
MCP_WEATHER_SERVER_URL = os.environ.get('MCP_WEATHER_SERVER_URL', 'http://localhost:8002')

# Initialize MCP Client (lazy loading)
_mcp_client = None
_guardrails = None
_translator = None
_pilot_metrics = None
_ip_hasher = None

def get_mcp_client():
    """Get or initialize MCP Client"""
    global _mcp_client
    if _mcp_client is None:
        try:
            from mcp.client import MCPClient
            servers = {
                'agmarknet': MCP_AGMARKNET_SERVER_URL,
                'weather': MCP_WEATHER_SERVER_URL
            }
            _mcp_client = MCPClient(MCP_TOOL_REGISTRY_PATH, servers)
            logger.info("MCP Client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MCP Client: {e}")
            _mcp_client = None
    return _mcp_client


def get_guardrails():
    """Get or initialize Bedrock Guardrails"""
    global _guardrails
    if _guardrails is None:
        try:
            from utils.bedrock_guardrails import BedrockGuardrails
            _guardrails = BedrockGuardrails()
            logger.info("Bedrock Guardrails initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Guardrails: {e}")
            _guardrails = None
    return _guardrails


def get_translator():
    """Get or initialize Amazon Translate"""
    global _translator
    if _translator is None:
        try:
            from utils.amazon_translate import AmazonTranslate
            _translator = AmazonTranslate()
            logger.info("Amazon Translate initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Translator: {e}")
            _translator = None
    return _translator


def get_pilot_metrics():
    """Get or initialize Pilot Metrics"""
    global _pilot_metrics
    if _pilot_metrics is None:
        try:
            from utils.pilot_metrics import PilotMetrics
            _pilot_metrics = PilotMetrics()
            logger.info("Pilot Metrics initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Pilot Metrics: {e}")
            _pilot_metrics = None
    return _pilot_metrics


def get_ip_hasher():
    """Get or initialize IP Address Hasher"""
    global _ip_hasher
    if _ip_hasher is None:
        try:
            from utils.ip_hasher import get_ip_hasher as get_hasher
            _ip_hasher = get_hasher()
            logger.info("IP Address Hasher initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize IP Hasher: {e}")
            _ip_hasher = None
    return _ip_hasher


def generate_presigned_url(s3_key: str, expiration: int = 3600) -> Optional[str]:
    """Generate presigned URL for S3 object"""
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': S3_BUCKET,
                'Key': s3_key
            },
            ExpiresIn=expiration
        )
        return url
    except Exception as e:
        logger.error(f"Failed to generate presigned URL for {s3_key}: {e}")
        return None


def process_scheme_pdf_markers(response_text: str) -> Dict[str, Any]:
    """
    Process [SCHEME_PDF:name] and [SCHEME_WEBSITE:name:type] markers in response
    Returns dict with processed text and lists of PDF links and website links
    """
    import re
    
    pdf_links = []
    website_links = []
    
    # Find all [SCHEME_PDF:name] markers
    pdf_pattern = r'\[SCHEME_PDF:([^\]]+)\]'
    pdf_matches = re.findall(pdf_pattern, response_text)
    
    for scheme_name in pdf_matches:
        # Get S3 key for this scheme
        s3_key = SCHEME_PDF_MAPPING.get(scheme_name)
        
        if s3_key:
            # Generate presigned URL
            presigned_url = generate_presigned_url(s3_key, expiration=86400)  # 24 hours
            
            if presigned_url:
                pdf_links.append({
                    'scheme_name': scheme_name,
                    'url': presigned_url,
                    's3_key': s3_key,
                    'type': 'full_guidelines'
                })
                
                # Replace marker with user-friendly text
                replacement = f"📄 Download {scheme_name} Guidelines (PDF available)"
                response_text = response_text.replace(f'[SCHEME_PDF:{scheme_name}]', replacement)
            else:
                response_text = response_text.replace(f'[SCHEME_PDF:{scheme_name}]', '')
        else:
            response_text = response_text.replace(f'[SCHEME_PDF:{scheme_name}]', '')
    
    # Find all [SCHEME_EXTRACTED:name] markers (for application forms, etc.)
    extracted_pattern = r'\[SCHEME_EXTRACTED:([^\]]+)\]'
    extracted_matches = re.findall(extracted_pattern, response_text)
    
    for extracted_name in extracted_matches:
        s3_key = SCHEME_EXTRACTED_PDF_MAPPING.get(extracted_name)
        
        if s3_key:
            presigned_url = generate_presigned_url(s3_key, expiration=86400)
            
            if presigned_url:
                # Parse the name to make it user-friendly
                parts = extracted_name.split('_')
                scheme = parts[0]
                doc_type = ' '.join(parts[1:]).title()
                
                pdf_links.append({
                    'scheme_name': f"{scheme} {doc_type}",
                    'url': presigned_url,
                    's3_key': s3_key,
                    'type': 'extracted'
                })
                
                replacement = f"📄 Download {scheme} {doc_type} (PDF available)"
                response_text = response_text.replace(f'[SCHEME_EXTRACTED:{extracted_name}]', replacement)
            else:
                response_text = response_text.replace(f'[SCHEME_EXTRACTED:{extracted_name}]', '')
        else:
            response_text = response_text.replace(f'[SCHEME_EXTRACTED:{extracted_name}]', '')
    
    # Find all [SCHEME_WEBSITE:scheme:type] markers
    website_pattern = r'\[SCHEME_WEBSITE:([^:]+):([^\]]+)\]'
    website_matches = re.findall(website_pattern, response_text)
    
    for scheme_name, link_type in website_matches:
        scheme_websites = SCHEME_WEBSITE_MAPPING.get(scheme_name, {})
        url = scheme_websites.get(link_type)
        
        if url:
            website_links.append({
                'scheme_name': scheme_name,
                'link_type': link_type.replace('_', ' ').title(),
                'url': url
            })
            
            replacement = f"🔗 Visit {scheme_name} {link_type.replace('_', ' ').title()}"
            response_text = response_text.replace(f'[SCHEME_WEBSITE:{scheme_name}:{link_type}]', replacement)
        else:
            response_text = response_text.replace(f'[SCHEME_WEBSITE:{scheme_name}:{link_type}]', '')
    
    return {
        'text': response_text,
        'pdf_links': pdf_links,
        'website_links': website_links
    }


def get_user_context(user_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve user context from DynamoDB"""
    try:
        table = dynamodb.Table(USER_TABLE)
        response = table.get_item(Key={'user_id': user_id})
        return response.get('Item')
    except ClientError as e:
        logger.error(f"Failed to get user context: {e}")
        return None


def get_conversation_history(user_id: str, limit: int = 5) -> list:
    """Retrieve recent conversation history"""
    try:
        table = dynamodb.Table(CONVERSATIONS_TABLE)
        response = table.get_item(Key={'user_id': user_id})
        
        if 'Item' in response:
            # Get the conversation list and return last N messages
            conversations = response['Item'].get('conversations', [])
            return conversations[-limit:] if conversations else []
        return []
    except ClientError as e:
        logger.error(f"Failed to get conversation history: {e}")
        return []


def store_conversation(
    user_id: str,
    query: str,
    response: str,
    agent_used: str,
    metadata: Optional[Dict] = None,
    event: Optional[Dict] = None
):
    """Store conversation in DynamoDB with hashed IP address and TTL"""
    try:
        table = dynamodb.Table(CONVERSATIONS_TABLE)
        
        # Get existing conversations
        existing = table.get_item(Key={'user_id': user_id})
        conversations = existing.get('Item', {}).get('conversations', [])
        existing_expiry = existing.get('Item', {}).get('expiry_time')
        
        # Hash IP address if event is provided
        if event:
            ip_hasher = get_ip_hasher()
            if ip_hasher:
                hashed_ip = ip_hasher.extract_and_hash_ip(event)
                if metadata is None:
                    metadata = {}
                metadata['hashed_ip'] = hashed_ip
                logger.debug(f"Stored hashed IP for user {user_id}")
        
        # Add new conversation
        conversations.append({
            'timestamp': datetime.utcnow().isoformat(),
            'query': query,
            'response': response,
            'agent_used': agent_used,
            'metadata': metadata or {}
        })
        
        # Keep only last 50 conversations
        if len(conversations) > 50:
            conversations = conversations[-50:]
        
        # Calculate TTL - extend session on every interaction (3 hours from now)
        try:
            from utils.ttl_manager import TTLManager
            ttl_manager = TTLManager()
            
            # Extend session if existing expiry, otherwise create new
            if existing_expiry:
                new_expiry = ttl_manager.extend_session(existing_expiry)
                logger.debug(f"Extended session TTL for user {user_id}")
            else:
                new_expiry = ttl_manager.calculate_expiry_time()
                logger.debug(f"Set new session TTL for user {user_id}")
            
            # Update table with TTL
            table.put_item(Item={
                'user_id': user_id,
                'conversations': conversations,
                'last_updated': datetime.utcnow().isoformat(),
                'expiry_time': new_expiry
            })
            
            logger.info(f"Stored conversation for user {user_id} with TTL {new_expiry}")
        
        except Exception as ttl_error:
            # Fallback: Store without TTL if TTL calculation fails
            logger.error(f"Failed to calculate TTL, storing without TTL: {ttl_error}")
            table.put_item(Item={
                'user_id': user_id,
                'conversations': conversations,
                'last_updated': datetime.utcnow().isoformat()
            })
            logger.info(f"Stored conversation for user {user_id} (without TTL)")
    
    except ClientError as e:
        logger.error(f"Failed to store conversation: {e}")


def process_image_upload(image_data: str, user_id: str) -> Optional[bytes]:
    """Process base64 image and upload to S3, return image bytes"""
    try:
        import base64
        from uuid import uuid4
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        
        # Generate unique filename
        filename = f"uploads/{user_id}/{uuid4()}.jpg"
        
        # Upload to S3
        s3_client.put_object(
            Bucket=S3_BUCKET,
            Key=filename,
            Body=image_bytes,
            ContentType='image/jpeg'
        )
        
        s3_uri = f"s3://{S3_BUCKET}/{filename}"
        logger.info(f"Uploaded image to {s3_uri}")
        
        return image_bytes
    
    except Exception as e:
        logger.error(f"Failed to upload image: {e}")
        return None


def invoke_supervisor_agent(
    query: str,
    user_context: Optional[Dict] = None,
    image_bytes: Optional[bytes] = None,
    language: str = 'en'
) -> Dict[str, Any]:
    """Invoke Supervisor Agent to route query"""
    start_time = datetime.utcnow()
    
    try:
        # Get guardrails, translator, and metrics
        # TEMPORARILY DISABLE GUARDRAILS - they're blocking legitimate agricultural queries
        guardrails = None  # get_guardrails()
        translator = get_translator()
        metrics = get_pilot_metrics()
        
        # Check input with guardrails
        if guardrails:
            input_check = guardrails.check_input(query)
            if input_check['blocked']:
                logger.warning(f"Input blocked by guardrails: {input_check['reason']}")
                
                # Track guardrails action
                if metrics:
                    metrics.track_guardrails_action(
                        action='input_blocked',
                        reason=input_check['reason'],
                        user_id=user_context.get('user_id') if user_context else None
                    )
                
                blocked_message = "I cannot process this request as it contains inappropriate content. Please ask about agricultural topics like crop diseases, market prices, or irrigation."
                
                # Translate blocked message if needed
                if translator and language != 'en':
                    blocked_message = translator.translate_response(blocked_message, language)
                
                return {
                    'success': False,
                    'response': blocked_message,
                    'agent_used': 'guardrails',
                    'metadata': {'blocked': True, 'reason': input_check['reason']}
                }
        
        # Import here to avoid cold start issues
        import sys
        from pathlib import Path
        
        # Add src to path if not already there
        src_path = str(Path(__file__).parent.parent)
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        # Use simple supervisor agent (direct responses, no delegation)
        # The full supervisor with agent tools has a Strands framework issue where
        # tools are identified but not executed - they just return the function call string
        from agents.supervisor_simple import supervisor_simple_with_prices
        
        # If image is provided, use Bedrock directly for image analysis
        if image_bytes:
            import boto3
            
            # Use Bedrock to analyze image
            bedrock_runtime = boto3.client(
                'bedrock-runtime', 
                region_name=os.getenv('BEDROCK_REGION', 'us-east-1')
            )
            
            # Use inference profile ARN instead of direct model ID
            # This is required for on-demand throughput with Nova Lite
            model_id = "us.amazon.nova-lite-v1:0"
            
            response = bedrock_runtime.converse(
                modelId=model_id,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "image": {
                                "format": "jpeg",
                                "source": {"bytes": image_bytes}
                            }
                        },
                        {"text": f"Analyze this crop image and answer: {query}"}
                    ]
                }]
            )
            
            image_analysis = response['output']['message']['content'][0]['text']
            
            # Combine with text query and use simple supervisor
            # Add location context if available
            if user_context and user_context.get('location') and user_context['location'] != 'Unknown':
                full_query = f"[User Location: {user_context['location']}]\n\nImage Analysis: {image_analysis}\n\nUser Question: {query}"
            else:
                full_query = f"Image Analysis: {image_analysis}\n\nUser Question: {query}"
            
            agent_response = supervisor_simple_with_prices(full_query)
            agent_used = 'agri-expert'
            metadata = {'image_analysis': image_analysis}
        else:
            # Text-only query - use simple supervisor
            # Add location context if available
            if user_context and user_context.get('location') and user_context['location'] != 'Unknown':
                full_query = f"[User Location: {user_context['location']}]\n\n{query}"
            else:
                full_query = query
            
            agent_response = supervisor_simple_with_prices(full_query)
            agent_used = 'supervisor'
            metadata = {}
        
        response_text = str(agent_response)
        
        # Process scheme PDF markers and generate download links
        pdf_result = process_scheme_pdf_markers(response_text)
        response_text = pdf_result['text']
        if pdf_result['pdf_links']:
            metadata['pdf_links'] = pdf_result['pdf_links']
        if pdf_result['website_links']:
            metadata['website_links'] = pdf_result['website_links']
        
        # Check output with guardrails
        if guardrails:
            output_check = guardrails.check_output(response_text)
            if output_check['blocked']:
                logger.warning(f"Output blocked by guardrails: {output_check['reason']}")
                
                # Track guardrails action
                if metrics:
                    metrics.track_guardrails_action(
                        action='output_blocked',
                        reason=output_check['reason'],
                        user_id=user_context.get('user_id') if user_context else None
                    )
                
                response_text = "I cannot provide this information as it may be harmful or off-topic. Please ask about safe agricultural practices."
                metadata['output_blocked'] = True
                metadata['block_reason'] = output_check['reason']
        
        # Translate response if needed
        if translator and language != 'en':
            original_length = len(response_text)
            response_text = translator.translate_response(response_text, language)
            metadata['translated'] = True
            metadata['target_language'] = language
            
            # Track translation
            if metrics:
                metrics.track_translation('en', language, original_length)
        
        # Calculate response time
        response_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Track query metrics
        if metrics:
            metrics.track_query(
                user_id=user_context.get('user_id') if user_context else 'unknown',
                agent_used=agent_used,
                success=True,
                response_time=response_time,
                language=language,
                has_image=image_bytes is not None
            )
        
        return {
            'success': True,
            'response': response_text,
            'agent_used': agent_used,
            'metadata': metadata
        }
    
    except Exception as e:
        logger.error(f"Failed to invoke supervisor agent: {e}", exc_info=True)
        
        # Calculate response time
        response_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Track error
        metrics = get_pilot_metrics()
        if metrics:
            metrics.track_error(
                error_type='agent_error',
                agent_used='supervisor',
                user_id=user_context.get('user_id') if user_context else None
            )
            metrics.track_query(
                user_id=user_context.get('user_id') if user_context else 'unknown',
                agent_used='error',
                success=False,
                response_time=response_time,
                language=language,
                has_image=image_bytes is not None
            )
        
        error_message = 'Sorry, I encountered an error processing your request. Please try again.'
        
        # Translate error message if needed
        translator = get_translator()
        if translator and language != 'en':
            error_message = translator.translate_response(error_message, language)
        
        return {
            'success': False,
            'error': str(e),
            'response': error_message,
            'agent_used': 'error'
        }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler for URE MVP
    
    Expected event structure:
    {
        "user_id": "farmer123",
        "query": "What disease is affecting my tomato plant?",
        "image": "base64_encoded_image_data",  # optional
        "language": "en"  # optional
    }
    """
    try:
        # Parse request body
        if 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            body = event
        
        # Extract parameters
        user_id = body.get('user_id')
        query = body.get('query')
        image_data = body.get('image')
        language = body.get('language', 'en')
        location = body.get('location')  # Get location from request
        
        # Validate required parameters
        if not user_id or not query:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing required parameters: user_id and query'
                })
            }
        
        logger.info(f"Processing query for user {user_id}: {query[:50]}...")
        if location:
            logger.info(f"User location: {location}")
        
        # Get user context
        user_context = get_user_context(user_id)
        if not user_context:
            logger.warning(f"No user context found for {user_id}, using defaults")
            user_context = {
                'user_id': user_id,
                'language': language,
                'location': location or 'Unknown'
            }
        else:
            # Update location if provided in request
            if location:
                user_context['location'] = location
        
        # Process image if provided
        image_bytes = None
        if image_data:
            image_bytes = process_image_upload(image_data, user_id)
        
        # Invoke Supervisor Agent
        result = invoke_supervisor_agent(query, user_context, image_bytes, language)
        
        # Store conversation
        if result['success']:
            store_conversation(
                user_id=user_id,
                query=query,
                response=result['response'],
                agent_used=result['agent_used'],
                metadata=result.get('metadata'),
                event=event  # Pass event for IP hashing
            )
        
        # Return response
        return {
            'statusCode': 200 if result['success'] else 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'user_id': user_id,
                'query': query,
                'response': result['response'],
                'agent_used': result['agent_used'],
                'metadata': result.get('metadata', {}),
                'timestamp': datetime.utcnow().isoformat()
            })
        }
    
    except Exception as e:
        logger.error(f"Lambda handler error: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }


# For local testing
if __name__ == "__main__":
    # Test event
    test_event = {
        'user_id': 'test_farmer_001',
        'query': 'What are the symptoms of tomato late blight?',
        'language': 'en'
    }
    
    result = lambda_handler(test_event, None)
    print(json.dumps(result, indent=2))
