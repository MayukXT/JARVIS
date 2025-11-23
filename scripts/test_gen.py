import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')

if not api_key:
    print("Error: GOOGLE_API_KEY not found.")
else:
    genai.configure(api_key=api_key)
    model_name = 'gemini-2.0-flash-lite'
    print(f"Testing generation with {model_name}...")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say hello")
        print(f"Success! Response: {response.text}")
    except Exception as e:
        print(f"Error generating content: {e}")
