#script to build the database
import artists_first_letter_urls
import singers_urls
import songs_urls
import song_lyrics

def main():
    #order of modules run is important since some calls are based on data that have been already saved
    artists_first_letter_urls.main()
    singers_urls.main()
    songs_urls.main()
    song_lyrics.main()


if __name__=='___main__':
    main()
