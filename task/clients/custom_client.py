import json

import aiohttp
import requests

from task.constants import API_KEY, DIAL_ENDPOINT
from task.models.message import Message
from task.models.role import Role


class DialClient:
    _endpoint: str
    _api_key: str

    def __init__(self, deployment_name: str):
        # super().__init__(deployment_name)
        self._endpoint = (
            DIAL_ENDPOINT + f"/openai/deployments/{deployment_name}/chat/completions"
        )
        self._api_key = API_KEY

    def get_completion(self, messages: list[Message]) -> Message:
        # TODO:
        # Take a look at README.md of how the request and regular response are looks like!
        # 1. Create headers dict with api-key and Content-Type
        # 2. Create request_data dictionary with:
        #   - "messages": convert messages list to dict format using msg.to_dict() for each message
        # 3. Make POST request using requests.post() with:
        #   - URL: self._endpoint
        #   - headers: headers from step 1
        #   - json: request_data from step 2
        # 4. Get content from response, print it and return message with assistant role and content
        # 5. If status code != 200 then raise Exception with format: f"HTTP {response.status_code}: {response.text}"

        headers = {"api-key": self._api_key, "Content-Type": "application/json"}

        request_data = {"messages": [msg.to_dict() for msg in messages]}
        response = requests.post(url=self._endpoint, headers=headers, json=request_data)
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
        data = response.json()
        choices = data.get("choices")
        if not choices:
            raise Exception("No choices in response found")
        message = choices[0].get("message")
        if not message:
            raise Exception("No message in response found")
        content = message.get("content", "")
        print(content)
        return Message(role=Role.AI, content=content)

    async def stream_completion(self, messages: list[Message]) -> Message:
        # TODO:
        # Take a look at README.md of how the request and streamed response chunks are looks like!
        # 1. Create headers dict with api-key and Content-Type
        # 2. Create request_data dictionary with:
        #    - "stream": True  (enable streaming)
        #    - "messages": convert messages list to dict format using msg.to_dict() for each message
        # 3. Create empty list called 'contents' to store content snippets
        # 4. Create aiohttp.ClientSession() using 'async with' context manager
        # 5. Inside session, make POST request using session.post() with:
        #    - URL: self._endpoint
        #    - json: request_data from step 2
        #    - headers: headers from step 1
        #    - Use 'async with' context manager for response
        # 6. Get content from chunks (don't forget that chunk start with `data: `, final chunk is `data: [DONE]`), print
        #    chunks, collect them and return as assistant message
        headers = {"api-key": self._api_key, "Content-Type": "application/json"}
        request_data = {"stream": True, "messages": [msg.to_dict() for msg in messages]}
        contents = []

        def _get_content_snippet(line):
            content_chunk = None
            decoded_line = line.decode("utf-8").strip()
            if decoded_line.startswith("data: "):
                data = decoded_line[6:]
                if data == "[DONE]":
                    return None
                chunk = json.loads(data)
                choices = chunk.get("choices")
                if choices and len(choices) > 0:
                    delta = choices[0].get("delta", {})
                    content_chunk = delta.get("content", "")
            return content_chunk

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=self._endpoint, json=request_data, headers=headers
            ) as response:
                async for line in response.content:
                    content_chunk = _get_content_snippet(line)
                    if content_chunk is not None:
                        contents.append(content_chunk)
                        print(content_chunk, end="", flush=True)

        print()
        return Message(role=Role.AI, content="".join(contents))
