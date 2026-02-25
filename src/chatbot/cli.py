import json
from conversation import Conversation
from utils.openai_client import get_openai_client
from chatbot.config import load_prompts
from core.settings import settings
from tool_definitions import tools
from tools import get_current_date, add_days_to_date

client = get_openai_client()
conversation = Conversation(system_prompt=load_prompts()["system"])

while True:
    user_input = input("User: ")
    conversation.user_message(user_input)

    response = client.chat.completions.create(
        model=settings.default_model,
        messages=conversation.get_messages(),
        tools=tools,
        tool_choice="auto",
    )

    message = response.choices[0].message

    if message.tool_calls:
        conversation.add_assistant_message_with_tool_calls(message)
        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            if function_name == "get_current_date":
                tool_result = get_current_date()
            elif function_name == "add_days_to_date":
                tool_result = add_days_to_date(arguments["date_str"], arguments["days"])
            else:
                tool_result = f"Error: unknown tool {function_name}"

            conversation.add_tool_result(tool_call.id, tool_result)

        response = client.chat.completions.create(
            model=settings.default_model,
            messages=conversation.get_messages(),
            tools=tools,
            tool_choice="auto",
        )
        assistant_reply = response.choices[0].message.content
        print(f"Assistant: {assistant_reply}")
        conversation.add_assistant_message(assistant_reply)

    else:
        assistant_reply = message.content
        print(f"Assistant: {assistant_reply}")
        conversation.add_assistant_message(assistant_reply)