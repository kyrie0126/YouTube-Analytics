import plotly.express as px
import plotly.graph_objects as go


def scatter_performance(username, df, variable: str, vid_type: str):
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