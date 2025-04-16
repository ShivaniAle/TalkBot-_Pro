import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
print(f"API Key loaded: {api_key is not None}")
if api_key:
    print(f"API Key length: {len(api_key)}") 