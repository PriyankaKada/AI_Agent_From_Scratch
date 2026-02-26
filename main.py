import os
from groq import Groq
from dotenv import load_dotenv
import json 

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

class ToolExecutor:
    def __init__(self, client: Groq, model: str, system: str = "", tools: list | None = None) -> None:
        self.client = client
        self.model = model
        self.messages: list = []
        self.tools = tools if tools is not None else []
        if system:
            self.messages.append({"role": "system", "content": system})

    def __call__(self, message: str= ""):
        if message:
            self.messages.append({"role": "user", "content": message})
        final_assistant_content = self.execute()
        if final_assistant_content:
            self.messages.append({"role": "assistant", "content": final_assistant_content})
        return final_assistant_content

    def execute(self):
        while True:
            completion = self.client.chat.completions.create(
                model = self.model,
                messages = self.messages,
                tools = self.tools,
                tool_choice = "auto" #Let the model decide when to use tools
            )

            response_message = completion.choices[0].message

            if response_message.tool_calls:
                self.messages.append(response_message)

                tool_outputs = []
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    tool_output_content = f"Tool '{function_name}' not found."
                    if function_name in globals() and callable(globals()[function_name]):
                        function_to_call = globals()[function_name]
                        executed_output = function_to_call(**function_args)
                        tool_output_content = str(executed_output)

                    tool_outputs.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": tool_output_content,
                        }
                    )

                self.messages.extend(tool_outputs)
                continue

            return response_message.content
        
query = "What is the temperature in Tokyo today?"

personal_agent = ToolExecutor(
    client = client,
    model = "openai/gpt-oss-120b",
    system = "You are a helpful assistant named Alex",
    tools = [weather_tool_schema]
)

response = personal_agent(query)
print("Messages", personal_agent.messages)
print("Response from Alex: ", response)