# Voice Agent

A sophisticated voice-based conversational AI agent built with Twilio and OpenAI's Assistants API, featuring advanced conversation management through Model Context Protocol (MCP).

## Features

- **Natural Phone Conversations**: Engage in fluid, natural-sounding phone conversations
- **Model Context Protocol (MCP)**: Advanced conversation state tracking and context management
- **Emotional Intelligence**: Detects and adapts to user's emotional tone and energy level
- **Context Awareness**: Maintains topic continuity and builds natural context connections
- **Enhanced Speech Recognition**: Optimized for phone call quality with improved accuracy
- **Real-time Response**: Quick and natural responses with proper phone call etiquette
- **Error Handling**: Robust error recovery and graceful fallbacks

## Technical Stack

1. Someone calls the phone number
2. The system greets them and asks them to speak
3. Their voice is recorded and converted to text
4. The AI understands what they said and generates a response
5. The response is played back to the caller
6. The conversation is saved for future reference

## Tech Stuff

### Main Technologies
- **FastAPI**: Makes the web server fast and reliable
- **Twilio**: Handles phone calls and voice processing
- **OpenAI**: Powers the AI conversation
- **Google Cloud**: Stores data and runs the service

### Required Tools
- Python 3.11 or newer
- Docker (for running the service)
- Google Cloud account
- Twilio account
- OpenAI API access
- **Backend**: Python with FastAPI
- **Voice Processing**: Twilio Voice API
- **AI**: OpenAI Assistants API with GPT-4
- **Conversation Management**: Custom Model Context Protocol (MCP)
- **Logging**: Comprehensive logging for debugging and monitoring





## Setup

1. **Environment Variables**
   ```bash
   TWILIO_ACCOUNT_SID=your_twilio_sid
   TWILIO_AUTH_TOKEN=your_twilio_token
   TWILIO_PHONE_NUMBER=your_twilio_phone
   OPENAI_API_KEY=your_openai_key
   OPENAI_ASSISTANT_ID=your_assistant_id
   ```

2. **Installation**
   ```bash
   pip install -r requirements.txt
   ```

3. **Running the Application**
   ```bash
   uvicorn app.main:app --reload
   ```

## Model Context Protocol (MCP)

The system implements a sophisticated MCP that tracks:

- **Emotional Tone**: Detects user's emotional state (positive, negative, neutral)
- **Energy Level**: Adapts to user's energy (high, medium, low)
- **Topic Tracking**: Maintains conversation context and topic continuity
- **Context Connections**: Builds natural bridges between conversation topics
- **Conversation History**: Manages recent interaction history

## Recent Improvements

- Enhanced emotional tone detection
- Improved energy level adaptation
- Better topic continuity
- More natural context connections
- Optimized speech recognition settings
- Reduced response timeouts
- Enhanced error handling
- Improved conversation flow

## Usage

1. Call your Twilio phone number
2. The system will greet you naturally
3. Speak naturally - the system will:
   - Detect your emotional tone
   - Match your energy level
   - Maintain topic context
   - Provide natural responses
   - Handle interruptions gracefully

## Development

To contribute or modify the system:

1. The main components are:
   - `app/main.py`: FastAPI application and routes
   - `app/twilio_handler.py`: Twilio voice handling
   - `app/openai_handler.py`: OpenAI integration and MCP implementation

2. Key features to modify:
   - Conversation flow in `handle_speech`
   - MCP implementation in `_update_conversation_state`
   - System context in `get_response`

## Troubleshooting

Common issues and solutions:

1. **No Response**
   - Check OpenAI API key and assistant ID
   - Verify Twilio credentials
   - Check logs for specific errors

2. **Poor Speech Recognition**
   - Ensure good phone connection
   - Speak clearly and naturally
   - Check Twilio speech settings

3. **Unnatural Responses**
   - Verify MCP state tracking
   - Check conversation history
   - Review system context

## License

MIT License - See LICENSE file for details

## Project Structure

```
voice_agent/
├── app/                      # Main application code
│   ├── main.py              # FastAPI application and endpoints
│   ├── twilio_handler.py    # Handles phone calls and voice processing
│   ├── openai_handler.py    # Manages AI conversations and responses
│   └── gcp_handler.py       # Handles cloud storage and file management
│
├── tests/                   # Test files
│   ├── test_main.py        # Tests for main application
│   ├── test_twilio.py      # Tests for Twilio integration
│   ├── test_openai.py      # Tests for OpenAI integration
│   └── test_gcp.py         # Tests for GCP integration
│
├── config/                  # Configuration files
│   ├── settings.py         # Application settings
│   └── logging.py          # Logging configuration
│
├── utils/                  # Utility functions
│   ├── audio_utils.py     # Audio processing helpers
│   └── storage_utils.py   # Cloud storage helpers
│
├── models/                # Data models
│   ├── audio.py          # Audio file models
│   └── conversation.py   # Conversation models
│
├── requirements.txt      # Python package dependencies
├── Dockerfile           # Container configuration
├── .env.example        # Example environment variables
├── .gitignore         # Git ignore rules
└── README.md         # Project documentation
```

### Key Components Explained

- **app/**: Contains the main application code
  - `main.py`: Entry point for the FastAPI application
  - `twilio_handler.py`: Manages phone calls and voice processing
  - `openai_handler.py`: Handles AI conversations
  - `gcp_handler.py`: Manages cloud storage

- **tests/**: Contains all test files
  - Separate test files for each component
  - Integration tests for the complete system

- **config/**: Configuration files
  - Settings for different environments
  - Logging configuration

- **utils/**: Helper functions
  - Audio processing utilities
  - Cloud storage utilities

- **models/**: Data structures
  - Audio file models
  - Conversation models

### Data Flow

```
User Call → Twilio → FastAPI → OpenAI → GCP Storage
   ↑           ↓         ↓         ↓         ↓
   └───────────┴─────────┴─────────┴─────────┘
          Response Flow & Storage
```


