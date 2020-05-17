import pandas as pd
import requests
from bs4 import BeautifulSoup
import sqlite3
import time

# Create your connection with the database
cnx = sqlite3.connect('stoixoi_info.db')

#drop table if it is already existing
c=cnx.cursor()
c.execute('drop table if exists song_lyrics')

#get info on the urls of the songs
artist_songs=pd.read_sql("select * from artist_songs_info",cnx)

#keep columns needed
songs_to_query=artist_songs[['song_href','song','song_id']].drop_duplicates().reset_index(drop=True)

#create full url to call
songs_to_query['url']='http://www.stixoi.info/'+songs_to_query['song_href']

# define function to save values
songs_to_query_save = pd.DataFrame(columns=['song_index','song_id','song_href', 'song', 'lyrics'])

# get lyrics for all songs
text_temp = ''
for i in range(0, songs_to_query.shape[0]):
    print("{x},lyrics for song: {y}".format(x=i, y=songs_to_query.song[i]))
    # put script to sleep
    time.sleep(1)
    #select url to make request
    song_url_temp = songs_to_query.url[i]
    #try to make the request, if not successful, put it to sleep for 1 minute
    while 1:
        try:
            page = requests.get(song_url_temp,timeout=5)
            break
        except:
            print("put to sleep for 60 secs")
            time.sleep(60)
            pass

    #check if request is successful
    if page.status_code==200:
        soup = BeautifulSoup(page.content, 'html.parser')
        lyrics_temp = soup.find_all('div', {'class': 'lyrics'})
        #check if there are lyrics to be found
        if len(lyrics_temp) != 0:
            text_temp = lyrics_temp[0].text
        #save lyrics found
        songs_to_query_save = songs_to_query_save.append(pd.DataFrame({'song_index':[i],
                                                                       'song_id':[songs_to_query.song_id[i]],
                                                                       'song_href': [songs_to_query.url[i]],
                                                                       'song': [songs_to_query.song[i]],
                                                                       'lyrics': [text_temp]}),
                                                         sort=False)
        text_temp = ''
    else:
        #if no lyrics are found set None
        songs_to_query_save = songs_to_query_save.append(pd.DataFrame({'song_index':[i],
                                                                       'song_id': [songs_to_query.song_id[i]],
                                                                       'song_href': [songs_to_query.url[i]],
                                                                       'song': [songs_to_query.song[i]],
                                                                       'lyrics': [None]}),
                                                         sort=False)

    #every 1000 calls write the song lyrics found
    if songs_to_query_save.shape[0]%1000==0 or i==(songs_to_query.shape[0]-1):
        #append batch of lyrics to table
        songs_to_query_save.to_sql(name='song_lyrics', con=cnx, index=False, if_exists='append')
        #initialize again the df to store the next batch
        songs_to_query_save = pd.DataFrame(columns=['song_index','song_id','song_href', 'song', 'lyrics'])
