### Web Scrapper for stixoi.info

This is a web scrapper for stixoi.info page where information related to greek songs are to be found. 

Information like artist names, lyricists and composers as well as lyrics of songs in greek language are fetched and can be used for projects.

Scripts included are fetching processing and storing the files in an SQLite Database in your local folder.

Scripts should run in the following order:

1. artists_first_letter_urls.py
2. singers_urls.py
3. songs_urls.py
4. song_lyrics.py

Data will be stored in stixoi_info.db. In all scripts 'time.sleep' parameters have been set to avoid server overload. 