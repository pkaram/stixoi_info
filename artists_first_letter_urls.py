import requests
import pandas as pd
from bs4 import BeautifulSoup
import sqlite3

def main():
    # Create your connection with the database, if not already existing it will be created
    cnx = sqlite3.connect('stoixoi_info.db')

    #url to scrap
    url="http://www.stixoi.info/stixoi.php?info=Lyrics&act=singer&sort=alpha"
    page=requests.get(url)

    if page.status_code==200:
        soup = BeautifulSoup(page.content, 'html.parser')
        #find all letters
        table_elements=soup.find_all('a',{'class':'letter'})

        #define dataframe to store data
        alphabet_urls_df=pd.DataFrame(columns=['href','letter'])
        for element in table_elements:
            alphabet_urls_df=alphabet_urls_df.append(pd.DataFrame({'href':[element['href']],
                                                               'letter':[element['title']]}))

    #reset index
    alphabet_urls_df=alphabet_urls_df.reset_index(drop=True)
    #create the full url for each sub url
    alphabet_urls_df['href_full']='http://www.stixoi.info/'+alphabet_urls_df['href']

    #save data on database
    alphabet_urls_df.to_sql(name='alphabet_urls', con=cnx,index=False,if_exists='replace')

if __name__=='__main__':
    main()