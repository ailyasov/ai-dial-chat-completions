import asyncio

from task.clients.custom_client import DialClient
from task.constants import DEFAULT_SYSTEM_PROMPT
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role


async def start(stream: bool) -> None:
    dial_client = DialClient(deployment_name="gpt-4o")
    custom_dial_client = DialClient(deployment_name="gpt-4o")
    conversation = Conversation()
    system_prompt = input("Provide System prompt or press 'enter' to continue.\n")
    if system_prompt.strip() == "":
        system_prompt = DEFAULT_SYSTEM_PROMPT
    conversation.add_message(Message(role=Role.SYSTEM, content=system_prompt))
    print("Type your question or 'exit' to quit.")
    while True:
        input_message = input("> ")
        if input_message == "exit":
            break
        conversation.add_message(Message(role=Role.USER, content=input_message))
        if stream:
            response = await dial_client.stream_completion(conversation.get_messages())
            conversation.add_message(response)
        else:
            response = dial_client.get_completion(conversation.get_messages())
            conversation.add_message(response)
        print()


asyncio.run(start(True))
