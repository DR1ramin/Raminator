from base64 import b64decode
from pathlib import Path
from datetime import datetime
import requests
 # تولید نام فایل بر اساس تاریخ و زمان فعلی
now = datetime.now()
timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")  # قالب: سال-ماه-روز_ساعت-دقیقه-ثانیه
r = requests.post(
    "https://api.imagepig.com/flux",
    headers={"Api-Key": "e1aa9003-c274-4cc9-8459-2e9a8b5d88d0"},
    json={"prompt": "Vast forest","proportion":"landscape"},
)

if r.ok:
    with Path(f"static/images/image-{timestamp}.jpeg").open("wb") as f:
        f.write(b64decode(r.json()["image_data"]))
else:
    r.raise_for_status()