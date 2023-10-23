from googleapiclient.discovery import build
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('YT_API_KEY')
youtube = build('youtube', 'v3', developerKey=api_key)


def retrieve_channel_stats(id):
    """
    Return channel statistics as dictionary
    
    Params:
    
    username: (str) channel username
    """

    req = youtube.channels().list(
        part=['statistics', 'snippet'],
        id = id
    ).execute()
    
    stats = {
        'username': req['items'][0]['snippet']['title'],
        'channel_id': req['items'][0]['id'],
        'channel_views': req['items'][0]['statistics']['viewCount'],
        'subscriber': req['items'][0]['statistics']['subscriberCount'],
        'video_count': req['items'][0]['statistics']['videoCount']
    }
    
    return stats


def retrieve_channel_id(url):
    """
    Return channel id as string
    
    Params:
    
    url: (str) url of any video posted by channel
    """

    vid_id = url.split('=')[-1]

    req = youtube.videos().list(
        part='snippet',
        id=vid_id).execute()
    
    channel_id = req['items'][0]['snippet']['channelId']
    
    return channel_id


def retrieve_channel_videos(id):
    """Retrieve all videos from a channel, return as dataframe
    
    Params (require at least 1):\n
    channel_id: (str) unique channel id assigned by youtube \n
    username: (str) channel username seen by viewers
    """
    
    # retrieve uploads playlist id
    channel_info = youtube.channels().list(
        id=id,
        part='contentDetails'
    ).execute()
    
    uploads_id = channel_info['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    
    # retrieve video ids
    vid_ids = []
    next_page_token = None
    
    while True:
        res = youtube.playlistItems().list(
            playlistId=uploads_id,
            part=['snippet', 'contentDetails'],
            maxResults=50,
            pageToken=next_page_token
        ).execute()
        for video in res['items']:
            vid_ids.append(video['contentDetails']['videoId'])
            
        next_page_token = res.get('nextPageToken')
        
        if next_page_token is None:
            break
        
    
    # retrieve video data
    vid50 = [vid_ids[i * 50:(i + 1) * 50] for i in range((len(vid_ids) + 49) // 50 )]
    video_data = []

    for i in vid50:
        req = youtube.videos().list(
        part=['snippet', 'statistics', 'contentDetails'],
        id=i).execute()
        
        for video in req['items']:
            vid_dict = {
                'id': video['id'],
                'title': video['snippet']['title'],
                'publishTime': video['snippet']['publishedAt'],
                'duration': video['contentDetails']['duration'],
                'views': video['statistics']['viewCount'],
                'likes': video['statistics']['likeCount'],
                'comments': video['statistics']['commentCount']
            }
            video_data.append(vid_dict)
            
    df = pd.DataFrame.from_records(video_data)
    
    # clean datetime columns
    df['publishTime'] = pd.to_datetime(df['publishTime'])
    df['day_name'] = df['publishTime'].dt.day_name()

    # Define custom weekday order
    weekdays_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    weekday_cat_dtype = pd.api.types.CategoricalDtype(categories=weekdays_order, ordered=True)
    df['weekday_name'] = df['day_name'].astype(weekday_cat_dtype)

    # clean ISO encoded duration column
    df['duration'] = pd.to_timedelta(df['duration'])
    df['duration_min'] = df['duration'].dt.components.minutes + df['duration'].dt.components.seconds / 60
    
    # indicate full video or YT short
    df['video_type'] = np.where(df['duration_min'] > 1, 'standard', 'short')


    return df
    
    
    
    