import pandas as pd
import numpy as np
from sklearn.neighbors import LocalOutlierFactor


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
    try:
        # LOF for shorts
        df_short = df[df['video_type']=='short'].copy()
        model_LOF = LocalOutlierFactor()
        df_short['indicator'] = model_LOF.fit_predict(df_short[anomaly_inputs])
        df_short['performance'] = np.where(df_short['indicator']==1, 'Normal', 'Hit')
    except ValueError:
        return df_video    

    return pd.concat([df_video, df_short], axis=0)