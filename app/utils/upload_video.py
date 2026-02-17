import os
import pickle
import google.auth.transport.requests
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from pathlib import Path
from googleapiclient.errors import HttpError

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRETS_DIR = BASE_DIR / "materials" / "secrets"

CLIENT_SECRETS_FILE = SECRETS_DIR / "client_secrets.json"
TOKEN_FILE = SECRETS_DIR / "token.pickle"

# If modifying scopes, delete token.pickle.
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def authenticate():
    credentials = None

    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, "rb") as token:
            credentials = pickle.load(token)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(google.auth.transport.requests.Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CLIENT_SECRETS_FILE), SCOPES
            )
            credentials = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(credentials, token)

    return build("youtube", "v3", credentials=credentials)


def upload_video(file_path, title, description, thumbnail_path=None):
    youtube = authenticate()

    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": "public"
        }
    }

    media_file = MediaFileUpload(file_path, chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media_file
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploading... {int(status.progress() * 100)}%")

    video_id = response["id"]

    print("Upload complete!")
    print("Video ID:", video_id)
    print(f"YouTube URL: https://youtube.com/watch?v={video_id}")

    # ---------- THUMBNAIL UPLOAD ----------
    if thumbnail_path and os.path.exists(thumbnail_path):
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
            print("Thumbnail uploaded successfully.")
        except HttpError as e:
            print("Thumbnail upload failed:", e)


if __name__ == "__main__":
    upload_video(
        file_path="video.mp4",
        title="Automated Upload Test",
        description="Uploaded via Python automation.",
    )
