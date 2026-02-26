import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROWQ_API_KEY")

client = Groq(api_key=api_key)

query= "What is your name ?"

completion= client.chat.completions.create(
    model = "openai/gpt-oss-120b",
    messages=[{"role": "user", "content": query}]
)

print(completion.choices)