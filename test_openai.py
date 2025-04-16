import openai
import os

# Set API key and project configuration
openai.api_key = "Your_API_KEY"
openai.api_base = "https://api.openai.com/v1"

try:
    # Test the connection with a simple completion
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello"}]
    )
    print("OpenAI connection successful!")
    print("Response:", response.choices[0].message.content)
except Exception as e:
    print("Error connecting to OpenAI:")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}") 