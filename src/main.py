"""
Script to build the database. Order of modules run is important since some calls are based on data 
that have been already saved
"""
import create_alphabet_table as create_alphabet_table
import create_singers_table as create_singers_table
import create_songs_table as create_songs_table
import create_lyrics_table as create_lyrics_table

def main():
    create_alphabet_table.main()
    create_singers_table.main()
    create_songs_table.main()
    create_lyrics_table.main()

if __name__=='___main__':
    main()
