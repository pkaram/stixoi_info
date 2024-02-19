import logging
import pandas as pd
from bs4 import BeautifulSoup
from connection_utils import store_df_to_db, make_request

URL = "http://www.stixoi.info/stixoi.php?info=Lyrics&act=singer&sort=alpha"
logging.getLogger().setLevel(logging.INFO)

def main():
    "creates a alphabet_urls table on a database"
    r = make_request(URL)
    try:
        soup = BeautifulSoup(r.content, 'html.parser')
    except Exception as e:
        logging.info("Error while parsing: %s", e)
    table_elements=soup.find_all('a',{'class':'letter'})
    href, letter = [], []
    for element in table_elements:
        href.append(element['href'])
        letter.append(element['title'])
    alphabet_urls_df=pd.DataFrame({'href':href,'letter':letter})
    #create the full url for each sub url
    base_url = 'http://www.stixoi.info/'
    alphabet_urls_df['href_full'] = alphabet_urls_df.apply(lambda x: base_url+x.href, axis=1)
    store_df_to_db(alphabet_urls_df, 'alphabet_urls')

if __name__=='__main__':
    main()
