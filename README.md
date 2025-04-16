# VoiceFlow AI

A sophisticated voice AI agent that handles phone calls and provides intelligent responses using OpenAI's Assistants API.

## Features

- **Voice Call Handling**: Seamless integration with Twilio for handling incoming calls
- **Real-time Speech Processing**: Advanced speech recognition and processing
- **AI-Powered Responses**: Intelligent conversation handling using OpenAI's Assistants API
- **Cloud Storage**: Secure storage of audio files in Google Cloud Storage
- **Text-to-Speech**: High-quality voice responses using Google Cloud Text-to-Speech
- **Extensible Architecture**: Modular design for easy extension and maintenance

## Project Structure

```
voice_agent/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── twilio_handler.py    # Twilio call handling
│   ├── openai_handler.py    # OpenAI API integration
│   ├── gcp_handler.py       # Google Cloud Platform services
│   ├── models/
│   │   ├── __init__.py
│   │   ├── audio.py         # Audio file models
│   │   └── conversation.py  # Conversation models
│   └── utils/
│       ├── __init__.py
│       ├── audio_utils.py   # Audio processing utilities
│       └── storage_utils.py # Cloud storage utilities
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_main.py
│   ├── test_twilio_handler.py
│   ├── test_openai_handler.py
│   ├── test_gcp_handler.py
│   ├── test_models.py
│   └── test_utils.py
├── requirements.txt
├── .env.example
└── run.py                   # Application runner
```

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/voiceflow-ai.git
   cd voiceflow-ai
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your API keys:
   ```env
   # OpenAI
   OPENAI_API_KEY=your_openai_api_key
   OPENAI_ASSISTANT_ID=your_assistant_id

   # Twilio
   TWILIO_ACCOUNT_SID=your_twilio_account_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   TWILIO_PHONE_NUMBER=your_twilio_phone_number

   # Google Cloud
   GCP_PROJECT_ID=your_gcp_project_id
   GCP_BUCKET_NAME=your_bucket_name
   GOOGLE_APPLICATION_CREDENTIALS=path_to_your_credentials.json

   # Application
   DEBUG=true
   HOST=0.0.0.0
   PORT=8000
   ```

5. Configure Google Cloud credentials:
   - Download your service account key file
   - Set the path in `GOOGLE_APPLICATION_CREDENTIALS`

## Running the Application

1. Start the server:
   ```bash
   python run.py
   ```

2. Configure your Twilio webhook:
   - Set the voice webhook URL to: `https://your-domain.com/voice`
   - Set the speech webhook URL to: `https://your-domain.com/speech`


### Testing

Run tests with pytest:
```bash
pytest
```

## API Endpoints

- `GET /`: Root endpoint
- `GET /health`: Health check endpoint
- `POST /voice`: Handle incoming voice calls
- `POST /speech`: Handle speech results from Twilio

## License

This project is licensed under the MIT License - see the LICENSE file for details.