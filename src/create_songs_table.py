import time
import logging
import pandas as pd
from bs4 import BeautifulSoup
from connection_utils import get_data_from_db, make_request, store_df_to_db

logging.getLogger().setLevel(logging.INFO)

def extract_song_id(text):
    "function to extract the song_id"
    text = text.split('&')
    text = [s for s in text if "song_id=" in s]
    song_id=text[0].replace('song_id=','')
    return int(song_id)

def main():
    "creates a artist_songs_info table on a database"
    query = "select * from singers_urls"
    singers_urls_df = get_data_from_db(query)
    # values are well structured, so we can build a df to iteratively get the values of interest
    artist_songs =pd.DataFrame(columns=['artist_name' ,'row_id' ,'song_href' ,'song',
    'lyricist_name', 'composer_name','first_artist_to_sing_the_song' ,'year' ,'upload_date','viewed'])
    for j in range(len(singers_urls_df)):
        name_temp = singers_urls_df['artist'][j]
        logging.info("running for artist: %s", name_temp)
        url_temp = singers_urls_df['href_artist_full'][j]
        k = -1
        page_idx = 1
        while k == -1:
            time.sleep(3)
            url_temp_incr = url_temp + '&kota=' + str(page_idx)
            r = make_request(url_temp_incr)
            try:
                soup = BeautifulSoup(r.content, 'html.parser')
            except Exception as e:
                logging.info("Error while parsing: %s", e)
            elements = soup.find_all('td',{'class':'row1'})
            if len(elements)==0:
                k=1
            else:
                # run throught the elements and save the values in a dataframe
                for i in range(0,len(elements),9):
                    row_id_temp = elements[i].string
                    song_name_temp = elements[i+1].find('a').string
                    song_href_temp = elements[i+1].find('a')['href']
                    lyricist_name_temp = elements[i+2].find('a').string
                    composer_name_temp = elements[i+3].find('a').string
                    first_artist_temp = elements[i+4].find('a').string
                    year_temp = elements[i+5].string
                    date_temp = elements[i+6].string
                    views_temp = elements[i+7].string

                    artist_songs_temp = pd.DataFrame({
                    'artist_name':[name_temp],
                    'row_id':[row_id_temp],
                    'song_href':[song_href_temp],
                    'song':[song_name_temp],
                    'lyricist_name':[lyricist_name_temp],
                    'composer_name':[composer_name_temp],
                    'first_artist_to_sing_the_song':[first_artist_temp],
                    'year':[year_temp],
                    'upload_date':[date_temp],
                    'viewed':[views_temp]})
                    artist_songs = pd.concat([artist_songs, artist_songs_temp])
                page_idx += 1
        logging.info("pages found: %s", page_idx-1)
        artist_songs = artist_songs.reset_index(drop=True)

    artist_songs['song_id'] = artist_songs.apply(lambda x: extract_song_id(x.song_href), axis=1)
    store_df_to_db(artist_songs, 'artist_songs_info')

if __name__=='__main__':
    main()
