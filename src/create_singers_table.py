import re
import time
import logging
import pandas as pd
from bs4 import BeautifulSoup
from connection_utils import store_df_to_db, get_data_from_db, make_request

logging.getLogger().setLevel(logging.INFO)

def extract_signer_id(text):
    text = text.split('&')
    text = [s for s in text if "singer_id" in s]
    singer_id = text[0].replace('singer_id=','')
    return int(singer_id)

def main():
    "creates a singers_urls table on a database"
    query = "select * from alphabet_urls"
    alphabet_urls_df = get_data_from_db(query)
    # define dataframe to store all information
    singers_df = pd.DataFrame(columns=['href_parent', 'href', 'artist'])
    for j in range(len(alphabet_urls_df)):
        url = alphabet_urls_df['href_full'][j]
        logging.info("scraping url: %s", url)
        r = make_request(url)
        try:
            soup = BeautifulSoup(r.content, 'html.parser')
        except Exception as e:
            logging.info("Error while parsing: %s", e)
        elements = soup.find_all('a')
        href_parent_temp = alphabet_urls_df['href'][j]
        href_parent,href,artist = [],[],[]
        for e in elements:
            if bool(re.search('info=Lyrics', e.get('href'))) and bool(re.search('singer_id=', e.get('href'))):
                href_parent.append(href_parent_temp)
                href.append(e.get('href'))
                artist.append(e.string)
        singers_df_temp = pd.DataFrame({
            'href_parent':href_parent,
            'href':href,
            'artist':artist
        })
        singers_df = pd.concat([singers_df, singers_df_temp])
        time.sleep(5)
    singers_df = singers_df.reset_index(drop=True)
    singers_df['href_artist_full'] = 'http://www.stixoi.info/'+ singers_df['href']
    singers_df['singer_id'] = singers_df.apply(lambda x: extract_signer_id(x.href), axis=1)
    store_df_to_db(singers_df, 'singers_urls')

if __name__=='__main__':
    main()
