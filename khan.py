import nest_asyncio
import asyncio
import os
from pyrogram import Client
from fastapi import FastAPI

# Python 3.14 + Pyrogram Event Loop Fix
nest_asyncio.apply()

try:
    asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# Render Web Service को एक्टिव रखने के लिए FastAPI Setup
app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Bot is running online!"}

# Telegram Bot Credentials (अपनी जानकारी यहाँ भरें)
API_ID = 1234567               # अपना API ID (Integer) यहाँ लिखें
API_HASH = "your_api_hash"      # अपना API Hash यहाँ लिखें
BOT_TOKEN = "your_bot_token"    # अपना Bot Token यहाँ लिखें

bot = Client(
    "my_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Startup & Shutdown Events
@app.on_event("startup")
async def start_bot():
    await bot.start()
    print("Bot Started Successfully!")

@app.on_event("shutdown")
async def stop_bot():
    await bot.stop()
    print("Bot Stopped!")
