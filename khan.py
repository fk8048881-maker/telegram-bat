import asyncio
import os
from pyrogram import Client
from fastapi import FastAPI

# Python 3.14 Event Loop Fix (इसे सबसे ऊपर रहना जरूरी है)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# FastAPI Setup (Render Web Service के लिए)
app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "Bot is running online!"}

# Telegram Bot Credentials (यहाँ अपनी सही जानकारी भरें)
API_ID = 1234567                # अपना API ID (संख्या) डालें
API_HASH = "your_api_hash"       # अपना API Hash डालें
BOT_TOKEN = "your_bot_token"     # अपना Bot Token डालें

# Pyrogram Client Setup
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
