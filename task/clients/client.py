from aidial_client import Dial, AsyncDial

from task.clients.base import BaseClient
from task.constants import API_KEY, DIAL_ENDPOINT
from aidial_client.types.chat.request_param import Message as DialMessage
from task.models.message import Message as LocalMessage  # Your message class
from task.models.role import Role

from typing import cast, List
from typing import cast, Sequence


class DialClient(BaseClient):

    def __init__(self, deployment_name: str):
        super().__init__(deployment_name)
        # TODO:
        # Documentation: https://pypi.org/project/aidial-client/ (here you can find how to create and use these clients)
        self.dial_client = Dial(api_key=API_KEY, base_url=DIAL_ENDPOINT)
        self.async_dial_client = AsyncDial(api_key=API_KEY, base_url=DIAL_ENDPOINT)

    def get_completion(self, messages: list[LocalMessage]) -> LocalMessage:
        # TODO:
        # 1. Create chat completions with client
        #    Hint: to unpack messages you can use the `to_dict()` method from Message object
        # 2. Get content from response, print it and return message with assistant role and content
        # 3. If choices are not present then raise Exception("No choices in response found")
        completion = self.dial_client.chat.completions.create(
            deployment_name=self._deployment_name,
            stream=False,
            messages=cast(List[DialMessage], [msg.to_dict() for msg in messages]),
            api_version="2024-02-15-preview",
        )
        print(completion)
        print("hello")
        return LocalMessage(role=Role.AI, content=completion.choices[0].message.content or "")
        #LocalMessage(role=Role.AI, content=completion.choices[0].message.content)

    async def stream_completion(self, messages: list[LocalMessage]) -> LocalMessage:
        # TODO:
        # 1. Create chat completions with async client
        #    Hint: don't forget to add `stream=True` in call.
        # 2. Create array with `contents` name (here we will collect all content chunks)
        # 3. Make async loop from `chunks` (from 1st step)
        # 4. Print content chunk and collect it contents array
        # 5. Print empty row `print()` (it will represent the end of streaming and in console we will print input from a new line)
        # 6. Return Message with assistant role and message collected content
        completion = await self.async_dial_client.chat.completions.create(
            deployment_name=self._deployment_name,
            stream=True,
            messages=cast(List[DialMessage], [msg.to_dict() for msg in messages]),
            api_version="2024-02-15-preview",
        )
        contents = []
        async for chunk in completion:
            contents.append(chunk.choices[0].delta.content or "")

        return LocalMessage(role=Role.AI, content=''.join(contents))
