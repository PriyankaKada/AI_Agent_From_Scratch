import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROWQ_API_KEY")

client = Groq(api_key=api_key)

query= "What is temperature in Berlin today?"

weather_tool_schema = {
    "type": "function",
    "function": {
        "name": "get_temperature",
        "description": "Get the current temperature in a given city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city to get the temperature for.",
                }
            },
            "required": ["city"],
        },
    },
    
}


completion= client.chat.completions.create(
    model = "openai/gpt-oss-120b",
    messages=[{"role": "user", "content": query}],
    tools=[weather_tool_schema],
)

print(completion.choices)

def get_temperature(city: str) -> str:
    """Get the current temperature in a given city."""
    # Ideally it should call a weather API to get real/actual weather information
    if city.lower() == "berlin":
        return "72"
    if city.lower() == "london":
        return "75"
    if city.lower() == "tokyo":
        return "73"
    return "70"

