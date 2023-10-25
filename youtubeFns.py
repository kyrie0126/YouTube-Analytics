from googleapiclient.discovery import build
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
from sklearn.neighbors import LocalOutlierFactor
import plotly.express as px
import plotly.graph_objects as go

load_dotenv()
api_key = os.getenv('YT_API_KEY')
youtube = build('youtube', 'v3', developerKey=api_key)

class AnalyzeChannel():
    
        
    def __init__(self, api_key, url) -> None:
        self.__api_key = api_key
        self.__youtube = build('youtube', 'v3', developerKey=self.__api_key)
         
        self.channel_id = self.retrieve_channel_id(url)
        self.channel_stats = self.retrieve_channel_stats()
        self.channel_username = self.channel_stats['username']
        self.channel_view_count = int(self.channel_stats['channel_views'])
        self.channel_subscriber_count = int(self.channel_stats['subscriber'])
        self.channel_video_count = int(self.channel_stats['video_count'])


    def retrieve_channel_id(self, url):
            """
            Return channel id as string
            
            Params:
            
            url: (str) url of any video posted by channel
            """

            vid_id = url.split('=')[-1]

            req = self.__youtube.videos().list(
                part='snippet',
                id=vid_id).execute()
            
            channel_id = req['items'][0]['snippet']['channelId']
            
            return channel_id


    def retrieve_channel_stats(self):
        """
        Return channel statistics as dictionary
        
        Params:
        
        username: (str) channel username
        """

        req = self.__youtube.channels().list(
            part=['statistics', 'snippet'],
            id = self.channel_id
        ).execute()
        
        stats = {
            'username': req['items'][0]['snippet']['title'],
            'channel_id': req['items'][0]['id'],
            'channel_views': req['items'][0]['statistics']['viewCount'],
            'subscriber': req['items'][0]['statistics']['subscriberCount'],
            'video_count': req['items'][0]['statistics']['videoCount']
        }
        
        return stats


    def retrieve_channel_videos(self):
        """Retrieve all videos from a channel, return as dataframe
        
        Params (require at least 1):\n
        channel_id: (str) unique channel id assigned by youtube \n
        username: (str) channel username seen by viewers
        """
        
        # retrieve uploads playlist id
        channel_info = self.__youtube.channels().list(
            id=self.channel_id,
            part='contentDetails'
        ).execute()
        
        uploads_id = channel_info['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        
        # retrieve video ids
        vid_ids = []
        next_page_token = None
        
        while True:
            res = self.__youtube.playlistItems().list(
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
            req = self.__youtube.videos().list(
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
        df['duration_min'] = round(df['duration'].dt.components.minutes + df['duration'].dt.components.seconds / 60, 2)
        
        # indicate full video or YT short
        df['video_type'] = np.where(df['duration_min'] > 1, 'standard', 'short')
        
        # convert to numeric
        df['views'] = df['views'].astype('int')
        df['likes'] = df['likes'].astype('int')
        df['comments'] = df['comments'].astype('int')

        return df
        
        
def calculate_lof(df, variable: str):
    """
    Applies unsupervised local outlier factor (LOF) algorithm to variable of interest to classify 
    video performance as hit or normal
    
    Args:
        df (pd.DataFrame): dataframe from `retrieve_channel_videos` function in `AnalyzeChannel()` class
        variable (str): variable of interest
    
    Returns:
        pd.DataFrame: initial dataframe with two extra columns containing LOF result 
    """
    anomaly_inputs = [variable]
        
    # LOF for videos
    df_video = df[df['video_type']=='standard'].copy()
    model_LOF = LocalOutlierFactor()
    df_video['indicator'] = model_LOF.fit_predict(df_video[anomaly_inputs])
    df_video['performance'] = np.where(df_video['indicator']==1, 'Normal', 'Hit')
    
    # LOF for shorts
    df_short = df[df['video_type']=='short'].copy()
    model_LOF = LocalOutlierFactor()
    df_short['indicator'] = model_LOF.fit_predict(df_short[anomaly_inputs])
    df_short['performance'] = np.where(df_short['indicator']==1, 'Normal', 'Hit')
    
    
    
    return pd.concat([df_video, df_short], axis=0)
    
    
    
    
    
def visualize_performance(username, df, variable: str, vid_type: str):
    """
    Creates interactive scatterplot of video performance comparing normal videos to hit videos
    
    Args:
        username (str): name of YouTube channel
        df (DataFrame): output from `calculate_lof` function
        variable (str): column of interest from df
        vid_type (str): type of YT video with 2 choices: 'standard' or 'short'
    
    Returns:
        plotly scatterplot
    """
    
    if vid_type=='standard':
        graph_title = f"{username}'s Youtube Video Performance ({variable})"
    else:
        graph_title = f"{username}'s Youtube Shorts Performance ({variable})"
    
    df_full = df[df['video_type']==vid_type].copy()
    
    df_norm = df_full[df_full['performance']=='Normal'].copy()
    df_norm['normal_rolling_average'] = df_norm[variable].rolling(12).mean()
    
    color_map = {
        'Normal':'#497174',
        'Hit':'#EB6440'
    }
    fig1 = px.scatter(df_full,
                    x='publishTime',
                    y=variable,
                    hover_data=['title', 'duration_min'],
                    color='performance',
                    color_discrete_map=color_map)
    fig2 = px.line(df_norm, x='publishTime',y='normal_rolling_average')
    fig2.update_traces(line_color='#497174')

    fig3 = go.Figure(data = fig1.data + fig2.data)
    fig3.update_layout(title_text=graph_title,
                    title_x=0.5,
                    height=600,
                    plot_bgcolor='#D6E4E5')
    fig3.update_layout(
        legend=dict(
            title=dict(text='Performance'),
            itemsizing='constant'
        ),
        legend_traceorder="reversed"
    )
    fig3.update_xaxes(title_text='Date Posted')
    fig3.update_yaxes(title_text=variable)
    fig3.show()