import os
from dotenv import load_dotenv
from google import genai

# 1. Load the API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY not found in environment.")
    exit(1)

# 2. Initialize the client
client = genai.Client(api_key=api_key)

print("Attempting to connect to the Gemini API...")

try:
    # 3. Send the simplest possible prompt to the most lightweight model
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents="Please reply with exactly one word: Success."
    )
    print(f"\nAPI Call Worked! Model replied with: {response.text}")

except Exception as e:
    print(f"\nAPI Call Failed. Error details:\n{e}")