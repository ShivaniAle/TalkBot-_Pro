# Voice AI Agent

A conversational AI voice agent built with OpenAI Assistants SDK, Twilio, and Google Cloud Platform.

## Features

- Voice input handling via Twilio
- Real-time transcription using Google Cloud Speech-to-Text
- Conversational responses using OpenAI Assistants
- Audio file storage in Google Cloud Storage
- Extensible architecture for adding new tools and agents

## Project Structure

```
voice_agent/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── twilio_handler.py    # Twilio webhook handling
│   ├── openai_handler.py    # OpenAI integration
│   ├── gcp_handler.py       # Google Cloud Platform services
│   ├── models/              # Data models
│   │   ├── __init__.py
│   │   ├── conversation.py
│   │   └── audio.py
│   └── utils/               # Utility functions
│       ├── __init__.py
│       ├── audio_utils.py
│       └── storage_utils.py
├── tests/                   # Test files
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
└── README.md               # Project documentation
```

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables in `.env`:
   ```
   OPENAI_API_KEY=your_openai_api_key
   TWILIO_ACCOUNT_SID=your_twilio_account_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   GCP_PROJECT_ID=your_gcp_project_id
   GCP_BUCKET_NAME=your_gcs_bucket_name
   ```
4. Set up Google Cloud credentials:
   - Download service account key file
   - Set GOOGLE_APPLICATION_CREDENTIALS environment variable

## Running the Application

1. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload
   ```
2. Configure Twilio webhook URL to point to your server's `/twilio/voice` endpoint

## Development

- Use `black` for code formatting
- Use `isort` for import sorting
- Use `mypy` for type checking
- Run tests with `pytest`

app/main.py: The main FastAPI application with routes and middleware setup
app/config.py: Configuration management using Pydantic settings
app/twilio_handler.py: Handles Twilio voice interactions and webhooks
app/openai_handler.py: Manages interactions with OpenAI's API
app/gcp_handler.py: Handles Google Cloud Platform services
app/models/audio.py: Data model for audio files
app/models/conversation.py: Data model for conversation management
app/utils/audio_utils.py: Utility functions for audio processing
app/utils/storage_utils.py: Utility functions for storage operations
requirements.txt: Project dependencies with specific versions