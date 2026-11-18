# from google import genai
# client = genai.Client()  # usa GEMINI_API_KEY / GOOGLE_API_KEY do ambiente
# for m in client.models.list():
#     print(m.name)

import os
from dotenv import load_dotenv
from groq import Groq
from openai import OpenAI

load_dotenv()
client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

response = client.responses.create(
    input="Explain the importance learning a second language.",
    model="openai/gpt-oss-120b",
)
print(response.output_text)

# client = OpenAI(
#     api_key=os.environ.get("GROQ_API_KEY"),
#     base_url="https://api.groq.com/openai/v1",
# )

# for model in client.models.list():
#     print(model.id)