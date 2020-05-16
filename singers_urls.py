import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
import sqlite3

#database should already exist and include "alphabet_urls" table
cnx = sqlite3.connect('stoixoi_info.db')

#read "alphabet_urls" table
alphabet_urls_df=pd.read_sql("select * from alphabet_urls",cnx)

# define dataframe to store all information
singers_urls_df_all =pd.DataFrame(columns=['href_parent', 'href', 'artist'])

#run loop to get urls for all singers
for j in range(0 ,alphabet_urls_df.shape[0]):
    url =alphabet_urls_df['href_full'][j]
    print('running for ' + alphabet_urls_df['letter'][j] + ':  '+ url)
    page =requests.get(url)
    # define dataframe to store data
    singers_urls_df = pd.DataFrame(columns=['href_parent', 'href', 'artist'])
    if page.status_code==200:
        soup = BeautifulSoup(page.content, 'html.parser')
        elements =soup.find_all('a')
        href_parent_temp =alphabet_urls_df['href'][j]
        for element in elements:
            if ('info=Lyrics' in element['href']) and ('singer_id=' in element['href']):
                singers_urls_df =singers_urls_df.append(pd.DataFrame({'href_parent' :[href_parent_temp],
                                                                 'href' :[element['href']],
                                                                 'artist' :[element.string]}))
        # reset index
        singers_urls_df =singers_urls_df.reset_index(drop=True)

    singers_urls_df_all =singers_urls_df_all.append(singers_urls_df)
    time.sleep(5)

#reset index
singers_urls_df_all=singers_urls_df_all.reset_index(drop=True)
#create full url for each artist
singers_urls_df_all['href_artist_full']='http://www.stixoi.info/'+singers_urls_df_all['href']

#function to extract the singer_id
def singer_id_extract(href):
    url_split=href.split('&')
    matching = [s for s in url_split if "singer_id" in s]
    singer_id=matching[0].replace('singer_id=','')
    return int(singer_id)

singers_urls_df_all['singer_id']=singers_urls_df_all.href.apply(singer_id_extract)

#save df
singers_urls_df_all.to_sql(name='singers_urls', con=cnx,index=False,if_exists='replace')
