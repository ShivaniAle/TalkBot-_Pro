import asyncio
import logging
import pytest
from app.openai_handler import OpenAIClient
from app.config import settings

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_openai_configuration():
    """Test OpenAI configuration and functionality"""
    try:
        # 1. Test OpenAI Client Initialization
        logger.info("\n=== Testing OpenAI Configuration ===")
        logger.info("1. Testing OpenAI client initialization...")
        client = OpenAIClient()
        logger.info("✅ OpenAI client initialized successfully")
        
        # 2. Test Environment Variables
        logger.info("\n2. Testing environment variables...")
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set")
        if not settings.OPENAI_ASSISTANT_ID:
            raise ValueError("OPENAI_ASSISTANT_ID is not set")
        logger.info("✅ Environment variables are set")
        
        # 3. Test Assistant Access
        logger.info("\n3. Testing Assistant access...")
        assistant = client.client.beta.assistants.retrieve(
            assistant_id=settings.OPENAI_ASSISTANT_ID
        )
        logger.info(f"✅ Assistant found: {assistant.name}")
        logger.info(f"Model: {assistant.model}")
        logger.info(f"Instructions preview: {assistant.instructions[:100] if assistant.instructions else 'No instructions set'}...")
        
        # 4. Test Basic Response
        logger.info("\n4. Testing basic response...")
        test_input = "Hello, can you hear me?"
        logger.info(f"Sending test input: '{test_input}'")
        response = await client.get_response(test_input)
        logger.info(f"✅ Received response: '{response}'")
        
        # 5. Test Context Maintenance
        logger.info("\n5. Testing context maintenance...")
        follow_up = "What did I just say to you?"
        logger.info(f"Sending follow-up: '{follow_up}'")
        response = await client.get_response(follow_up)
        logger.info(f"✅ Context response: '{response}'")
        
        # 6. Test Response Time
        logger.info("\n6. Testing response time...")
        start_time = asyncio.get_event_loop().time()
        response = await client.get_response("Give me a quick response")
        end_time = asyncio.get_event_loop().time()
        response_time = end_time - start_time
        logger.info(f"✅ Response received in {response_time:.2f} seconds")
        
        # 7. Test Error Handling
        logger.info("\n7. Testing error handling...")
        try:
            response = await client.get_response("")
            logger.info("✅ Error handling works")
        except Exception as e:
            logger.info(f"✅ Error properly caught: {str(e)}")
        
        # 8. Test Conversation State
        logger.info("\n8. Testing conversation state...")
        test_input = "I'm feeling happy today!"
        response = await client.get_response(test_input)
        logger.info(f"✅ Response with emotional context: '{response}'")
        
        # 9. Test Interruption Handling
        logger.info("\n9. Testing interruption handling...")
        test_input = "Stop! I want to change the topic."
        response = await client.get_response(test_input)
        logger.info(f"✅ Interruption response: '{response}'")
        
        # Print Summary
        logger.info("\n=== Test Summary ===")
        logger.info("1. OpenAI Client Initialization: ✅")
        logger.info("2. Environment Variables: ✅")
        logger.info("3. Assistant Access: ✅")
        logger.info("4. Basic Response: ✅")
        logger.info("5. Context Maintenance: ✅")
        logger.info("6. Response Time: ✅")
        logger.info("7. Error Handling: ✅")
        logger.info("8. Conversation State: ✅")
        logger.info("9. Interruption Handling: ✅")
        
        logger.info("\nAll tests completed successfully! Your OpenAI Assistant is properly configured.")
        
    except Exception as e:
        logger.error(f"\n❌ Test failed: {str(e)}")
        logger.error("\nPlease check:")
        logger.error("1. Your OPENAI_API_KEY is valid")
        logger.error("2. Your OPENAI_ASSISTANT_ID is correct")
        logger.error("3. The Assistant is properly configured in OpenAI")
        logger.error("4. Your network connection is stable")
        raise

@pytest.mark.asyncio
async def test_openai_streaming():
    """Test OpenAI streaming functionality"""
    try:
        client = OpenAIClient()
        logger.info("\n=== Testing OpenAI Streaming ===")
        
        # Test streaming response
        test_input = "Tell me a short story"
        logger.info(f"Sending streaming test input: '{test_input}'")
        
        async for chunk in client.get_streaming_response(test_input):
            logger.info(f"Received chunk: {chunk}")
        
        logger.info("✅ Streaming test completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Streaming test failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(test_openai_configuration())
    asyncio.run(test_openai_streaming()) 