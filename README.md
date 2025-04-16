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


### Setting up ngrok

1. Download and install ngrok:
   ```bash
   # For Windows (using Chocolatey)
   choco install ngrok

   # For macOS (using Homebrew)
   brew install ngrok

   # For Linux
   sudo snap install ngrok
   ```

2. Start ngrok to create a tunnel to your local server:
   ```bash
   ngrok http 8000
   ```

3. Note the HTTPS URL provided by ngrok (e.g., `https://abc123.ngrok.io`)

### Configuring Twilio

1. Sign up for a Twilio account at [twilio.com](https://www.twilio.com)

2. Get your Twilio credentials:
   - Account SID
   - Auth Token
   - Phone Number

3. Configure your Twilio phone number:
   - Go to the [Twilio Console](https://console.twilio.com)
   - Navigate to Phone Numbers > Manage > Active Numbers
   - Click on your phone number
   - Under "Voice & Fax" > "A Call Comes In":
     - Set the webhook URL to: `https://your-ngrok-url/voice`
     - Set the HTTP method to: `POST`
   - Under "Voice & Fax" > "Speech Recognition":
     - Set the webhook URL to: `https://your-ngrok-url/speech`
     - Set the HTTP method to: `POST`

4. Update your `.env` file with Twilio credentials:
   ```env
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_PHONE_NUMBER=your_twilio_phone_number
   ```

### Testing the Setup

1. Start your application:
   ```bash
   python run.py
   ```

2. Start ngrok in a separate terminal:
   ```bash
   ngrok http 8000
   ```

3. Make a test call:
   - Call your Twilio phone number
   - You should hear the AI assistant's greeting
   - Speak your question
   - The AI should respond through the call

### Troubleshooting

If you encounter issues:

1. **ngrok Connection Issues**:
   - Ensure your local server is running on port 8000
   - Check that ngrok is properly installed and running
   - Verify the ngrok URL is accessible

2. **Twilio Webhook Issues**:
   - Verify the webhook URLs in Twilio console match your ngrok URL
   - Check that both `/voice` and `/speech` endpoints are properly configured
   - Ensure your Twilio credentials are correct in the `.env` file

3. **Call Handling Issues**:
   - Check the application logs for errors
   - Verify that your OpenAI API key and assistant ID are correctly set
   - Ensure your Google Cloud credentials are properly configured