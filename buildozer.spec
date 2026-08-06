[app]
title = Telegram Web App
package.name = telegramapp
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt
version = 1.0

requirements = python3,fastapi,uvicorn,pyrogram,httpx,tgcrypto

orientation = portrait
osx.python_version = 3
osx.kivy_version = 1.9.1
fullscreen = 0
android.permissions = INTERNET

[buildozer]
log_level = 2
warn_on_root = 1
