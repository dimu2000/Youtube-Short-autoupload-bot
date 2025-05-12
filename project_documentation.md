# Automating YouTube Short Uploads: A Step-by-Step Guide

## What Does This Project Do?

This project is a YouTube Short auto-upload bot designed to automate the process of uploading videos to YouTube. By using metadata from a CSV file, it schedules the upload of videos, making it an excellent tool for content creators who want to consistently upload content without manual intervention. The script ensures that videos are uploaded with the right descriptions, tags, and scheduled timings, thereby simplifying video management on YouTube.


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
