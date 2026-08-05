import asyncio
import os
from pyrogram import Client
from fastapi import FastAPI

# Python 3.14 के लिए Event Loop एरर फिक्स
try:
    asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# FastAPI App (Render को एक्टिव रखने के लिए)
app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Bot is running!"}

# आपका Pyrogram Client सेटअप (यहाँ अपने API credentials डालें)
API_ID = 1234567  # अपना API ID डालें
API_HASH = "your_api_hash"  # अपना API Hash डालें
BOT_TOKEN = "your_bot_token"  # अपना Bot Token डालें

bot = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# बोट स्टार्ट करने का सही तरीका
@app.on_event("startup")
async def start_bot():
    await bot.start()
    print("Bot Started Successfully!")

@app.on_event("shutdown")
async def stop_bot():
    await bot.stop()
    print("Bot Stopped!")
