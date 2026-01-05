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
        self.dial_client = Dial(api_key=API_KEY, base_url=DIAL_ENDPOINT)
        self.async_dial_client = AsyncDial(api_key=API_KEY, base_url=DIAL_ENDPOINT)

    def get_completion(self, messages: list[LocalMessage]) -> LocalMessage:
        response = self.dial_client.chat.completions.create(
            deployment_name=self._deployment_name,
            stream=False,
            messages=cast(List[DialMessage], [msg.to_dict() for msg in messages]),
        )
        print(response)
        if not response.choices:
            raise Exception("No choices in response found")
        message = response.choices[0].message
        if message is None:
            raise Exception("No message in response found")
        return LocalMessage(role=Role.AI, content=message.content or "")

    async def stream_completion(self, messages: list[LocalMessage]) -> LocalMessage:
        completion = await self.async_dial_client.chat.completions.create(
            deployment_name=self._deployment_name,
            stream=True,
            messages=cast(List[DialMessage], [msg.to_dict() for msg in messages]),
        )
        contents = []
        async for chunk in completion:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    print(delta.content, end="", flush=True)
                    contents.append(delta.content)

        print()
        return LocalMessage(role=Role.AI, content="".join(contents))
