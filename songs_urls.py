import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
import sqlite3

def main():
    #database should already exist and include "alphabet_urls" table
    cnx = sqlite3.connect('stoixoi_info.db')

    singers_urls_df_all=pd.read_sql("select * from singers_urls",cnx)

    # values are well structured, so we can build a df to iteratively get the values of interest
    artist_songs =pd.DataFrame(columns=['artist_name' ,'row_id' ,'song_href' ,'song', 'lyricist_name', 'composer_name',
                                       'first_artist_to_sing_the_song' ,'year' ,'upload_date',
                                       'viewed'])

    # go through all urls of artists from singers_urls_df_all dataframe
    for j in range(0,singers_urls_df_all.shape[0]):
        # save artist's name
        artist_name_temp=singers_urls_df_all['artist'][j]
        print('running for {}'.format(artist_name_temp))
        # store url of the artist
        url_temp =singers_urls_df_all['href_artist_full'][j]

        # start looking in pages
        k=-1
        page_int=1
        while k==-1 :
            # put script to sleep to avoid timeout errors
            time.sleep(3)
            # kota=n_of_page is used as url parameter for page index
            url_temp_incr=url_temp+'&kota='+str(page_int)
            page=requests.get(url_temp_incr)
            soup = BeautifulSoup(page.content,'html.parser')
            # all elements that are stored on the table can be retrieved via row1 class for 'td'
            elements=soup.find_all('td',{'class':'row1'})

            # if no elements are to be found then change value of k and exit the loop
            if len(elements)==0:
                k=1

            # else store all values that will be found inside:
            else:
                # run throught the elements and save the values in a dataframe
                for i in range(0,len( elements),9):
                    # artist_name=None
                    row_id=None
                    song_href=None
                    song=None
                    lyricist_name= None
                    composer_name=None
                    first_artist_to_sing_the_song=None
                    year=None
                    upload_date=None
                    viewed=None

                    element=elements[i]
                    row_id_temp=element.string

                    element=elements[i+1]
                    song_name_temp=element.find('a').string
                    song_href_temp=element.find('a')['href']

                    element=elements[i+2]
                    lyricist_name_temp=element.find('a').string

                    element=elements[i+3]
                    composer_name_temp=element.find('a').string

                    element=elements[i+4]
                    first_artist_temp=element.find('a').string

                    element=elements[i+5]
                    year_temp=element.string

                    element=elements[i+6]
                    date_temp=element.string

                    element=elements[i+7]
                    views_temp=element.string

                    artist_songs=artist_songs.append(pd.DataFrame({'artist_name':[artist_name_temp],
                                                                     'row_id':[row_id_temp],
                                                                     'song_href':[song_href_temp],
                                                                     'song':[song_name_temp],
                                                                     'lyricist_name':[lyricist_name_temp],
                                                                     'composer_name':[composer_name_temp],
                                                                     'first_artist_to_sing_the_song':[first_artist_temp],
                                                                     'year':[year_temp],
                                                                     'upload_date':[date_temp],
                                                                     'viewed':[views_temp]}),
                                                     sort=False)

                page_int+=1


        print('{} pages found'.format(page_int-1))
        artist_songs=artist_songs.reset_index(drop=True)


    #function to extract the song_id
    def song_id_extract(song_href):
        url_split=song_href.split('&')
        matching = [s for s in url_split if "song_id=" in s]
        song_id=matching[0].replace('song_id=','')
        return int(song_id)

    #extract song_id
    artist_songs['song_id']=artist_songs.song_href.apply(song_id_extract)

    #save df
    artist_songs.to_sql(name='artist_songs_info', con=cnx,index=False,if_exists='replace')


if __name__=='__main__':
    main()