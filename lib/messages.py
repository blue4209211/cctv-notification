from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerUser, InputPeerChannel
from telethon import TelegramClient
import asyncio

from lib import config

event_loop = asyncio.new_event_loop()
asyncio.set_event_loop(event_loop)

client = TelegramClient(
    "session", config.telegram_api_id, config.telegram_api_hash, loop=event_loop
)
client.start()


async def send_message_async(frame, message):
    try:
        if message:
            await client.send_message("me", message)
        if frame:
            await client.send_file("me", frame)
    except Exception as e:
        print("got error while sending message", e)


def send_message(frame, message):
    event_loop.run_until_complete(send_message_async(frame, message))
