import logging
import time
import pandas as pd
from bs4 import BeautifulSoup
from connection_utils import get_data_from_db, make_request, store_df_to_db

logging.getLogger().setLevel(logging.INFO)

def main():
    "creates a song_lyrics table on a database"
    query = "select song_href, song, song_id, count(*) as cnt from artist_songs_info group by 1,2,3"
    songs_to_query = get_data_from_db(query)
    songs_to_query['url'] = 'http://www.stixoi.info/' + songs_to_query['song_href']
    songs = pd.DataFrame(columns=['song_index','song_id','song_href', 'song', 'lyrics'])
    for i in range(len(songs_to_query)):
        logging.info("running for song: %s", songs_to_query.song[i])
        time.sleep(0.5)
        url_temp = songs_to_query.url[i]
        while 1:
            try:
                r = make_request(url_temp)
                break
            except Exception as e:
                logging.info("Error while scraping: %s, putting to sleep for 60 secs", e)
        soup = BeautifulSoup(r.content, 'html.parser')
        lyrics_temp = soup.find_all('div', {'class': 'lyrics'})
        text_temp = lyrics_temp[0].text if len(lyrics_temp) != 0 else None
        song_temp = pd.DataFrame({'song_index':[i],
        'song_id':[songs_to_query.song_id[i]],
        'song_href': [songs_to_query.url[i]],
        'song': [songs_to_query.song[i]],
        'lyrics': [text_temp]})
        songs = pd.concat([songs, song_temp])
        if i%1000 == 0 or i == len(songs_to_query):
            store_df_to_db(songs, 'song_lyrics', 'append')
            songs = pd.DataFrame(columns=songs.columns)

if __name__=='__main__':
    main()
