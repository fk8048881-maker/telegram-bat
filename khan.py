import os
from fastapi import FastAPI, Form, Header
from fastapi.responses import HTMLResponse, StreamingResponse, RedirectResponse
from pyrogram import Client
from pyrogram.errors import SessionPasswordNeeded

app = FastAPI()

# Credentials Render Environment Variables से ऑटो-रीड होंगे
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")

tg_client = None
auth_data = {}

HTML_HEAD = """
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #030712; color: #f1f5f9; padding-bottom: 70px; }
        .top-bar { display: flex; justify-content: space-between; align-items: center; padding: 16px; background: #0b132b; border-bottom: 1px solid #1d4ed844; position: sticky; top: 0; z-index: 100; }
        .brand-box { display: flex; align-items: center; gap: 10px; }
        .brand-logo { width: 40px; height: 40px; border-radius: 50%; background: #2563eb; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 18px; color: #fff; box-shadow: 0 0 12px #2563ebaa; }
        .brand-title { font-weight: 800; font-size: 20px; color: #3b82f6; letter-spacing: 0.5px; }
        .brand-sub { font-size: 11px; color: #93c5fd; }
        .section-header { padding: 16px 16px 12px 16px; font-size: 18px; font-weight: 700; color: #3b82f6; }
        .chat-list { padding: 0 16px; display: flex; flex-direction: column; gap: 10px; }
        .chat-item { background: #0f172a; border-radius: 12px; padding: 14px; text-decoration: none; color: white; border: 1px solid #1e40af44; display: flex; align-items: center; gap: 12px; }
        .chat-icon { width: 42px; height: 42px; border-radius: 50%; background: #1e3a8a; display: flex; align-items: center; justify-content: center; color: #60a5fa; font-size: 18px; flex-shrink: 0; }
        .chat-name { font-size: 14px; font-weight: 600; text-overflow: ellipsis; overflow: hidden; white-space: nowrap; color: #f1f5f9; }
        .auth-container { padding: 20px; display: flex; justify-content: center; margin-top: 30px; }
        .card { background: #0b132b; padding: 24px; border-radius: 16px; width: 100%; max-width: 380px; border: 1px solid #2563eb66; box-shadow: 0 0 25px #1d4ed833; }
        .card h2 { color: #3b82f6; text-align: center; margin-bottom: 12px; font-weight: 800; font-size: 24px; }
        .info-text { font-size: 12px; color: #94a3b8; line-height: 1.5; margin-bottom: 16px; text-align: center; }
        input { width: 100%; padding: 12px; margin: 8px 0; background: #030712; border: 1px solid #2563eb55; border-radius: 10px; color: #60a5fa; font-size: 14px; outline: none; }
        input::placeholder { color: #1d4ed8; }
        button, .btn { width: 100%; padding: 12px; background: #2563eb; color: #fff; border: none; border-radius: 10px; cursor: pointer; text-decoration: none; display: block; text-align: center; font-weight: 800; margin-top: 14px; box-shadow: 0 0 12px #2563eb55; }
        .btn-blue { background: #2563eb; color: #fff; border: none; padding: 8px 16px; border-radius: 20px; font-weight: 700; text-decoration: none; font-size: 13px; display: inline-flex; align-items: center; gap: 6px; }
        .error { background: #450a0a; color: #fca5a5; padding: 12px; border-radius: 8px; margin-bottom: 15px; text-align: center; font-size: 13px; border: 1px solid #ef444455; }
    </style>
</head>
"""

@app.get("/")
async def root():
    if tg_client and tg_client.is_connected:
        return RedirectResponse(url="/home")
    return RedirectResponse(url="/login")

@app.get("/login", response_class=HTMLResponse)
async def login_page():
    return f"""<!DOCTYPE html><html>{HTML_HEAD}<body>
    <div class="auth-container">
        <div class="card">
            <h2>TeleStream</h2>
            <div class="info-text">Apna Telegram Mobile Number daalein (+91 ke saath)</div>
            <form action="/send_otp" method="post">
                <input type="text" name="phone" placeholder="+91XXXXXXXXXX" required>
                <button type="submit">Send OTP</button>
            </form>
        </div>
    </div>
    </body></html>"""

@app.post("/send_otp", response_class=HTMLResponse)
async def send_otp(phone: str = Form(...)):
    global tg_client, auth_data
    clean_phone = phone.strip().replace(" ", "")
    if not clean_phone.startswith("+"):
        clean_phone = "+" + clean_phone

    try:
        if tg_client and tg_client.is_connected:
            await tg_client.disconnect()

        if os.path.exists("fk_session.session"):
            os.remove("fk_session.session")

        tg_client = Client(
            "fk_session",
            api_id=API_ID,
            api_hash=API_HASH,
            device_model="Android Web",
            system_version="Android 13",
            app_version="1.0"
        )

        await tg_client.connect()
        sent_code = await tg_client.send_code(clean_phone)
        
        auth_data["phone"] = clean_phone
        auth_data["hash"] = sent_code.phone_code_hash

        return f"""<!DOCTYPE html><html>{HTML_HEAD}<body>
        <div class="auth-container">
            <div class="card">
                <h2>Enter OTP</h2>
                <div class="info-text" style="color:#93c5fd;">OTP aapke Telegram App par bhej diya gaya hai.</div>
                <form action="/verify_otp" method="post">
                    <input type="text" name="code" placeholder="Enter OTP Code" required>
                    <input type="password" name="password" placeholder="2FA Password (If enabled)">
                    <button type="submit">Verify & Login</button>
                </form>
            </div>
        </div>
        </body></html>"""
    except Exception as e:
        return f"""<!DOCTYPE html><html>{HTML_HEAD}<body>
        <div class="auth-container"><div class="card">
            <div class="error">Error: {e}</div>
            <a href="/login" class="btn">Try Again</a>
        </div></div></body></html>"""

@app.post("/verify_otp")
async def verify_otp(code: str = Form(...), password: str = Form(None)):
    global tg_client, auth_data
    try:
        await tg_client.sign_in(
            phone_number=auth_data["phone"],
            phone_code_hash=auth_data["hash"],
            phone_code=code.strip()
        )
    except SessionPasswordNeeded:
        if password:
            await tg_client.check_password(password)
        else:
            return HTMLResponse(f"""<!DOCTYPE html><html>{HTML_HEAD}<body>
            <div class="auth-container"><div class="card">
                <div class="error">2FA Password Required!</div>
                <a href="/login" class="btn">Back to Start</a>
            </div></div></body></html>""")
    except Exception as e:
        return HTMLResponse(f"""<!DOCTYPE html><html>{HTML_HEAD}<body>
        <div class="auth-container"><div class="card">
            <div class="error">Error: {e}</div>
            <a href="/login" class="btn">Try Again</a>
        </div></div></body></html>""")

    return RedirectResponse(url="/home", status_code=303)

@app.get("/home", response_class=HTMLResponse)
async def home():
    if tg_client is None or not tg_client.is_connected:
        return RedirectResponse(url="/login")

    html = f"""<!DOCTYPE html><html>{HTML_HEAD}<body>
    <div class="top-bar">
        <div class="brand-box">
            <div class="brand-logo"><i class="fa-solid fa-play"></i></div>
            <div>
                <div class="brand-title">TELESTREAM</div>
                <div class="brand-sub">Telegram OTT Player</div>
            </div>
        </div>
    </div>
    <div class="section-header">Select a Chat</div>
    <div class="chat-list">
        <a href="/chat/me" class="chat-item">
            <div class="chat-icon"><i class="fa-solid fa-bookmark"></i></div>
            <div class="chat-name">Saved Messages</div>
        </a>
    """

    try:
        async for dialog in tg_client.get_dialogs(limit=30):
            try:
                if dialog.chat.is_self:
                    continue
                chat_title = dialog.chat.title or dialog.chat.first_name or f"Chat_{dialog.chat.id}"
                html += f"""
                <a href="/chat/{dialog.chat.id}" class="chat-item">
                    <div class="chat-icon"><i class="fa-solid fa-folder"></i></div>
                    <div class="chat-name">{chat_title}</div>
                </a>
                """
            except Exception:
                continue
    except Exception as e:
        html += f"<div class='error'>Failed to load chats: {e}</div>"

    html += '</div></body></html>'
    return html

@app.get("/chat/{chat_id}", response_class=HTMLResponse)
async def get_chat_videos(chat_id: str):
    if tg_client is None or not tg_client.is_connected:
        return RedirectResponse(url="/login")

    chat_target = "me" if chat_id == "me" else (int(chat_id) if chat_id.lstrip('-').isdigit() else chat_id)

    html = f"""<!DOCTYPE html><html>{HTML_HEAD}<body>
    <div class="top-bar">
        <div class="brand-box">
            <a href="/home" style="color:#3b82f6; font-size:20px; text-decoration:none; margin-right:10px;"><i class="fa-solid fa-arrow-left"></i></a>
            <div class="brand-title">Videos</div>
        </div>
    </div>
    <div style="padding:16px;">
    """
    
    count = 0
    try:
        async for msg in tg_client.get_chat_history(chat_target, limit=100):
            media = msg.video or msg.document
            if media:
                mime = getattr(media, "mime_type", "") or ""
                fname = getattr(media, "file_name", None) or f"Video_{msg.id}.mp4"
                if msg.video or "video" in mime or fname.lower().endswith(('.mp4', '.mkv', '.avi', '.webm')):
                    count += 1
                    intent_url = f"intent://127.0.0.1:10000/stream/{chat_id}/{msg.id}#Intent;scheme=http;type=video/*;end"
                    html += f"""
                    <div style="background:#0f172a; border-radius:12px; padding:12px; margin-bottom:12px; border:1px solid #1e40af44; display:flex; justify-content:space-between; align-items:center;">
                        <div style="width:60%;">
                            <div style="font-size:13px; font-weight:600; color:#fff; text-overflow:ellipsis; overflow:hidden; white-space:nowrap;">{fname}</div>
                        </div>
                        <a href="{intent_url}" class="btn-blue"><i class="fa-solid fa-play"></i> Play</a>
                    </div>
                    """
    except Exception as e:
        html += f"<div class='error'>Error loading videos: {e}</div>"

    if count == 0:
        html += "<p style='color:#93c5fd; text-align:center; padding:40px 0;'>Is chat mein koi video nahi mili!</p>"

    html += "</div></body></html>"
    return html

@app.get("/stream/{chat_id}/{message_id}")
async def stream_video(chat_id: str, message_id: int, range: str = Header(None)):
    if tg_client is None or not tg_client.is_connected:
        return HTMLResponse("Not logged in", status_code=401)

    chat_target = "me" if chat_id == "me" else (int(chat_id) if chat_id.lstrip('-').isdigit() else chat_id)

    try:
        msg = await tg_client.get_messages(chat_target, message_id)
        media = msg.video or msg.document if msg else None
        if not msg or not media:
            return HTMLResponse("Video not found", status_code=404)

        file_size = media.file_size
        chunk_size = 1024 * 1024

        start = 0
        end = file_size - 1
        status_code = 200

        if range:
            try:
                range_value = range.replace("bytes=", "").split("-")
                start = int(range_value[0]) if range_value[0] else 0
                end = int(range_value[1]) if len(range_value) > 1 and range_value[1] else file_size - 1
                status_code = 206
            except (ValueError, IndexError):
                start = 0
                end = file_size - 1

        offset_chunks = start // chunk_size
        first_chunk_cut = start % chunk_size

        async def video_generator():
            bytes_sent = 0
            total_needed = end - start + 1
            is_first = True
            async for chunk in tg_client.stream_media(msg, offset=offset_chunks):
                if is_first and first_chunk_cut:
                    chunk = chunk[first_chunk_cut:]
                    is_first = False
                remaining = total_needed - bytes_sent
                if remaining <= 0:
                    break
                if len(chunk) > remaining:
                    chunk = chunk[:remaining]
                bytes_sent += len(chunk)
                yield chunk

        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(end - start + 1),
        }

        return StreamingResponse(
            video_generator(),
            status_code=status_code,
            media_type="video/mp4",
            headers=headers,
        )
    except Exception as e:
        return HTMLResponse(f"Streaming error: {e}", status_code=500)
