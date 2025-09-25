from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(
    base_url = "https://api.aimlapi.com/v1",
    api_key = os.getenv("DEMO_API_KEY")
)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
  "role": "user",
  "content": "hi im trying to talk to you"
}
    ],
    temperature=0.7,
    top_p=0.7,
    frequency_penalty=1,
    max_tokens=1536,
    top_k=50,
)

message = response.choices[0].message.content
print(f"Assistant: {message}")