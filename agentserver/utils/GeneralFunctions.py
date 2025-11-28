import asyncio
import time
from typing import List

from utils.QueueDict import QueueDict


async def async_generator(stream_content: list):
    for each_content in stream_content:
        await asyncio.sleep(0.01)
        yield each_content

def test_generator(stream_content: list):
    for each_content in stream_content:
        time.sleep(0.1)
        yield each_content


TOOL_CALL_S = '[TOOL_CALL]'
TOOL_CALL_E = ''
TOOL_RESULT_S = '[TOOL_RESPONSE]'
TOOL_RESULT_E = ''
THOUGHT_S = '[THINK]'
ANSWER_S = '[ANSWER]'
ASSISTANT = 'assistant'
FUNCTION = 'function'


def iterate_generator(stream_content, history: QueueDict=None, hist_key=None):
    reply = []
    response_plain_text = ''
    for reply in stream_content:
        full_text = ''
        content = []
        for msg in reply:
            if msg['role'] == ASSISTANT:
                if msg.get('reasoning_content'):
                    assert isinstance(msg['reasoning_content'], str), 'Now only supports text messages'
                    content.append(f'{THOUGHT_S}\n{msg["reasoning_content"]}')
                if msg.get('content'):
                    assert isinstance(msg['content'], str), 'Now only supports text messages'
                    content.append(f'{ANSWER_S}\n{msg["content"]}')
                if msg.get('function_call'):
                    content.append(f'{TOOL_CALL_S} {msg["function_call"]["name"]}\n{msg["function_call"]["arguments"]}')
            elif msg['role'] == FUNCTION:
                content.append(f'{TOOL_RESULT_S} {msg["name"]}\n{msg["content"]}')
            else:
                raise TypeError
        if content:
            full_text = '\n'.join(content)
            print(full_text[len(response_plain_text):], end='', flush=True)
            yield full_text[len(response_plain_text):]

        response_plain_text = full_text

    if history and hist_key:
        history.enqueue(hist_key, reply[-1])

