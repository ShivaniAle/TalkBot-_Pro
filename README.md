# VoiceFlow AI

A smart voice assistant that can have natural conversations with users over the phone. It uses cutting-edge AI to understand and respond to what you say, making it feel like you're talking to a real person.

## Features

- **Voice Call Handling**: Seamless integration with Twilio for handling incoming calls
- **Real-time Speech Processing**: Advanced speech recognition and processing
- **AI-Powered Responses**: Intelligent conversation handling using OpenAI's Assistants API
- **Cloud Storage**: Secure storage of audio files in Google Cloud Storage
- **Text-to-Speech**: High-quality voice responses using Google Cloud Text-to-Speech
- **Extensible Architecture**: Modular design for easy extension and maintenance

## How It Works

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

## Setup

### 1. Set Up Your Environment
```bash
# Create a virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 2. Configure Your Settings
Create a `.env` file with your API keys:
```env
#OpenAI
OPENAI_API_KEY=your_openai_key
OPENAI_ASSISTANT_ID=your_assistant_id

#Twilio
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=your_phone_number

#GCP
GCP_PROJECT_ID=your_project_id
GCP_BUCKET_NAME=your_bucket_name
```

### 3. Run the Service
```bash
# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

### 4. Deploy to Cloud Run
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/your-project/voiceflow-ai
gcloud run deploy voiceflow-ai --image gcr.io/your-project/voiceflow-ai
```

### 5. Configure Google Cloud credentials:
      - Download your service key account key file
      - set the path in GOOGLE_APPLICATION_CREDENTIALS

## Running the Application

### 1. Start the server
```bash
Python run.py
```
### 2. Configure your Twilio Webhook:
   
## API Endpoints
 - GET /: Root endpoint
 - GET /health: Health check endpoint
 - POST /voice: Handle incoming voice calls
 - POST /speech: Handle speech results from Twilio

## Setting up ngrok
### 1.Download and install ngrok:
```bash
# For Windows (using Chocolatey)
choco install ngrok

# For macOS (using Homebrew)
brew install ngrok

```
### 2.Start ngrok to create a tunnel to your local server:
```bash
ngrok http 8000
```
### 3.Note the HTTPS URL provided by ngrok (e.g., https://abc123.ngrok.io)

## Configuring Twilio
### 1.Sign up for a Twilio account at twilio.com

### 2.Get your Twilio credentials:

 - Account SID
 - Auth Token
 - Phone Number
### 3.Configure your Twilio phone number:

- Go to the Twilio Console
- Navigate to Phone Numbers > Manage > Active Numbers
- Click on your phone number
- Under "Voice & Fax" > "A Call Comes In":
- Set the webhook URL to: https://your-ngrok-url/voice
- Set the HTTP method to: POST
- Under "Voice & Fax" > "Speech Recognition":
- Set the webhook URL to: https://your-ngrok-url/speech
- Set the HTTP method to: POST
### 4.Update your .env file with Twilio credentials:
```bash
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
```

##Testing the Setup
### 1.Start your application:
```bash
python run.py
```
### 2.Start ngrok in a separate terminal:
```bash
ngrok http 8000
```
### 3.Make a test call:

 - Call your Twilio phone number
 - You should hear the AI assistant's greeting
 - Speak your question
- The AI should respond through the call


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


