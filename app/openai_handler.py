from openai import OpenAI
import os
import logging
from dotenv import load_dotenv
from app.config import settings
from typing import Optional, AsyncGenerator
import asyncio
from typing import AsyncIterator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(self):
        """Initialize OpenAI client with enhanced conversation settings"""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.assistant_id = settings.OPENAI_ASSISTANT_ID
        self.threads = {}
        self.conversation_states = {}
        
        # Enhanced system context for more natural conversation
        self.system_context = """You are a friendly, conversational AI assistant having a natural phone conversation. 
        Your responses should be:
        1. Brief and conversational - use short sentences and natural pauses
        2. Interactive - ask follow-up questions and show genuine interest
        3. Emotionally aware - match the user's tone and energy level
        4. Natural - use conversational fillers like "hmm", "well", "you know" appropriately
        5. Responsive - acknowledge what the user says before responding
        6. Engaging - maintain a back-and-forth dialogue
        7. Personal - use "I" statements and share brief personal insights
        8. Dynamic - vary your response length and style based on the conversation flow
        
        Keep responses under 2-3 sentences to allow for natural conversation flow.
        Use natural pauses and conversational markers to indicate when you're thinking or transitioning.
        Show active listening by acknowledging what the user said before responding.
        Match the user's energy level and emotional tone.
        Ask relevant follow-up questions to keep the conversation flowing.
        Use natural speech patterns and avoid sounding robotic or scripted."""

    async def get_response(self, user_input: str, phone_number: str = None) -> str:
        """Get AI response with enhanced conversation handling"""
        try:
            if not phone_number:
                phone_number = "default"
            
            # Get or create thread
            thread_id = self.threads.get(phone_number)
            if not thread_id:
                thread = self.client.beta.threads.create()
                thread_id = thread.id
                self.threads[phone_number] = thread_id
                self.conversation_states[phone_number] = {
                    "emotional_tone": "neutral",
                    "energy_level": "medium",
                    "current_topic": None,
                    "conversation_history": []
                }
            
            # Update conversation state
            self._update_conversation_state(phone_number, user_input)
            
            # Add user message to thread
            self.client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=user_input
            )
            
            # Get current conversation state
            state = self.conversation_states[phone_number]
            
            # Create run with enhanced context
            run = self.client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=self.assistant_id,
                instructions=f"""Current conversation state:
                - Emotional tone: {state['emotional_tone']}
                - Energy level: {state['energy_level']}
                - Current topic: {state['current_topic']}
                - Recent history: {state['conversation_history'][-3:] if state['conversation_history'] else 'None'}
                
                {self.system_context}
                
                Keep your response brief and conversational. Use natural pauses and acknowledgments.
                Show you're listening and maintain a natural back-and-forth flow."""
            )
            
            # Wait for completion
            while True:
                run_status = self.client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )
                if run_status.status == "completed":
                    break
                elif run_status.status in ["failed", "cancelled", "expired"]:
                    raise Exception(f"Run failed with status: {run_status.status}")
                await asyncio.sleep(1)
            
            # Get messages
            messages = self.client.beta.threads.messages.list(thread_id=thread_id)
            assistant_messages = [msg for msg in messages if msg.role == "assistant"]
            
            if not assistant_messages:
                raise Exception("No response from assistant")
            
            # Get the latest assistant message
            response = assistant_messages[0].content[0].text.value
            
            # Add natural pauses and acknowledgments
            response = self._add_conversational_elements(response, state)
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting response: {str(e)}")
            return "I'm having trouble understanding. Could you please repeat that?"

    def _add_conversational_elements(self, response: str, state: dict) -> str:
        """Add natural conversational elements to the response"""
        # Add acknowledgment based on emotional tone
        if state['emotional_tone'] == 'excited':
            response = f"Wow! {response}"
        elif state['emotional_tone'] == 'concerned':
            response = f"Hmm, {response}"
        elif state['emotional_tone'] == 'curious':
            response = f"Interesting! {response}"
        
        # Add energy level markers
        if state['energy_level'] == 'high':
            response = response.replace('.', '!')
        elif state['energy_level'] == 'low':
            response = response.replace('.', '...')
        
        # Add natural pauses
        response = response.replace('. ', '. <break time="0.5s"/> ')
        response = response.replace('! ', '! <break time="0.3s"/> ')
        response = response.replace('? ', '? <break time="0.7s"/> ')
        
        return response

    def _format_for_voice(self, text: str) -> str:
        """Format text to be more suitable for voice output"""
        # Enhanced replacements for more natural speech
        replacements = {
            '...': ' ',
            'etc.': 'and so on',
            'e.g.': 'for example',
            'i.e.': 'that is',
            '&': 'and',
            '%': 'percent',
            '#': 'number',
            '@': 'at',
            '\n': ' ',
            '  ': ' ',
            '!': '. ',
            '?': '? ',
            '.': '. ',
            '**': '',
            '*': '',
            '_': '',
            '`': '',
            '>': '',
            '<': '',
            '[': '',
            ']': '',
            '(': '',
            ')': '',
            '{': '',
            '}': '',
            '|': '',
            '\\': '',
            '/': '',
            '"': '',
            "'": '',
            ';': '.',
            ':': '.',
            ',': '.',
            '...': '... ',
            '..': '. ',
            '  ': ' '
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Ensure the response is clear and concise
        text = text.strip()
        if len(text.split()) > 50:  # If response is too long, truncate it
            text = ' '.join(text.split()[:50]) + '...'
        
        return text

    async def get_streaming_response(self, user_input: str) -> AsyncIterator[str]:
        """Get streaming response from OpenAI"""
        try:
            logger.info("Starting streaming response from OpenAI")
            
            messages = self._prepare_conversation_context(user_input)
            
            # Create streaming response
            stream = await self.client.chat.completions.create(
                model="gpt-4",  # Using GPT-4 for better conversational abilities
                messages=messages,
                stream=True,
                temperature=0.9,  # Higher temperature for more creative responses
                max_tokens=150,   # Shorter responses for more natural conversation
                presence_penalty=0.6,
                frequency_penalty=0.6,
                top_p=0.9
            )
            
            collected_chunks = []
            collected_messages = []
            
            async for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    collected_chunks.append(content)
                    collected_messages.append(content)
                    # Yield each chunk for real-time processing
                    yield content
            
            # Store the complete message in conversation history
            full_response = ''.join(collected_messages)
            self._update_conversation_history(user_input, full_response)
            
        except Exception as e:
            logger.error(f"Error in streaming response: {str(e)}", exc_info=True)
            raise

    def _prepare_conversation_context(self, user_input: str) -> list:
        """Prepare conversation context with system message and history"""
        messages = [{
            "role": "system",
            "content": """You are a friendly and engaging conversational AI assistant. 
            Keep your responses concise and to the point.
            Respond directly to the question asked.
            Use simple, clear language.
            Be conversational but professional.
            If interrupted, stop your current response and address the new question."""
        }]
        
        # Add relevant conversation history (last 3 turns)
        messages.extend(self.conversation_history[-3:])
        
        # Add current user input
        messages.append({
            "role": "user",
            "content": user_input
        })
        
        return messages

    def _update_conversation_history(self, user_input: str, assistant_response: str):
        """Update conversation history with new messages"""
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_response
        })
        
        # Keep conversation history manageable (last 10 turns)
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]

    async def get_response_from_thread(self, user_input: str) -> str:
        """Get response from OpenAI assistant using a thread"""
        try:
            logger.info(f"Sending request to OpenAI: {user_input}")
            
            # Add user input to conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            
            # Create a thread
            thread = self.client.beta.threads.create()
            logger.info(f"Created thread: {thread.id}")
            
            # Add conversation history to thread
            for message in self.conversation_history:
                self.client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role=message["role"],
                    content=message["content"]
                )
            
            # Run the assistant with specific instructions
            run = self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=settings.OPENAI_ASSISTANT_ID,
                instructions="""You are a friendly and conversational AI assistant. 
                Keep your responses natural and engaging. 
                Use a warm, helpful tone and maintain context from previous messages.
                Keep responses concise but informative.
                If you're unsure about something, be honest about it.
                Use natural language patterns and occasional conversational fillers.
                Remember that you're speaking to someone, so be personable."""
            )
            logger.info(f"Created run: {run.id}")
            
            # Wait for completion
            while True:
                run_status = self.client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
                logger.info(f"Run status: {run_status.status}")
                
                if run_status.status == 'completed':
                    break
                elif run_status.status in ['failed', 'cancelled', 'expired']:
                    raise Exception(f"Run failed with status: {run_status.status}")
                
                # Wait before checking again
                import time
                time.sleep(1)
            
            # Get the assistant's response
            messages = self.client.beta.threads.messages.list(
                thread_id=thread.id
            )
            
            # Get the last assistant message
            assistant_messages = [msg for msg in messages.data if msg.role == "assistant"]
            if not assistant_messages:
                raise Exception("No response from assistant")
                
            response = assistant_messages[0].content[0].text.value
            logger.info(f"Received response from OpenAI: {response}")
            
            # Add assistant response to conversation history
            self.conversation_history.append({"role": "assistant", "content": response})
            
            # Keep conversation history manageable
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting OpenAI response: {str(e)}", exc_info=True)
            raise 

    def _update_conversation_state(self, phone_number: str, user_input: str) -> None:
        """Update conversation state based on user input"""
        try:
            # Get or create conversation state
            if phone_number not in self.conversation_states:
                self.conversation_states[phone_number] = {
                    "emotional_tone": "neutral",
                    "energy_level": "medium",
                    "current_topic": None,
                    "conversation_history": []
                }
            
            state = self.conversation_states[phone_number]
            
            # Analyze emotional tone from user input
            emotional_indicators = {
                "positive": ["happy", "great", "wonderful", "excited", "love", "enjoy"],
                "negative": ["sad", "angry", "frustrated", "upset", "disappointed"],
                "neutral": ["okay", "fine", "alright", "normal"]
            }
            
            # Detect emotional tone
            tone = "neutral"
            for word in user_input.lower().split():
                if word in emotional_indicators["positive"]:
                    tone = "positive"
                    break
                elif word in emotional_indicators["negative"]:
                    tone = "negative"
                    break
            
            # Update conversation state
            state["emotional_tone"] = tone
            
            # Detect energy level from input length and punctuation
            if len(user_input) > 50 or "!" in user_input:
                state["energy_level"] = "high"
            elif len(user_input) < 20:
                state["energy_level"] = "low"
            else:
                state["energy_level"] = "medium"
            
            # Update last interaction
            state["last_interaction"] = user_input
            
            # Extract potential topics
            topic_keywords = ["work", "family", "weather", "food", "travel", "music", "sports", "movies"]
            for keyword in topic_keywords:
                if keyword in user_input.lower():
                    state["current_topic"] = keyword
                    break
            
            # Build context connections
            if state["conversation_history"]:
                last_user_input = state["conversation_history"][-1]["user"]
                if any(word in last_user_input.lower() for word in user_input.lower().split()):
                    state["context_connections"] = state.get("context_connections", []) + [{
                        "from": last_user_input,
                        "to": user_input,
                        "connection_type": "topic_continuation"
                    }]
            
            logger.info(f"Updated conversation state: {state}")
            
        except Exception as e:
            logger.error(f"Error updating conversation state: {str(e)}")
            # Reset to default state on error
            self.conversation_states[phone_number] = {
                "emotional_tone": "neutral",
                "energy_level": "medium",
                "current_topic": None,
                "conversation_history": [],
                "context_connections": []
            } 