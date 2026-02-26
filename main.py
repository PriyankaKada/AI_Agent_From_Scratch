import os
from groq import Groq
from dotenv import load_dotenv
import os
import json
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from a .env file (useful during development).
load_dotenv()

# API key for Groq client - make sure this variable name matches your .env file.
api_key = os.getenv("GROWQ_API_KEY")

# Create a Groq client instance using the API key from environment.
client = Groq(api_key=api_key)

# Example prompt (not used directly below, kept for reference)
query = "What is temperature in Berlin today?"

# Definition of a tool schema that we expose to the language model. This
# schema follows a simple structure describing the function name, its purpose,
# and what parameters it expects. The language model can return a tool call
# matching this schema to ask the executor to run the corresponding Python
# function.
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
    """Mock temperature lookup.

    Parameters:
        city: Name of the city to lookup.

    Returns:
        A string containing a mocked temperature value. In a real application
        this function would call an external weather API and return actual
        data (and probably a numeric type). This string-based return keeps
        the example simple for beginners.
    """
    # NOTE: This is a stub. Replace with a real API call for production use.
    if city.lower() == "berlin":
        return "72"
    if city.lower() == "london":
        return "75"
    if city.lower() == "tokyo":
        return "73"
    return "70"


class ToolExecutor:
    """Execute a chat loop that supports model-initiated tool calls.

    The `ToolExecutor` keeps a `messages` list (conversation history) which is
    sent to the Groq client's chat completions API. If the model's response
    includes `tool_calls`, the executor will try to find a matching Python
    function in `globals()` and run it, then append the tool output back into
    the conversation and continue the loop. When the model replies with no
    tool calls, the executor returns the assistant's final content.

    Attributes:
        client: An instance of `Groq` used to call the model.
        model: Model identifier string to use for completions.
        messages: Conversation history formatted as a list of role/content
                  dictionaries (system/user/assistant/tool).
        tools: List of tool schemas the model can use (informational only).
    """

    def __init__(self, client: Groq, model: str, system: str = "", tools: list | None = None) -> None:
        """Create a new ToolExecutor.

        Parameters:
            client: Groq client instance.
            model: Model name to request completions from.
            system: Optional system instruction to seed the conversation.
            tools: Optional list of tool schemas that describe callable tools.
        """
        self.client = client
        self.model = model
        self.messages: list = []
        self.tools = tools if tools is not None else []
        if system:
            # Add a system-level message that can instruct the assistant's behavior.
            self.messages.append({"role": "system", "content": system})

    def __call__(self, message: str = ""):
        """Send a user message and run the execution loop.

        If `message` is provided it is appended to the conversation and the
        executor runs until a final assistant response (without tool calls)
        is returned.
        """
        if message:
            self.messages.append({"role": "user", "content": message})

        # Run the loop that interacts with the model and handles tool calls.
        final_assistant_content = self.execute()

        if final_assistant_content:
            # Save the assistant's final reply into the messages history.
            self.messages.append({"role": "assistant", "content": final_assistant_content})
        return final_assistant_content

    def execute(self):
        """Core loop: ask the model for a completion and handle tool calls.

        Returns the assistant's final textual response after any tool
        executions. The loop continues whenever the model requests that a
        tool be run, so the model can perform multi-step interactions that
        require calling Python functions.
        """
        while True:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                tools=self.tools,
                tool_choice="auto",  # Let the model decide when to use tools
            )

            response_message = completion.choices[0].message

            # If the model asked to call one or more tools, execute them.
            if response_message.tool_calls:
                # Keep the tool call record in history so the model sees it.
                self.messages.append(response_message)

                tool_outputs = []
                for tool_call in response_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    # Default message if tool not available.
                    tool_output_content = f"Tool '{function_name}' not found."

                    # If a matching Python function exists in globals, call it.
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

                # Append tool outputs to the conversation and let the loop continue
                # so the model can react to the results of the tool execution.
                self.messages.extend(tool_outputs)
                continue

            # No tool calls requested, return the assistant's message content.
            return response_message.content


# Example usage: create an agent that can use the `get_temperature` tool.
query = "What is the temperature in Tokyo today?"

personal_agent = ToolExecutor(
    client=client,
    model="openai/gpt-oss-120b",
    system="You are a helpful assistant named Alex",
    tools=[weather_tool_schema],
)

response = personal_agent(query)
print("Messages", personal_agent.messages)
print("Response from Alex:", response)