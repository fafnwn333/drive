import os
import asyncio
from telethon import TelegramClient, events
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# === Google Drive config ===
SERVICE_ACCOUNT_FILE = "service_account.json"
DRIVE_FOLDER_ID = "1CxYhtopcXOofh0UGgVLyL3zyN5-wmiLE"

# === Telethon config ===
API_ID = 24211342
API_HASH = "4e49c0fabe940e6312af9e21f604e9c0"
SESSION_STRING = "1BVtsOH4Bu3IzckECVp1WwgSV4adA6VSWTLNd7omPG0po_qD4BaI9btZvUUZ6yEF7Lw7Qjs-YfkuiwdEQwJhDVxdkFUKIPIZ-rxFwzkl3nSZVF2GnDsaxa5VfqpNhOLy1mR_4IP2sGKuQ-my_vx5rNw7XoVY5qFSjz8WbvchPNd5nrrk313hunHf7tF4Wp_rK8qwNP2ovvmXzJpQXIpWjhVLgnVZZJO0Uswwiw1dDK9b1RHHOzxDwv0OMJpqnahwLwcTd-pFWMfVVu2zeVa-HGyClCqDsCWTmcL9ECs6k46XTgS2GYb7U15Rzg6yv2ykAEubVI2q4lYdRkfA9T90hstgF9yjCxbg="
CHANNEL_ID = -1002734528612  # Your specific channel

# === Authenticate Google Drive ===
def upload_to_drive(file_path, filename):
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/drive"]
    )
    service = build("drive", "v3", credentials=creds)

    file_metadata = {"name": filename, "parents": [DRIVE_FOLDER_ID]}
    media = MediaFileUpload(file_path, resumable=True)
    uploaded_file = service.files().create(body=file_metadata, media_body=media, fields="id").execute()

    # Make it public
    service.permissions().create(
        fileId=uploaded_file["id"],
        body={"type": "anyone", "role": "reader"},
    ).execute()

    return f"https://drive.google.com/uc?id={uploaded_file['id']}"

# === Start Telethon client ===
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@client.on(events.NewMessage(chats=CHANNEL_ID))
async def handler(event):
    if event.file:
        print(f"📥 File received: {event.file.name}")
        path = await event.download_media()
        print(f"✅ Downloaded: {path}")

        try:
            url = upload_to_drive(path, os.path.basename(path))
            await event.reply(f"✅ Uploaded to Google Drive:\n{url}")
        except Exception as e:
            await event.reply(f"❌ Upload failed:\n{str(e)}")

        os.remove(path)

async def main():
    print("🚀 Bot is running and listening for files...")
    await client.start()
    await client.run_until_disconnected()

if __name__ == "__main__":
    from telethon.sessions import StringSession
    asyncio.run(main())
