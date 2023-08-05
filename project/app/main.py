# Simple project withFast API interaction that exposes a GET endpoint that accepts a URL of a video to fetch metadata
# It downlodas a video, converts to audio file and fetches metadata via shazamio library
# https://developers.google.com/explorer-help/code-samples#python
# Author: Nina Siaminou
# Date: 4/8/23

from fastapi import FastAPI, HTTPException     # pylint: disable=import-error
from fastapi import BackgroundTasks
from googleapiclient.discovery import build    # pylint: disable=import-error
from googleapiclient.errors import HttpError 
import asyncio
from utils import Utils
import json
 
app = FastAPI()

# Put here the development key. You can produce one on the following link: https://console.cloud.google.com/
# Opening JSON file to fetch the key
c_file = open("../dev_key.json")
 
# returns JSON object as
# a dictionary
data = json.load(c_file)
print(data)
DEVELOPER_KEY = data["dev_key"]

# Base path where the audio files are saved
BASE_PATH = "/audio_files/"

# API parameters to build the resource to communicate with the API
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

# Build the API
youtube_api = build(serviceName=API_SERVICE_NAME, version=API_VERSION, developerKey=DEVELOPER_KEY)

# Define the get method with the video-data endpoint
@app.get("/video-data/")
async def get_video_data(video_url: str, background_tasks: BackgroundTasks):
    """_summary_

    Args:
        video_url (str): url of the video to fetch its metadata

    Raises:
        HTTPException: HTTP exception when a problem arises

    Returns:
        dict: dictionary with the fetched metadata
    """
    # Extract video_id from the URL given
    video_id = video_url.split("=")[-1]
    # Call the YouTube Data API to fetch video data
    try:
        # connect with the youtube API
        response = youtube_api.videos().list( # pylint: disable=maybe-no-member
            part='snippet,statistics',id=video_id
        ).execute()
        # check if the response has videos with this id
        if not response.get("items"):
            raise IndexError("No video found with this url")
        # Process the response and extract relevant metadata
        video_snippet = response['items'][0]['snippet']
        video_statistics = response['items'][0]['statistics']

        # path to the downloaded video
        output_path = Utils.download_video(video_url, BASE_PATH)
        print(output_path)

        background_tasks.add_task(Utils.analyze_audio, output_path)
    

        return {
            "title": video_snippet['title'],
            "published_at": video_snippet['publishedAt'],
            "description": video_snippet['description'],
            "channel_title": video_snippet['channelTitle'],
            "view_count": video_statistics["viewCount"],
            "like_count": video_statistics["likeCount"],
            "comment_count": video_statistics["commentCount"]
        }
    
    # Error Handling
    except IndexError as e:
        raise HTTPException(status_code=404, detail="This url does not correspond to a video, please try again!")
    except HttpError as e:
        # Check if the error message contains the words forbidden quota to handle these scenarios
        error_message = e.content if e.content else str(e)
        if "quota" in error_message.lower():  
            raise HTTPException(f"Quota Exceeded, Please try again later. Error: {error_message}")
        if "forbidden" in error_message.lower():
            raise HTTPException(f"Video needs a kind of authorization, please try again! Error: {error_message}")
    # General pool error handling
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ERROR: {str(e)}")
        
    