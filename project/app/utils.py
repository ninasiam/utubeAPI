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
import csv
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
            # create the object 
            utube = YouTube(url)
            stream = utube.streams.filter(only_audio=True).first()
            # Construct the path
            path = os.path.dirname(os.getcwd()) + path
            # Download the video
            audio = stream.download(output_path=path)
            # Return the path
            base, ext = os.path.splitext(audio)
            path = base + ext
            return path
        except Exception as e:
            return f"Failed to download video. Error: {str(e)}"
        
    @staticmethod        
    async def analyze_audio(path: str):
        """Method that analyses the video via the shazamio library

        Args:
            path (str): path to the downloaded video
        """  
        # Create the Shazam object      
        shazam = Shazam()
        out = await shazam.recognize_song(path)
        serialized = Serialize.full_track(out)

        print(out["track"].keys())
        print(path)
        fields, data = out["track"].keys(), out["track"].values()

        #path_to_the_file = Utils.write_in_csv("/temp_shazam.csv", os.path.dirname(os.getcwd()), fields, data)
        
    @staticmethod
    def write_in_csv(csv_name: str, path: str, fields: list, data: list) -> str:
        """Function that writes to a csv file

        Args:
            path (str): the input path to write the csv file
            fields (list): the column names 
            data (list): data to write

        Returns:
            str: the path to the file
        """        
        path = os.path.dirname(os.getcwd()) + path
        csv_name = path + csv_name
        # writing to csv file 
        with open(csv_name, 'w') as csvfile: 
            # creating a csv writer object 
            csvwriter = csv.writer(csvfile) 
                
            # writing the fields 
            csvwriter.writerow(fields) 
                
            # writing the data rows 
            csvwriter.writerows(data)

        return csv_name


