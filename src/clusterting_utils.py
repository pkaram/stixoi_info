"""
utility functions for kmeans clustering and visual creation over data of stixoi_info.db
"""
import string
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import plotly.express as px
import plotly

SENTIMENT_LEXICON_URL = "https://raw.githubusercontent.com/MKLab-ITI/greek-sentiment-lexicon/master/greek_sentiment_lexicon.tsv"

def get_mean_value(df, col1, col2, col3, col4):
    "calculates mean value of cols of a dataframe"
    if sum(np.isnan([df[col1], df[col2], df[col3], df[col4]])) >= 3:
        return None
    return np.nanmean([df[col1], df[col2], df[col3], df[col4]])

def get_mode_value(df, col1, col2, col3, col4):
    "calculates mode value of cols of a dataframe"
    temp_list = [df[col1], df[col2], df[col3], df[col4]]
    mode_temp = max(set(temp_list), key=temp_list.count)
    return mode_temp

def get_sentiment_df():
    """
    Load sentiment scores from github repo (https://github.com/MKLab-ITI/greek-sentiment-lexicon),aggregate and provide
    a sentiment dataframe
    :return: pd.DataFrame
    """
    gr_lexicon = pd.read_csv(SENTIMENT_LEXICON_URL,sep='\t')
    # for Subjectivity we will tranform the categorical into numerical values
    subjectivity_cols = ['Subjectivity1', 'Subjectivity2', 'Subjectivity3', 'Subjectivity4']
    for col in subjectivity_cols:
        gr_lexicon[col] = gr_lexicon[col].apply(
            lambda s: 0 if s == 'OBJ' else 1 if s == "SUBJ-" else 2 if s == "SUBJ+" else None)
    cols_to_add = ['Anger', 'Disgust', 'Fear', 'Happiness', 'Sadness', 'Surprise', 'Subjectivity']
    for col in cols_to_add:
        columns_to_select = []
        for i in range(1, 5):
            columns_to_select.append(col + str(i))
        gr_lexicon[columns_to_select] = gr_lexicon[columns_to_select].astype(float)
        gr_lexicon[col] = gr_lexicon.apply(get_mean_value,
        col1=columns_to_select[0],
        col2=columns_to_select[1],
        col3=columns_to_select[2],
        col4=columns_to_select[3],
        axis=1)
        gr_lexicon = gr_lexicon.drop(columns=columns_to_select, axis=1)
    # for descriptive terms we will use the mode value
    cols_to_add = ['POS', 'Polarity']
    for col in cols_to_add:
        columns_to_select = []
        for i in range(1, 5):
            columns_to_select.append(col + str(i))
        gr_lexicon[col] = gr_lexicon.apply(get_mode_value,
        col1=columns_to_select[0],
        col2=columns_to_select[1],
        col3=columns_to_select[2],
        col4=columns_to_select[3],
        axis=1)
        gr_lexicon = gr_lexicon.drop(columns=columns_to_select, axis=1)
    cols = ['Term', 'POS', 'Polarity', 'Anger', 'Disgust', 'Fear', 'Happiness', 'Sadness', 'Surprise','Subjectivity']
    gr_lexicon = gr_lexicon[cols]
    # we will reproduce the terms for all gerders wherever this is applicable
    gr_lexicon_mod = pd.DataFrame(columns=cols)
    for i in range(len(gr_lexicon)):
        temp_term = gr_lexicon.Term[i]
        terms = temp_term.split(' ')
        temp_values = gr_lexicon.iloc[[i]]
        # remove blank terms caused whitespaces in the initial file
        if '' in terms:
            terms.remove('')
        if len(terms) > 1:
            # for each term you have to define the root of the word and add the part that refers to gender
            terms = [t.strip('-') for t in terms]
            terms = [t for t in terms if t!='/']
            # male is always in 0 position, we will define the root by removing last 2 characters from string
            term_root = terms[0][:-2]
            for j in range(1, len(terms)):
                terms[j] = term_root + terms[j]
            temp_values = temp_values.loc[temp_values.index.repeat(len(terms))]
            temp_values['Term'] = terms
            gr_lexicon_mod = pd.concat([gr_lexicon_mod, temp_values])
        else:
            temp_values['Term'] = terms[0]
            gr_lexicon_mod = pd.concat([gr_lexicon_mod, temp_values])
    gr_lexicon_mod = gr_lexicon_mod.reset_index(drop=True)
    return gr_lexicon_mod


def get_song_sentiments(song_lyrics_df,sentiment_df):
    """
    :param song_lyrics_df(pd.DataFrame): lyrics of songs
    :param sentiment_df(pd.DataFrame): word sentiment scores
    :returns df (pd.DataFrame): Song sentiment scores
    """
    df = pd.DataFrame()
    for i in range(len(song_lyrics_df)):
        lyrics_temp = song_lyrics_df.lyrics[i]
        lyrics_temp = lyrics_temp.replace('\n',' ').replace('\r','')
        for s in string.punctuation:
            lyrics_temp = lyrics_temp.replace(s,' ')
        lyrics_temp = [s for s in lyrics_temp if s!='']
        lyrics_temp = [s.lower() for s in lyrics_temp]
        lyrics_temp_df = pd.DataFrame({'words':lyrics_temp})
        lyrics_temp_df = lyrics_temp_df.groupby(['words']).agg(cnt=('words','count')).reset_index()
        song_info = lyrics_temp_df.merge(sentiment_df,how='left',left_on='words',right_on='Term')
        song_info=song_info.loc[
            (song_info.Anger.isna()==False)|
            (song_info.Disgust.isna()==False) |
            (song_info.Fear.isna()==False) |
            (song_info.Happiness.isna()==False) |
            (song_info.Sadness.isna()==False) |
            (song_info.Surprise.isna()==False) |
            (song_info.Subjectivity.isna()==False)].reset_index()
        cols_of_interest = ['Anger','Disgust','Fear','Happiness','Sadness','Surprise','Subjectivity']
        for col in cols_of_interest:
            song_info[col] = song_info[col] * song_info['cnt']
        song_info['song_name'] = song_lyrics_df.song[i]
        song_info = song_info.groupby('song_name').agg({
            'Anger':'sum',
            'Disgust':'sum',
            'Fear':'sum',
            'Happiness':'sum',
            'Sadness':'sum',
            'Surprise':'sum',
            'Subjectivity':'sum'}).reset_index()
        song_info['song_id'] = song_lyrics_df.song_id[i]
        df = pd.concat([df, song_info])
    df = df.reset_index(drop=True)
    return df

def perform_kmeans(df):
    "performs kmeans on a dataframe"
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df)
    pca = PCA(n_components=2)
    pca_features = pca.fit_transform(scaled_data)
    kmeans = KMeans(n_clusters=6)
    kmeans.fit(scaled_data)
    df['cluster'] = list(kmeans.labels_)
    df['PC_1'] = pca_features[:, 0]
    df['PC_2'] = pca_features[:, 1]
    return df

def produce_plot(df):
    "produces plot based on a dataframe"
    plot_df = df[['artist','PC_1','PC_2','cluster']]
    plot_df['cluster'] = plot_df.cluster.apply(str)
    fig = px.scatter(plot_df, x="PC_1", y="PC_2", text='artist',color='cluster')
    fig.update_traces(mode='markers')
    df = df.sort_values(by='count',ascending=False)
    #select top 10 artists (by # of songs) for each genre to add extra annotations
    df = df.groupby('cluster').head(10)
    plot_df = plot_df[plot_df.artist.isin(df.artist.to_list())]
    plot_df = plot_df.reset_index(drop=True)
    for i in range(len(plot_df)):
        fig.add_annotation(x=plot_df.PC_1[i], y=plot_df.PC_2[i], text=plot_df.artist[i],
                           showarrow=False,
                           yshift=10
                           )
    fig.update_layout(title_text="Artists Clusters based on Sensitivity Score", title_x=0.5)
    plotly.offline.plot(fig,filename='artist_sensitivity_clusters.html')
