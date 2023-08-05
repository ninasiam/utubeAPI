"""utils.py

This file contains the utility functions for:
 * video download
 * audio extraction
 * audio recognition

 Author: Nina Siaminou
"""

from pytube import YouTube
import asyncio
from shazamio import Shazam, Serialize
import os 

class Utils(object):
    """Class that contain utility functions for the video download and conversion
    """
    @staticmethod
    def download_video(url: str, path: str) -> str:
        """Function that downloads a video from youtube via pytube

        Args:
            url (str): url of the video
            path (str): path where the video will be saved

        Returns:
            str: in case of Success, the path is returned, else a string that describes the error
        """        
        try:
            utube = YouTube(url)
            stream = utube.streams.filter(only_audio=True).first()
            path = os.path.dirname(os.getcwd()) + path
            print(path)
            audio = stream.download(output_path=path)
            base, ext = os.path.splitext(audio)
            path = base + ext
            return path
        except Exception as e:
            return f"Failed to download video. Error: {str(e)}"
        
    @staticmethod        
    async def analyze_audio(path: str):
    
        shazam = Shazam()
        out = await shazam.recognize_song(path)
        print(out)

        serialized = Serialize.full_track(out)
        print(serialized)



