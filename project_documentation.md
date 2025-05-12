# Automating YouTube Short Uploads: A Step-by-Step Guide

## What Does This Project Do?

This project is a YouTube Short auto-upload bot designed to automate the process of uploading videos to YouTube. By using metadata from a CSV file, it schedules the upload of videos, making it an excellent tool for content creators who want to consistently upload content without manual intervention. The script ensures that videos are uploaded with the right descriptions, tags, and scheduled timings, thereby simplifying video management on YouTube.

## How This Script Works

The script is built around several key components that work together to achieve automated uploads. Let’s break down how it works in simple terms:

1. **Authentication with YouTube API**:  
   The script uses OAuth 2.0 to authenticate with YouTube, which allows it to upload videos on your behalf. If the credentials are expired or missing, it will prompt you to log in via a browser.

   Here is how it does that:
   ```python
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
   ```

2. **Scheduling Video Uploads**:  
   The script reads metadata from a CSV file, which includes file names, titles, descriptions, and tags, and schedules each video for upload at specific times.

   Here’s the main function where this happens:
   ```python
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

           for idx, row in enumerate(batch):
               file_name = row["File_name"].strip()
               title = row["title"].strip()
               description = row["description"].strip()
               tags = [tag.strip() for tag in row["tags"].split(",")]
               file_path = os.path.join(VIDEO_DIRECTORY, file_name)
               
               schedule_time = SCHEDULE_TIMINGS[idx]
               publish_time = publish_date.replace(hour=schedule_time[0], minute=schedule_time[1], second=0)

               if os.path.exists(file_path):
                   print(f"🚀 Scheduling {file_name} for {publish_time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
                   schedule_upload(youtube, file_path, title, description, tags, publish_time)
               else:
                   print(f"⚠️ File '{file_name}' not found in '{VIDEO_DIRECTORY}'. Skipping.")
   ```

3. **Uploading Videos**:  
   The `schedule_upload` function is responsible for uploading each video. It uses the `resumable_upload` function to handle potential interruptions during the upload process.

   Here’s how it works:
   ```python
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
               "publishAt": publish_time.isoformat() + "Z",
           },
       }
       media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
       request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
       resumable_upload(request)
   ```

4. **Error Handling**:  
   The script includes error handling to retry uploads in case of network issues, which ensures robust and reliable performance.

   Here’s how it manages retries:
   ```python
   def resumable_upload(request):
       response = None
       error = None
       retry = 0
       while response is None:
           try:
               print("Uploading file...")
               status, response = request.next_chunk()
               if response:
                   print(f"✅ Video uploaded successfully! Video ID: {response['id']}")
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
   ```

## How to Create It Step by Step

Here’s how you can recreate this project from scratch:

1. **Set Up the Environment**:
   - Install Python if you haven’t already.
   - Install necessary libraries: `google-auth`, `google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client`.

   ```bash
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

2. **Create a Google Cloud Project**:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/).
   - Create a new project and enable the YouTube Data API v3.
   - Create credentials: OAuth 2.0 Client IDs, and download the `client_secret.json` file.

3. **Prepare the Script**:
   - Save the provided script into a file named `app.py`.
   - Place `client_secret.json` in the same directory as your script and rename it to `yt_upload.json`.
   - Ensure you have a `video_metadata.csv` file with appropriate metadata for your videos.

4. **Populate the Video Directory**:
   - Create a folder named `videos` in the same directory as your script.
   - Place all the video files you intend to upload into this folder.

5. **Run the Script**:
   - Execute the script by running `python app.py` in your terminal.

   ```bash
   python app.py
   ```

6. **Authenticate**:
   - On first run, the script will open a browser for you to authenticate your Google account.

This project automates the tedious process of managing video uploads, allowing you to focus on creating content. With a few initial setups, you can have your videos uploaded and scheduled effortlessly.