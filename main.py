import os
import json
import asyncio
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# === Load .env ===
load_dotenv()

# === Config ===
API_ID = 24211342
API_HASH = "4e49c0fabe940e6312af9e21f604e9c0"
SESSION_STRING = "1BVtsOH4Bu3IzckECVp1WwgSV4adA6VSWTLNd7omPG0po_qD4BaI9btZvUUZ6yEF7Lw7Qjs-YfkuiwdEQwJhDVxdkFUKIPIZ-rxFwzkl3nSZVF2GnDsaxa5VfqpNhOLy1mR_4IP2sGKuQ-my_vx5rNw7XoVY5qFSjz8WbvchPNd5nrrk313hunHf7tF4Wp_rK8qwNP2ovvmXzJpQXIpWjhVLgnVZZJO0Uswwiw1dDK9b1RHHOzxDwv0OMJpqnahwLwcTd-pFWMfVVu2zeVa-HGyClCqDsCWTmcL9ECs6k46XTgS2GYb7U15Rzg6yv2ykAEubVI2q4lYdRkfA9T90hstgF9yjCxbg="
CHANNEL_ID = -1002734528612
DRIVE_FOLDER_ID = "1CxYhtopcXOofh0UGgVLyL3zyN5-wmiLE"

# === Parse service account JSON from .env ===
sa_raw = os.getenv("GOOGLE_SERVICE_ACCOUNT")
service_account_info = json.loads(sa_raw.replace("\\n", "\n"))

# === Upload to Drive ===
def upload_to_drive(file_path, filename):
    creds = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    drive = build("drive", "v3", credentials=creds)

    metadata = {"name": filename, "parents": [DRIVE_FOLDER_ID]}
    media = MediaFileUpload(file_path, resumable=True)
    uploaded = drive.files().create(body=metadata, media_body=media, fields="id").execute()

    # Make public
    drive.permissions().create(
        fileId=uploaded["id"],
        body={"type": "anyone", "role": "reader"}
    ).execute()

    return f"https://drive.google.com/uc?id={uploaded['id']}"

# === Telethon client ===
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@client.on(events.NewMessage(chats=CHANNEL_ID))
async def handler(event):
    if event.file:
        print(f"📥 File: {event.file.name}")
        path = await event.download_media()
        print(f"✅ Saved: {path}")

        try:
            link = upload_to_drive(path, os.path.basename(path))
            await event.reply(f"✅ Uploaded to Drive:\n{link}")
        except Exception as e:
            await event.reply(f"❌ Upload failed:\n{str(e)}")

        os.remove(path)

async def main():
    print("🚀 Bot started...")
    await client.start()
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
