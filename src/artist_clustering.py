"""
Script to calculate sentiment scores for the songs artists have sang, cluaster them based
on these scores and produce a visual.
"""
import logging
from connection_utils import get_data_from_db
from clusterting_utils import get_sentiment_df, get_song_sentiments, perform_kmeans, produce_plot

logging.getLogger().setLevel(logging.INFO)

if __name__=='__main__':
    logging.info('loading data')
    query = "select * from song_lyrics"
    song_lyrics = get_data_from_db(query)
    sentiment_df = get_sentiment_df()
    song_sentiment_scores=get_song_sentiments(song_lyrics, sentiment_df)
    query = "select first_artist_to_sing_the_song as artist,song_id from artist_songs_info"
    artists = get_data_from_db(query)
    logging.info('preparing data')
    songs_artists = song_sentiment_scores.merge(artists,on='song_id',how='left')
    songs_artists = songs_artists.groupby('artist').agg({'song_id':'count',
    'Anger':'sum',
    'Disgust':'sum',
    'Fear':'sum',
    'Happiness':'sum',
    'Sadness':'sum',
    'Surprise':'sum',
    'Subjectivity':'sum'
    }).reset_index()
    songs_artists=songs_artists.rename(columns={'song_id':'count'})
    # filter for artists that have at least sang 10 songs
    songs_artists = songs_artists.loc[songs_artists['count'] >= 10]
    # filter out special case
    songs_artists = songs_artists[songs_artists.artist!='Άγνωστος'].reset_index(drop=True)
    #divide with 'count' to get the me values for all sentiment related columns
    for col in songs_artists.columns:
        if (col not in ['count','artist']):
            songs_artists[col]=songs_artists[col]/songs_artists['count']
    logging.info('perfoming clustering')
    df = perform_kmeans(songs_artists.drop(columns=['artist', 'count']))
    df['artist'] = songs_artists['artist']
    df['count'] = songs_artists['count']
    logging.info('creating visualisation')
    produce_plot(df)
