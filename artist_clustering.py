import sqlite3
import pandas as pd
import numpy as np
import string
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import plotly.express as px
import plotly


def sentiment_dictionary():
    """
    Load sentiment scores from github repo (https://github.com/MKLab-ITI/greek-sentiment-lexicon),aggregate and provide
    a sentiment dictionary
    :return: sentiment dictionary
    """
    def mean_value(a, col1, col2, col3, col4):
        if sum(np.isnan([a[col1], a[col2], a[col3], a[col4]])) >= 3:
            return None
        else:
            return np.nanmean([a[col1], a[col2], a[col3], a[col4]])

    def mode_func(a, col1, col2, col3, col4):
        temp_list = [a[col1], a[col2], a[col3], a[col4]]
        mode_temp = max(set(temp_list), key=temp_list.count)
        return mode_temp

    gr_lexicon = pd.read_csv("https://raw.githubusercontent.com/MKLab-ITI/greek-sentiment-lexicon/master/greek_sentiment_lexicon.tsv",sep='\t')

    # for Subjectivity we will tranform the categorical into numerical values
    subjectivity_columns = ['Subjectivity1', 'Subjectivity2', 'Subjectivity3', 'Subjectivity4']
    for column_selected in subjectivity_columns:
        gr_lexicon[column_selected] = gr_lexicon[column_selected].apply(
            lambda s: 0 if s == 'OBJ' else 1 if s == "SUBJ-" else 2 if s == "SUBJ+" else None)

    # columns_to_add=['POS','Subjectivity','Polarity','Anger','Disgust','Fear','Happiness','Sadness','Surprise']
    columns_to_add = ['Anger', 'Disgust', 'Fear', 'Happiness', 'Sadness', 'Surprise', 'Subjectivity']
    for column_add in columns_to_add:
        columns_to_select = []
        for i in range(1, 5):
            columns_to_select.append(column_add + str(i))
        gr_lexicon[columns_to_select] = gr_lexicon[columns_to_select].astype(float)
        gr_lexicon[column_add] = gr_lexicon.apply(mean_value,
                                                  col1=columns_to_select[0],
                                                  col2=columns_to_select[1],
                                                  col3=columns_to_select[2],
                                                  col4=columns_to_select[3],
                                                  axis=1)
        gr_lexicon = gr_lexicon.drop(columns=columns_to_select, axis=1)

    # for descriptive terms we will use the mode value
    columns_to_add_descr = ['POS', 'Polarity']
    for column_add in columns_to_add_descr:
        columns_to_select = []
        for i in range(1, 5):
            columns_to_select.append(column_add + str(i))
        gr_lexicon[column_add] = gr_lexicon.apply(mode_func,
                                                  col1=columns_to_select[0],
                                                  col2=columns_to_select[1],
                                                  col3=columns_to_select[2],
                                                  col4=columns_to_select[3],
                                                  axis=1)
        gr_lexicon = gr_lexicon.drop(columns=columns_to_select, axis=1)

    # we will keep only certain columns
    columns_needed = ['Term', 'POS', 'Polarity', 'Anger', 'Disgust', 'Fear', 'Happiness', 'Sadness', 'Surprise','Subjectivity']
    gr_lexicon = gr_lexicon[columns_needed]

    # we will reproduce the terms for all gerders wherever this is applicable
    gr_lexicon_mod = pd.DataFrame(columns=columns_needed)
    columns_needed.remove('Term')
    for i in range(gr_lexicon.shape[0]):
        temp_term = gr_lexicon.Term[i]
        terms = temp_term.split(' ')
        temp_values = gr_lexicon.loc[i, columns_needed]
        # remove blank terms caused whitespaces in the initial file
        if '' in terms:
            terms.remove('')

        if len(terms) > 1:
            # for each term you have to define the root of the word and add the part that refers to gender
            terms = [s.strip('-') for s in terms]
            # male is always in 0 position, we will define the root by removing last 2 characters from string
            term_root = terms[0][:-2]
            for j in range(1, len(terms)):
                terms[j] = term_root + terms[j]

            for j in range(len(terms)):
                temp_values['Term'] = terms[j]
                gr_lexicon_mod = gr_lexicon_mod.append(temp_values)

        else:
            temp_values['Term'] = terms[0]
            gr_lexicon_mod = gr_lexicon_mod.append(temp_values)

    gr_lexicon_mod = gr_lexicon_mod.reset_index(drop=True)
    return gr_lexicon_mod


def song_sentiments(song_lyrics,sentiment_dict):
    """
    :param song_lyrics: lyrics of songs
    :param sentiment_dict: word sentiment scores
    :return: Song sentiment scores
    """
    #calculate sentiment scores for all songs of the artist
    song_info_all=pd.DataFrame()
    for i in range(song_lyrics.shape[0]):
        lyrics_temp=song_lyrics.lyrics[i]
        #replace strings related to format
        lyrics_temp=lyrics_temp.replace('\n',' ')
        lyrics_temp=lyrics_temp.replace('\r','')
        #remove punctuation
        for s in string.punctuation:
            lyrics_temp=lyrics_temp.replace(s,' ')

        lyrics_terms_temp=lyrics_temp.split(' ')
        #remove '' characters
        lyrics_terms_temp=[s for s in lyrics_terms_temp if s!='']
        #make all strings lower
        lyrics_terms_temp=[s.lower() for s in lyrics_terms_temp]

        lyrics_temp_df=pd.DataFrame({'words':lyrics_terms_temp})
        lyrics_temp_df=lyrics_temp_df.groupby(['words']).agg(cnt=('words','count')).reset_index()

        #join the sentiment_dict information on the words selected
        song_info=lyrics_temp_df.merge(sentiment_dict,how='left',left_on='words',right_on='Term')

        song_info=song_info.loc[
            (song_info.Anger.isna()==False )|
            (song_info.Disgust.isna()==False) |
            (song_info.Fear.isna()==False) |
            (song_info.Happiness.isna()==False) |
            (song_info.Sadness.isna()==False) |
            (song_info.Surprise.isna()==False) |
            (song_info.Subjectivity.isna()==False)].reset_index()

        columns_to_change=['Anger','Disgust','Fear','Happiness','Sadness','Surprise','Subjectivity']
        for column in columns_to_change:
            song_info[column]=song_info[column]*song_info['cnt']

        song_info['song_name']=song_lyrics.song[i]
        song_info=song_info.groupby('song_name').agg({'Anger':'sum',
                                        'Disgust':'sum',
                                        'Fear':'sum',
                                        'Happiness':'sum',
                                        'Sadness':'sum',
                                        'Surprise':'sum',
                                        'Subjectivity':'sum'}).reset_index()
        song_info['song_id'] = song_lyrics.song_id[i]
        song_info_all=song_info_all.append(song_info)
    song_info_all=song_info_all.reset_index(drop=True)
    return song_info_all


if __name__=='__main__':
    # connect with db (is created after running create_db.py)
    cnx = sqlite3.connect('stoixoi_info.db')
    # load all song lyrics
    song_lyrics = pd.read_sql("select * from song_lyrics", cnx)
    # load sentiment dictionary
    sentiment_dict = sentiment_dictionary()
    # song sentiments
    song_sentiment_scores=song_sentiments(song_lyrics, sentiment_dict)

    # artist information
    artists=pd.read_sql("select first_artist_to_sing_the_song as artist,song_id from artist_songs_info",cnx)
    songs_artists=song_sentiment_scores.merge(artists,on='song_id',how='left')
    songs_artists=songs_artists.groupby('artist').agg({'song_id':'count',
                                                            'Anger':'sum',
                                                            'Disgust':'sum',
                                                            'Fear':'sum',
                                                            'Happiness':'sum',
                                                            'Sadness':'sum',
                                                            'Surprise':'sum',
                                                            'Subjectivity':'sum'
                                                            })
    songs_artists=songs_artists.reset_index()
    songs_artists=songs_artists.rename(columns={'song_id':'count'})
    # filter for artists that have at least sang 10 songs
    songs_artists = songs_artists.loc[songs_artists['count'] >= 10]
    songs_artists=songs_artists[songs_artists.artist!='Άγνωστος']
    songs_artists=songs_artists.reset_index(drop=True)
    #divide with 'count' to get the me values for all sentiment related columns
    for temp_col in songs_artists.columns:
        if (temp_col not in ['count','artist']):
            songs_artists[temp_col]=songs_artists[temp_col]/songs_artists['count']

    #scale and perform PCA
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(songs_artists.drop(columns=['artist', 'count']))
    pca = PCA(n_components=2)
    pca_features = pca.fit_transform(scaled_data)

    #number of clusters selected based on elbow method (not included here)
    kmeans = KMeans(n_clusters=6)
    kmeans.fit(scaled_data)
    songs_artists['cluster'] = list(kmeans.labels_)

    plot_df = pd.DataFrame({'artist': songs_artists['artist'],
                            'PC_1': pca_features[:, 0],
                            'PC_2': pca_features[:, 1],
                            'cluster': list(kmeans.labels_)
                            })
    plot_df['cluster'] = plot_df.cluster.apply(str)

    fig = px.scatter(plot_df, x="PC_1", y="PC_2", text='artist',color='cluster')
    fig.update_traces(mode='markers')
    songs_artists=songs_artists.sort_values(by='count',ascending=False)
    #select top 10 artists (by # of songs) for each genre to add extra annotations
    songs_artists_cluster = songs_artists.groupby('cluster').head(10)
    plot_df_add = plot_df[plot_df.artist.isin(songs_artists_cluster.artist.to_list())]
    plot_df_add=plot_df_add.reset_index(drop=True)
    for i in range(0,plot_df_add.shape[0]):
        fig.add_annotation(x=plot_df_add.PC_1[i], y=plot_df_add.PC_2[i], text=plot_df_add.artist[i],
                           showarrow=False,
                           yshift=10
                           )
    fig.update_layout(title_text="Artists Clusters based on Sensitivity Score", title_x=0.5)
    #fig.show()
    #save plot in html format
    plotly.offline.plot(fig,filename='artist_sensitivity_clusters.html')