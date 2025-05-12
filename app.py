import os
import time
import random
import csv
import datetime
import google.auth
import google.auth.transport.requests
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Constants
CLIENT_SECRETS_FILE = "yt_upload.json"
TOKEN_FILE = "token.json"
YOUTUBE_UPLOAD_SCOPE = ["https://www.googleapis.com/auth/youtube.upload"]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
VIDEO_CATEGORY = "15"  # Change this as needed
PRIVACY_STATUS = "private"  # Videos will be scheduled as private
VIDEO_DIRECTORY = "videos"
CSV_FILE = "video_metadata.csv"
SET_SIZE = 5  # Number of videos to upload per batch (default: 10)
START_DATE = "2025-04-26"  # Change this to your desired start date (YYYY-MM-DD)

# Schedule timings in UTC (23:00 UTC to 03:30 UTC in 30-minute intervals)
SCHEDULE_TIMINGS = [
    (23, 0),   # 1st video at 23:00 UTC
    (23, 30),  # 2nd video at 23:30 UTC
    (0, 0),    # 3rd video at 00:00 UTC
    (0, 30),   # 4th video at 00:30 UTC
    (1, 0),    # 5th video at 01:00 UTC
    (1, 30),   # 6th video at 01:30 UTC
    (2, 0),    # 7th video at 02:00 UTC
    (2, 30),   # 8th video at 02:30 UTC
    (3, 0),    # 9th video at 03:00 UTC
    (3, 30),   # 10th video at 03:30 UTC
]

def get_authenticated_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, YOUTUBE_UPLOAD_SCOPE)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, YOUTUBE_UPLOAD_SCOPE)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=creds)

def schedule_upload(youtube, file_path, title, description, tags, publish_time):
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": VIDEO_CATEGORY,
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": PRIVACY_STATUS,
            "publishAt": publish_time.isoformat() + "Z",  # Convert to ISO format
        },
    }
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    resumable_upload(request)

def resumable_upload(request):
    response = None
    error = None
    retry = 0
    while response is None:
        try:
            print("Uploading file...")
            status, response = request.next_chunk()
            if response:
                if "id" in response:
                    print(f"✅ Video uploaded successfully! Video ID: {response['id']}")
                else:
                    print(f"❌ Upload failed: {response}")
                    return
        except HttpError as e:
            if e.resp.status in [500, 502, 503, 504]:
                error = f"A retriable HTTP error {e.resp.status} occurred: {e.content}"
            else:
                raise
        except Exception as e:
            error = f"A retriable error occurred: {e}"

        if error:
            print(error)
            retry += 1
            if retry > 10:
                print("❌ Max retries reached. Upload failed.")
                return
            sleep_time = random.uniform(1, min(60, 2**retry))
            print(f"🔄 Retrying in {sleep_time:.2f} seconds...")
            time.sleep(sleep_time)

def main():
    youtube = get_authenticated_service()
    if not os.path.exists(CSV_FILE):
        print(f"❌ CSV file '{CSV_FILE}' not found. Exiting.")
        return

    with open(CSV_FILE, mode="r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        videos = list(reader)

    if not videos:
        print("❌ No videos found in CSV file. Exiting.")
        return

    start_date = datetime.datetime.strptime(START_DATE, "%Y-%m-%d")
    for i in range(0, len(videos), SET_SIZE):
        publish_date = start_date + datetime.timedelta(days=i // SET_SIZE)

        batch = videos[i:i + SET_SIZE]
        print(f"📅 Scheduling batch {i // SET_SIZE + 1} for {publish_date.strftime('%Y-%m-%d')} UTC")

        for idx, row in enumerate(batch):
            file_name = row["File_name"].strip()
            title = row["title"].strip()
            description = row["description"].strip()
            tags = [tag.strip() for tag in row["tags"].split(",")]
            file_path = os.path.join(VIDEO_DIRECTORY, file_name)
            
            # Get the schedule time from the predefined list
            schedule_time = SCHEDULE_TIMINGS[idx]
            publish_time = publish_date.replace(hour=schedule_time[0], minute=schedule_time[1], second=0)

            if os.path.exists(file_path):
                print(f"🚀 Scheduling {file_name} for {publish_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
                schedule_upload(youtube, file_path, title, description, tags, publish_time)
            else:
                print(f"⚠️ File '{file_name}' not found in '{VIDEO_DIRECTORY}'. Skipping.")

if __name__ == "__main__":
    main()
