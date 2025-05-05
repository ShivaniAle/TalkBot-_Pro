import os
import logging
from openai import AsyncOpenAI
from app.config import settings
import json
import asyncio
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(self):
        """Initialize the OpenAI client"""
        try:
            logger.info("Initializing OpenAI client...")
            
            # Validate required settings
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY is not set in environment variables")
            
            # Initialize the OpenAI client
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            
            # Store conversation history and assistant
            self.conversation_history: Dict[str, Dict[str, Any]] = {}
            self.assistant = None
            self.active_runs: Dict[str, str] = {}  # Track active runs by thread_id
            self.thread_locks: Dict[str, asyncio.Lock] = {}  # Locks for each thread
            self.assistant_lock = asyncio.Lock()  # Lock for assistant initialization
            
            logger.info("OpenAI client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}", exc_info=True)
            raise

    async def _initialize_assistant(self):
        """Initialize the OpenAI assistant"""
        try:
            # Use lock to prevent multiple assistant creation
            async with self.assistant_lock:
                if self.assistant is not None:
                    return
                    
                # Create or retrieve the assistant
                assistant = await self.client.beta.assistants.create(
                    name="Voice Conversation Assistant",
                    instructions="""You are a friendly and engaging conversational AI assistant having a natural phone conversation. 
                    Your role is to maintain engaging, context-aware conversations with users.
                    
                    Important rules:
                    1. Maintain context from previous messages
                    2. Use natural conversational language
                    3. Show genuine interest in the conversation
                    4. Ask relevant follow-up questions
                    5. Use conversational fillers appropriately
                    6. Keep responses concise but engaging
                    7. Reference previous topics when relevant
                    8. Use a warm, friendly tone throughout
                    
                    When appropriate, use the available functions to enhance the conversation.""",
                    model="gpt-4-turbo-preview",
                    tools=[
                        {
                            "type": "function",
                            "function": {
                                "name": "get_user_preferences",
                                "description": "Get or update user preferences for the conversation",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "preference_type": {
                                            "type": "string",
                                            "enum": ["tone", "topics", "response_length"],
                                            "description": "Type of preference to get or update"
                                        },
                                        "value": {
                                            "type": "string",
                                            "description": "The preference value to set"
                                        }
                                    },
                                    "required": ["preference_type"]
                                }
                            }
                        },
                        {
                            "type": "function",
                            "function": {
                                "name": "analyze_conversation_sentiment",
                                "description": "Analyze the sentiment of the current conversation",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                        "text": {
                                            "type": "string",
                                            "description": "The text to analyze"
                                        }
                                    },
                                    "required": ["text"]
                                }
                            }
                        }
                    ]
                )
                
                self.assistant = assistant
                logger.info("OpenAI assistant initialized successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI assistant: {str(e)}", exc_info=True)
            raise

    async def _get_thread_lock(self, thread_id: str) -> asyncio.Lock:
        """Get or create a lock for a thread"""
        if thread_id not in self.thread_locks:
            self.thread_locks[thread_id] = asyncio.Lock()
        return self.thread_locks[thread_id]

    async def _cancel_active_run(self, thread_id: str) -> None:
        """Cancel an active run if it exists"""
        if thread_id in self.active_runs:
            try:
                run_id = self.active_runs[thread_id]
                await self.client.beta.threads.runs.cancel(
                    thread_id=thread_id,
                    run_id=run_id
                )
                logger.info(f"Cancelled active run {run_id} on thread {thread_id}")
            except Exception as e:
                logger.warning(f"Failed to cancel active run: {str(e)}")
            finally:
                self.active_runs.pop(thread_id, None)

    async def _wait_for_run_completion(self, thread_id: str, run_id: str) -> None:
        """Wait for a run to complete and handle any required actions"""
        try:
            while True:
                run_status = await self.client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run_id
                )
                
                if run_status.status == "completed":
                    break
                elif run_status.status == "requires_action":
                    # Handle function calls
                    await self._handle_function_calls(run_status, thread_id)
                elif run_status.status in ["failed", "cancelled", "expired"]:
                    raise Exception(f"Run failed with status: {run_status.status}")
                
                # Wait before checking again
                await asyncio.sleep(1)
        finally:
            # Always remove the run from active runs when done
            if thread_id in self.active_runs and self.active_runs[thread_id] == run_id:
                self.active_runs.pop(thread_id, None)

    async def get_response(self, user_input: str, conversation_context: dict = None) -> str:
        """Get AI response using the assistant"""
        try:
            logger.info(f"Getting response for: {user_input}")
            
            # Initialize assistant if not already done
            if self.assistant is None:
                await self._initialize_assistant()
            
            # Get or create conversation thread
            conversation_id = conversation_context.get("conversation_id", "default")
            if conversation_id not in self.conversation_history:
                thread = await self.client.beta.threads.create()
                self.conversation_history[conversation_id] = {
                    "thread_id": thread.id,
                    "messages": []
                }
            
            # Get thread ID and lock
            thread_id = self.conversation_history[conversation_id]["thread_id"]
            thread_lock = await self._get_thread_lock(thread_id)
            
            # Use lock to prevent concurrent runs
            async with thread_lock:
                # Cancel any active run
                await self._cancel_active_run(thread_id)
                
                # Add user message to thread
                await self.client.beta.threads.messages.create(
                    thread_id=thread_id,
                    role="user",
                    content=user_input
                )
                
                # Create new run
                run = await self.client.beta.threads.runs.create(
                    thread_id=thread_id,
                    assistant_id=self.assistant.id
                )
                
                # Track the active run
                self.active_runs[thread_id] = run.id
                
                # Wait for run completion
                await self._wait_for_run_completion(thread_id, run.id)
                
                # Get the assistant's response
                messages = await self.client.beta.threads.messages.list(thread_id=thread_id)
                assistant_message = messages.data[0].content[0].text.value
                
                # Store the conversation
                self.conversation_history[conversation_id]["messages"].append({
                    "role": "user",
                    "content": user_input
                })
                self.conversation_history[conversation_id]["messages"].append({
                    "role": "assistant",
                    "content": assistant_message
                })
                
                logger.info(f"Generated response: {assistant_message}")
                
                return assistant_message
            
        except Exception as e:
            logger.error(f"Error getting response: {str(e)}", exc_info=True)
            return "I'm having trouble processing that. Could you please try again?"

    async def _handle_function_calls(self, run_status, thread_id):
        """Handle function calls from the assistant"""
        try:
            required_actions = run_status.required_action.submit_tool_outputs.tool_calls
            
            tool_outputs = []
            for action in required_actions:
                function_name = action.function.name
                arguments = json.loads(action.function.arguments)
                
                if function_name == "get_user_preferences":
                    # Implement preference handling logic
                    result = {"status": "success", "preference": arguments}
                elif function_name == "analyze_conversation_sentiment":
                    # Implement sentiment analysis logic
                    result = {"sentiment": "positive", "confidence": 0.85}
                else:
                    result = {"error": "Unknown function"}
                
                tool_outputs.append({
                    "tool_call_id": action.id,
                    "output": json.dumps(result)
                })
            
            # Submit the function outputs
            await self.client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run_status.id,
                tool_outputs=tool_outputs
            )
            
        except Exception as e:
            logger.error(f"Error handling function calls: {str(e)}", exc_info=True)
            raise

    def set_interrupted(self, interrupted: bool = True):
        """Set interruption flag"""
        self.interrupted = interrupted 