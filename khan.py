import os
import asyncio
from fastapi import FastAPI, Request, Form, Query
from fastapi.responses import HTMLResponse, StreamingResponse
import httpx
from pyrogram import Client

app = FastAPI()

# Credentials from Environment Variables
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")

# Global client reference
tg_client = None

async def get_tg_client():
    """Safely initialize Pyrogram Client inside an active event loop."""
    global tg_client
    if tg_client is None:
        tg_client = Client(
            "tg_user_session",
            api_id=API_ID,
            api_hash=API_HASH,
            in_memory=True
        )
    return tg_client

HTML_HEAD = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram Bot</title>
    <style>
        body { font-family: system-ui, -apple-system, sans-serif; background: #0d1117; color: #c9d1d9; padding: 15px; margin: 0; }
        .container { max-width: 600px; margin: 0 auto; }
        .brand-logo { font-weight: bold; font-size: 20px; color: #58a6ff; margin-bottom: 15px; }
        .chat-frame { background: #161b22; border-radius: 8px; padding: 15px; border: 1px solid #30363d; margin-bottom: 15px; }
        .input-box { width: 100%; padding: 10px; margin: 8px 0; border-radius: 6px; border: 1px solid #30363d; background: #0d1117; color: #fff; box-sizing: border-box; }
        .btn { background: #238636; color: white; border: none; padding: 10px 15px; border-radius: 6px; cursor: pointer; width: 100%; font-weight: bold; }
        .btn:hover { background: #2ea043; }
        .status-card { border: 1px solid #30363d; border-radius: 6px; padding: 10px; margin-top: 10px; background: #161b22; }
    </style>
</head>
<body>
<div class="container">
<div class="brand-logo">Telegram Bot Web UI</div>
"""

HTML_FOOTER = """
</div>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def index():
    client = await get_tg_client()
    is_connected = client.is_connected if client else False

    content = f"""{HTML_HEAD}
    <div class="chat-frame">
        <h3>Status: {'Connected' if is_connected else 'Disconnected'}</h3>
        <form action="/send_phone" method="post">
            <label>Telegram Mobile Number (with +country code):</label>
            <input type="text" name="phone_number" class="input-box" placeholder="+91XXXXXXXXXX" required>
            <button type="submit" class="btn">Send OTP</button>
        </form>
    </div>
    {HTML_FOOTER}"""
    return HTMLResponse(content=content)

@app.post("/send_phone", response_class=HTMLResponse)
async def send_phone(phone_number: str = Form(...)):
    client = await get_tg_client()
    try:
        if not client.is_connected:
            await client.connect()
        
        sent_code = await client.send_code(phone_number)
        phone_code_hash = sent_code.phone_code_hash

        content = f"""{HTML_HEAD}
        <div class="chat-frame">
            <h3>Enter Verification Code</h3>
            <p>Sent OTP to: {phone_number}</p>
            <form action="/verify_otp" method="post">
                <input type="hidden" name="phone_number" value="{phone_number}">
                <input type="hidden" name="phone_code_hash" value="{phone_code_hash}">
                <input type="text" name="otp" class="input-box" placeholder="Enter OTP Code" required>
                <input type="password" name="password" class="input-box" placeholder="2FA Password (if enabled)">
                <button type="submit" class="btn">Verify & Login</button>
            </form>
        </div>
        {HTML_FOOTER}"""
        return HTMLResponse(content=content)
    except Exception as e:
        return HTMLResponse(content=f"{HTML_HEAD}<div class='chat-frame'><p style='color:red;'>Error: {str(e)}</p></div>{HTML_FOOTER}")

@app.post("/verify_otp", response_class=HTMLResponse)
async def verify_otp(
    phone_number: str = Form(...),
    phone_code_hash: str = Form(...),
    otp: str = Form(...),
    password: str = Form(None)
):
    client = await get_tg_client()
    try:
        try:
            await client.sign_in(phone_number, phone_code_hash, otp)
        except Exception as e:
            if "TWO_STEPS_VERIFICATION_REQUIRED" in str(e) and password:
                await client.check_password(password)
            else:
                raise e

        content = f"""{HTML_HEAD}
        <div class="chat-frame">
            <h3 style="color:#2ea043;">Login Successful!</h3>
            <p>Your Telegram session is active now.</p>
        </div>
        {HTML_FOOTER}"""
        return HTMLResponse(content=content)
    except Exception as e:
        return HTMLResponse(content=f"{HTML_HEAD}<div class='chat-frame'><p style='color:red;'>Login Error: {str(e)}</p></div>{HTML_FOOTER}")

@app.get("/stream_file")
async def stream_file(chat_id: str = Query(...), message_id: int = Query(...)):
    client = await get_tg_client()
    if not client.is_connected:
        await client.connect()

    try:
        msg = await client.get_messages(chat_id=int(chat_id), message_ids=message_id)
        if not msg or not msg.media:
            return HTMLResponse(content="Media not found", status_code=404)

        async def media_stream():
            async for chunk in client.stream_media(msg):
                yield chunk

        return StreamingResponse(media_stream(), media_type="application/octet-stream")
    except Exception as e:
        return HTMLResponse(content=f"Streaming Error: {str(e)}", status_code=500)
