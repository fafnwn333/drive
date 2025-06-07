import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import json

# === Google Drive config ===
DRIVE_FOLDER_ID = "1CxYhtopcXOofh0UGgVLyL3zyN5-wmiLE"

# === Telethon config ===
API_ID = 24211342
API_HASH = "4e49c0fabe940e6312af9e21f604e9c0"
SESSION_STRING = "1BVtsOH4Bu3IzckECVp1WwgSV4adA6VSWTLNd7omPG0po_qD4BaI9btZvUUZ6yEF7Lw7Qjs-YfkuiwdEQwJhDVxdkFUKIPIZ-rxFwzkl3nSZVF2GnDsaxa5VfqpNhOLy1mR_4IP2sGKuQ-my_vx5rNw7XoVY5qFSjz8WbvchPNd5nrrk313hunHf7tF4Wp_rK8qwNP2ovvmXzJpQXIpWjhVLgnVZZJO0Uswwiw1dDK9b1RHHOzxDwv0OMJpqnahwLwcTd-pFWMfVVu2zeVa-HGyClCqDsCWTmcL9ECs6k46XTgS2GYb7U15Rzg6yv2ykAEubVI2q4lYdRkfA9T90hstgF9yjCxbg="
CHANNEL_ID = -1002734528612  # Only your specific channel

# === Service Account JSON as Python dict ===
SERVICE_ACCOUNT_DICT = {
  "type": "service_account",
  "project_id": "feisty-pottery-462115-g5",
  "private_key_id": "33e8c52e6ae347db87e052c6c4d0327bf0cd285d",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCqZi7NqmRpDiqz\n57PKaMp8pVc912RHQzWIhFUivuAsg1hu+wtPJ9ETtUz/YfRNAymXa7qGP+KUW1vd\njwwSUbY1i0oie0RZccb4RnPHnyN7qZPfYWB8WUnd1BqCxbUmxLpx53EmT8jaG9gr\n85Jsuws6eRFMuNGtWHiVzBpMeknBQpMi5smUSw6/DOmWu/NB7K1nM1hoBo3NG9Sf\n7fUdegD0lqFZtzwcwHMt6sY9xMBuHQEypu6XZv7kmEKgLWwl3Habjr31V+Lvqr9H\n0ZQ62SBPly2ZKoS4BDQvUzbDVgZvkV3BYe41jT7aMgSdc73/iJcHqS+Xt5C2Aj4W\nFjciJdc9AgMBAAECggEATee34EnV7H4Qof3+Ij10zjYdw+VVMIuWzxqJfgA8p71J\nUjwuuHrgyRzr3hrfwdH/Uv5q4fQVWHTIdGxxPXLkVmifdVJcNnShXmN/jbXBWEl4\nlPmFTnTYI7ZUhJN1tgrdnzQMdFKn5qgyVi3fNRzzDkHJ2gTpwFIhl4MgRvTmAZf4\n9KLhF2IB5b5bAqnmChkyx/Bp0Hxdj7rzDa9oaksi3rlQqJKWVDEmLsxsMMRTV8Vp\nA0eQoV7v/FwDjVC3U+aHdMlbWAGjVJGbImwj11i50KF69B7bVToJestvmqgQ0p9U\nynk+2wCKaolzg8b7HPyne+C8d8lK7C7Z1AU+O2omNQKBgQDtejuIAlFAGUrzxFAb\nINqDyTEy75bc5OgVlSP6hOe/gkZ18gFPgD2cB2ZEc6DjByz4XUycAzSd7mQcCMyH\n67n4uJYhchg+pXmPX9tl9kC7erNfCgQwGBCWy9JDlovAS314jGJHVHOMg3vZTHxd\nEJSbhSrYuySz3IC9V1os0F2FJwKBgQC3sJT+PgXcN6AAHf4ZzCJhPsSogjetUVsR\nJuCVyhY9bp7hhvh2+zLgCVop5a5eXMok79V5hbxXlil9Hu7pKQFoJfcZFnfbiF/+\nNMb5PZNv4mL8ZoRGbJdcT7vh0lJobh4aC0Ly+jl57EGP4CyovrMCxqnF/L5PjjpO\nhnj4ARum+wKBgEDnv42U1JAoWYv2g85mVFLgkknRofINvkDn2kWGPbDh8lAaLLGF\n41DZ1OGwmLB0LZ5UIbQiTCc+GK5w2TXs/48zJBVQEcBNicPd9yEPBPI4vv2ixzI9\n4YrVekpuwxNzjn98HwBP3KTy6s6hUPw+o989rlA+FfHyul0FmufUqzrRAoGASUnm\n6FmOtQJskB9nVpufy/TjOehalogzMXC1go4SuYf9VDYpxC8NaV3R342IOJYFAR+/\nqLC3KKr8+rLw145IxWkAYb4ZLDoJMr+T87Whsa49mD6+3+pLqcUWTU9BGfF1iSad\nG5zCeebNcb4bk2givCTPb/Mba1pv4Qy+DxVCFykCgYEAheYB9N8Y+V0M9XQg/caQ\nNvKAD7/GKpuZWFL8aM3XONNPifhD9MY8S6c58FPZ1g9m/sUn3qa0CSvd3oJuvw8k\nBI8kziemNwT4ZsaIDCLKgibIhlNb5xtPo8kOXckhfgTMk/vu0eZEEk5dzjY2bflE\nOFg+Q9iDb85TSjipzIQfHuU=\n-----END PRIVATE KEY-----\n",
  "client_email": "flux-447@feisty-pottery-462115-g5.iam.gserviceaccount.com",
  "client_id": "107134653001878125524",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/flux-447%40feisty-pottery-462115-g5.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

# === Upload function ===
def upload_to_drive(file_path, filename):
    creds = service_account.Credentials.from_service_account_info(
        SERVICE_ACCOUNT_DICT,
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

# === Telethon client ===
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
    asyncio.run(main())
