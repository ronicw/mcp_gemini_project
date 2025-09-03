import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Create a client using your API key
client = genai.Client(api_key=os.environ["GOOGLE_API_KEY"])

# Generate content using the Gemini model
response = client.models.generate_content(
    model="gemini-2.5-pro",
    contents="Hello Gemini!"
)

# List models that support generateContent
# print("Models that support generateContent:\n")
# for model in client.models.list():
#     if "generateContent" in model.supported_actions:
#         print(f"- {model.name}")



