import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()

# ✅ Configure Gemini API key
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))  

# ✅ Initialize the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
model_name = "gemini-2.0-flash-thinking-exp-01-21"
model_gemini = genai.GenerativeModel(model_name=model_name, generation_config=generation_config)