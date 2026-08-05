import os
import uvicorn
from fastapi import FastAPI, Form, Header, Response
from fastapi.responses import HTMLResponse, StreamingResponse, RedirectResponse
from pyrogram import Client
from pyrogram.enums import ChatType
from pyrogram.errors import SessionPasswordNeeded, ApiIdInvalid

app = FastAPI()

tg_client = None
auth_data = {}

HTML_HEAD = """
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #050806; color: #e2e8f0; padding-bottom: 80px; }
        .top-bar { display: flex; justify-content: space-between; align-items: center; padding: 14px 16px; background: #0c140d; border-bottom: 1px solid #22c55e33; position: sticky; top: 0; z-index: 100; }
        .brand-title { font-weight: 900; font-size: 20px; color: #22c55e; letter-spacing: 0.5px; }
        
        .section-title { font-size: 18px; font-weight: 800; color: #ffffff; padding: 16px 16px 10px 16px; display: flex; justify-content: space-between; align-items: center; }
        
        .poster-row { display: flex; gap: 12px; overflow-x: auto; padding: 0 16px 10px 16px; scrollbar-width: none; }
        .poster-row::-webkit-scrollbar { display: none; }
        
        .poster-card { min-width: 130px; width: 130px; background: #0c140d; border-radius: 14px; overflow: hidden; position: relative; text-decoration: none; color: white; border: 1px solid #22c55e33; flex-shrink: 0; box-shadow: 0 4px 12px rgba(0,0,0,0.6); }
        .poster-img { width: 100%; height: 160px; object-fit: cover; background: #142416; display: block; }
        .badge { position: absolute; bottom: 36px; left: 8px; background: rgba(0,0,0,0.85); color: #22c55e; font-size: 9px; font-weight: 800; padding: 3px 6px; border-radius: 4px; text-transform: uppercase; border: 1px solid #22c55e44; }
        .card-name { padding: 8px; font-size: 12px; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; text-align: left; }

        .video-card { background: #0c140d; border-radius: 12px; padding: 12px; margin: 0 16px 10px 16px; border: 1px solid #22c55e33; display: flex; justify-content: space-between; align-items: center; }
        .btn-green { background: #22c55e; color: #000000; border: none; padding: 10px 18px; border-radius: 12px; font-weight: 800; text-decoration: none; font-size: 13px; display: inline-flex; align-items: center; justify-content: center; gap: 6px; cursor: pointer; }

        .bottom-nav { position: fixed; bottom: 0; left: 0; right: 0; background: #070d08; border-top: 1px solid #142416; display: flex; justify-around: space-around; padding: 10px 0; z-index: 1000; }
        .nav-item { color: #4b5563; text-decoration: none; display: flex; flex-direction: column; align-items: center; font-size: 10px; gap: 4px; font-weight: 600; }
        .nav-item.active { color: #22c55e; font-weight: 800; }

        .auth-container { padding: 20px; display: flex; justify-content: center; margin-top: 20px; }
        .card { background: #0c140d; padding: 24px; border-radius: 18px; width: 100%; max-width: 380px; border: 1px solid #22c55e44; box-shadow: 0 0 20px rgba(34, 197, 94, 0.08); }
        input { width: 100%; padding: 12px; margin: 8px 0; background: #040805; border: 1px solid #22c55e44; border-radius: 10px; color: #86efac; font-size: 14px; outline: none; }
        button { width: 100%; padding: 12px; background: #22c55e; color: #000000; border: none; border-radius: 10px; font-weight: 800; font-size: 15px; margin-top: 12px; cursor: pointer; }
        .error { background: #450a0a; color: #fca5a5; padding: 12px; border-radius: 8px; font-size: 13px; text-align: center; margin-bottom: 12px; border: 1px solid #ef444455; }

        /* Video Player Styling */
        .player-wrapper { width: 100%; max-width: 900px; margin: 0 auto; background: #000; position: relative; border-radius: 12px; overflow: hidden; border: 1px solid #22c55e33; box-shadow: 0 10px 30px rgba(0,0,0,0.9); }
        video { width: 100%; max-height: 70vh; display: block; outline: none; }
        .controls-panel { background: #0c140d; padding: 16px; border-radius: 12px; margin: 16px; border: 1px solid #22c55e33; display: flex; flex-wrap: wrap; gap: 12px; justify-content: space-between; align-items: center; }
        .select-box { background: #040805; color: #86efac; border: 1px solid #22c55e44; padding: 8px 12px; border-radius: 8px; font-size: 13px; outline: none; }
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
            <h2 style="color:#22c55e; text-align:center; margin-bottom:12px;">TeleStream Login</h2>
            <div style="font-size:12px; color:#86efac; text-align:center; margin-bottom:15px;">my.telegram.org se API ID & Hash enter karein</div>
            <form action="/send_otp" method="post">
                <input type="number" name="api_id" placeholder="API ID (Numbers only)" required>
                <input type="text" name="api_hash" placeholder="API Hash" required>
                <input type="text" name="phone" placeholder="Mobile Number (+91XXXXXXXXXX)" required>
                <button type="submit">Send OTP</button>
            </form>
        </div>
    </div>
    </body></html>"""

@app.post("/send_otp", response_class=HTMLResponse)
async def send_otp(phone: str = Form(...), api_id: str = Form(...), api_hash: str = Form(...)):
    global tg_client, auth_data
    clean_phone = phone.strip().replace(" ", "")
    if not clean_phone.startswith("+"):
        clean_phone = "+" + clean_phone

    try:
        parsed_api_id = int(api_id.strip())
        parsed_api_hash = api_hash.strip()

        if tg_client and tg_client.is_connected:
            await tg_client.disconnect()
            
        if os.path.exists("fk_session.session"):
            os.remove("fk_session.session")

        tg_client = Client("fk_session", api_id=parsed_api_id, api_hash=parsed_api_hash, device_model="Android Web", system_version="13", app_version="1.0")
        await tg_client.connect()
        sent_code = await tg_client.send_code(clean_phone)
        
        auth_data["phone"] = clean_phone
        auth_data["hash"] = sent_code.phone_code_hash

        return f"""<!DOCTYPE html><html>{HTML_HEAD}<body>
        <div class="auth-container"><div class="card">
            <h3 style="color:#22c55e; text-align:center; margin-bottom:10px;">Enter Telegram OTP</h3>
            <div style="font-size:12px; color:#86efac; text-align:center; margin-bottom:12px;">OTP Telegram App par bhej दिया गया है</div>
            <form action="/verify_otp" method="post">
                <input type="text" name="code" placeholder="Enter OTP Code" required>
                <input type="password" name="password" placeholder="2FA Password (If active)">
                <button type="submit">Verify & Login</button>
            </form>
        </div></div></body></html>"""
    except ApiIdInvalid:
        return f"""<!DOCTYPE html><html>{HTML_HEAD}<body><div class="auth-container"><div class="card"><div class="error">Invalid API ID or API Hash!</div><a href="/login" class="btn-green" style="display:block; text-align:center;">Go Back</a></div></div></body></html>"""
    except Exception as e:
        return f"""<!DOCTYPE html><html>{HTML_HEAD}<body><div class="auth-container"><div class="card"><div class="error">Error: {e}</div><a href="/login" class="btn-green" style="display:block; text-align:center;">Go Back</a></div></div></body></html>"""

@app.post("/verify_otp")
async def verify_otp(code: str = Form(...), password: str = Form(None)):
    global tg_client, auth_data
    try:
        await tg_client.sign_in(phone_number=auth_data["phone"], phone_code_hash=auth_data["hash"], phone_code=code.strip())
    except SessionPasswordNeeded:
        if password:
            await tg_client.check_password(password)
        else:
            return HTMLResponse(f"<!DOCTYPE html><html>{HTML_HEAD}<body><div class='auth-container'><div class='card'><div class='error'>2FA Password Required</div><a href='/login' class='btn-green' style='display:block; text-align:center;'>Go Back</a></div></div></body></html>")
    except Exception as e:
        return HTMLResponse(f"<!DOCTYPE html><html>{HTML_HEAD}<body><div class='auth-container'><div class='card'><div class='error'>{e}</div><a href='/login' class='btn-green' style='display:block; text-align:center;'>Go Back</a></div></div></body></html>")

    return RedirectResponse(url="/home", status_code=303)

@app.get("/chat_photo/{chat_id}")
async def get_chat_photo(chat_id: str):
    if not tg_client or not tg_client.is_connected:
        return Response(status_code=401)
    
    chat_target = "me" if chat_id == "me" else (int(chat_id) if chat_id.lstrip('-').isdigit() else chat_id)
    try:
        chat = await tg_client.get_chat(chat_target)
        if chat.photo:
            photo_bytes = await tg_client.download_media(chat.photo.small_file_id, in_memory=True)
            if photo_bytes:
                return Response(content=photo_bytes.getvalue(), media_type="image/jpeg")
    except Exception:
        pass

    default_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="130" height="160" viewBox="0 0 130 160">
        <rect width="100%" height="100%" fill="#142416"/>
        <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" fill="#22c55e" font-size="30" font-weight="bold">TG</text>
    </svg>"""
    return Response(content=default_svg, media_type="image/svg+xml")

@app.get("/home", response_class=HTMLResponse)
async def home():
    if tg_client is None or not tg_client.is_connected:
        return RedirectResponse(url="/login")

    me = await tg_client.get_me()

    channels_html = ""
    groups_html = ""
    folders_html = f"""
    <a href="/chat/me" class="poster-card">
        <img src="/chat_photo/me" class="poster-img">
        <span class="badge">SAVED</span>
        <div class="card-name">Saved Messages</div>
    </a>
    """

    try:
        async for dialog in tg_client.get_dialogs(limit=60):
            chat = dialog.chat
            if chat.id == me.id:
                continue

            chat_title = chat.title or chat.first_name or f"Chat_{chat.id}"
            
            if chat.type == ChatType.CHANNEL:
                channels_html += f"""
                <a href="/chat/{chat.id}" class="poster-card">
                    <img src="/chat_photo/{chat.id}" class="poster-img" loading="lazy">
                    <span class="badge">CHANNEL</span>
                    <div class="card-name">{chat_title}</div>
                </a>
                """
                folders_html += f"""
                <a href="/chat/{chat.id}" class="poster-card">
                    <img src="/chat_photo/{chat.id}" class="poster-img" loading="lazy">
                    <span class="badge">CHANNEL</span>
                    <div class="card-name">{chat_title}</div>
                </a>
                """
            elif chat.type in [ChatType.SUPERGROUP, ChatType.GROUP]:
                groups_html += f"""
                <a href="/chat/{chat.id}" class="poster-card">
                    <img src="/chat_photo/{chat.id}" class="poster-img" loading="lazy">
                    <span class="badge">GROUP</span>
                    <div class="card-name">{chat_title}</div>
                </a>
                """
    except Exception as e:
        channels_html = f"<div class='error'>{e}</div>"

    html = f"""<!DOCTYPE html><html>{HTML_HEAD}<body>
    <div class="top-bar">
        <div class="brand-title">TELESTREAM</div>
    </div>

    <div class="section-title">Your Telegram Folders</div>
    <div class="poster-row">
        {folders_html}
    </div>

    <div class="section-title">Telegram Channels</div>
    <div class="poster-row">
        {channels_html if channels_html else '<p style="color:#4b5563; font-size:12px;">No channels found</p>'}
    </div>

    <div class="section-title">Groups & Saved</div>
    <div class="poster-row">
        <a href="/chat/me" class="poster-card">
            <img src="/chat_photo/me" class="poster-img">
            <span class="badge">SAVED</span>
            <div class="card-name">Saved Messages</div>
        </a>
        {groups_html}
    </div>

    <div class="bottom-nav">
        <a href="/home" class="nav-item active"><i class="fa-solid fa-house" style="font-size:16px;"></i>Home</a>
        <a href="#" class="nav-item"><i class="fa-solid fa-magnifying-glass" style="font-size:16px;"></i>Search</a>
        <a href="#" class="nav-item"><i class="fa-solid fa-clock-rotate-left" style="font-size:16px;"></i>History</a>
        <a href="#" class="nav-item"><i class="fa-solid fa-gear" style="font-size:16px;"></i>More</a>
    </div>

    </body></html>"""
    return html

@app.get("/chat/{chat_id}", response_class=HTMLResponse)
async def get_chat_videos(chat_id: str):
    if tg_client is None or not tg_client.is_connected:
        return RedirectResponse(url="/login")

    chat_target = "me" if chat_id == "me" else (int(chat_id) if chat_id.lstrip('-').isdigit() else chat_id)

    html = f"""<!DOCTYPE html><html>{HTML_HEAD}<body>
    <div class="top-bar">
        <a href="/home" style="color:#22c55e; font-size:18px; text-decoration:none;"><i class="fa-solid fa-arrow-left"></i> Back</a>
        <div class="brand-title" style="font-size:16px;">Videos</div>
    </div>
    <div style="padding-top:16px;">
    """
    
    count = 0
    try:
        async for msg in tg_client.get_chat_history(chat_target, limit=300):
            media = msg.video or msg.document
            if media:
                mime = getattr(media, "mime_type", "") or ""
                fname = getattr(media, "file_name", None) or f"Video_{msg.id}.mp4"
                if msg.video or "video" in mime or fname.lower().endswith(('.mp4', '.mkv', '.avi', '.webm')):
                    count += 1
                    watch_url = f"/watch/{chat_id}/{msg.id}"
                    html += f"""
                    <div class="video-card">
                        <div style="width:65%;">
                            <div style="font-size:13px; font-weight:700; color:#fff; text-overflow:ellipsis; overflow:hidden; white-space:nowrap;">{fname}</div>
                        </div>
                        <a href="{watch_url}" class="btn-green"><i class="fa-solid fa-play"></i> Watch In-App</a>
                    </div>
                    """
    except Exception as e:
        html += f"<div class='error'>Error: {e}</div>"

    if count == 0:
        html += "<p style='color:#4b5563; text-align:center; padding:40px 0;'>Is channel mein koi video nahi mili!</p>"

    html += "</div></body></html>"
    return html

@app.get("/watch/{chat_id}/{message_id}", response_class=HTMLResponse)
async def watch_video(chat_id: str, message_id: int):
    if tg_client is None or not tg_client.is_connected:
        return RedirectResponse(url="/login")

    chat_target = "me" if chat_id == "me" else (int(chat_id) if chat_id.lstrip('-').isdigit() else chat_id)
    
    try:
        msg = await tg_client.get_messages(chat_target, message_id)
        media = msg.video or msg.document if msg else None
        fname = getattr(media, "file_name", None) or f"Video_{message_id}.mp4" if media else "Video Streaming"
    except Exception:
        fname = "TeleStream Video Player"

    stream_url = f"/stream/{chat_id}/{message_id}"

    return f"""<!DOCTYPE html><html>{HTML_HEAD}<body>
    <div class="top-bar">
        <a href="/chat/{chat_id}" style="color:#22c55e; font-size:18px; text-decoration:none;"><i class="fa-solid fa-arrow-left"></i> Back</a>
        <div class="brand-title" style="font-size:14px; text-overflow:ellipsis; overflow:hidden; white-space:nowrap; max-width:200px;">{fname}</div>
    </div>

    <div style="padding:16px;">
        <div class="player-wrapper">
            <video id="vPlayer" controls playsinline autoplay style="width:100%;">
                <source src="{stream_url}" type="video/mp4">
                Your browser does not support HTML5 video player.
            </video>
        </div>

        <div class="controls-panel">
            <div style="display:flex; align-items:center; gap:8px;">
                <i class="fa-solid fa-language" style="color:#22c55e; font-size:18px;"></i>
                <label style="font-size:12px; font-weight:700; color:#86efac;">Audio / Language:</label>
                <select id="audioSelect" class="select-box" onchange="changeAudioTrack(this.value)">
                    <option value="default">Default Track</option>
                </select>
            </div>

            <div style="display:flex; align-items:center; gap:8px;">
                <i class="fa-solid fa-closed-captioning" style="color:#22c55e; font-size:18px;"></i>
                <label style="font-size:12px; font-weight:700; color:#86efac;">Subtitles:</label>
                <select id="subSelect" class="select-box" onchange="changeSubtitleTrack(this.value)">
                    <option value="off">Off</option>
                </select>
            </div>
        </div>
    </div>

    <script>
        const video = document.getElementById('vPlayer');
        const audioSelect = document.getElementById('audioSelect');
        const subSelect = document.getElementById('subSelect');

        video.addEventListener('loadedmetadata', () => {{
            if (video.audioTracks && video.audioTracks.length > 0) {{
                audioSelect.innerHTML = '';
                for (let i = 0; i < video.audioTracks.length; i++) {{
                    const track = video.audioTracks[i];
                    const option = document.createElement('option');
                    option.value = i;
                    option.text = track.language || track.label || ('Track ' + (i + 1));
                    if (track.enabled) option.selected = true;
                    audioSelect.appendChild(option);
                }}
            }}

            if (video.textTracks && video.textTracks.length > 0) {{
                subSelect.innerHTML = '<option value="off">Off</option>';
                for (let i = 0; i < video.textTracks.length; i++) {{
                    const track = video.textTracks[i];
                    const option = document.createElement('option');
                    option.value = i;
                    option.text = track.language || track.label || ('Subtitle ' + (i + 1));
                    subSelect.appendChild(option);
                }}
            }}
        }});

        function changeAudioTrack(index) {{
            if (video.audioTracks && video.audioTracks.length > 0 && index !== 'default') {{
                for (let i = 0; i < video.audioTracks.length; i++) {{
                    video.audioTracks[i].enabled = (i == index);
                }}
            }}
        }}

        function changeSubtitleTrack(index) {{
            if (video.textTracks && video.textTracks.length > 0) {{
                for (let i = 0; i < video.textTracks.length; i++) {{
                    video.textTracks[i].mode = (i == index) ? 'showing' : 'hidden';
                }}
            }}
        }}
    </script>
    </body></html>"""

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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
