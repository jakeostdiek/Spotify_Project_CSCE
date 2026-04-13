'''
Using Personal Spotify data from the past year to extract insights into my listening habits.

1. JSON file from spotify to be read in
2. Separate data into duplicated dataframes depending on k insight
3. Sort for most/least listened
4. See what time of day a song is most listened to
'''

import pandas as pd

#load the data
def load_spotify_data(filename):
    #read the json file into a dataframe
    df = pd.read_json(filename)

    # 1. convert timestamp into column of datetime objects
    df['ts'] = pd.to_datetime(df['ts'])

    # 2. convert milliseconds played to minutes
    df['minutes_played'] = df['ms_played'] / 60000

    df = df.rename(columns={
        'master_metadata_album_artist_name': 'artist',
        'master_metadata_track_name': 'track',
        'master_metadata_album_name': 'album',
    })

    return df

def max_heap_creation(df, sort_factor):
    #create a max heap based on the criterion set by user (minutes, entries, etc.)
    pass

def min_heap_creation(df, sort_factor):
    #create a min heap based on the criterion set by user (minutes, entries, etc.)
    pass

#return the top ten songs
def top_ten_songs(df):
    top = []
    #use a max heap to sort the songs by most entries in the dataframe
    #remove the root (top song) 10 times and then songs in top list are the top 10 songs
    pass

def bottom_ten_songs(df):
    bottom = []
    #use a min heap to sort the songs by least entries in dataframe
    #remove the root (bottom song) 10 times and then songs in that list are the bottom 10
    pass

def search_artist(df):
    #data structure???
    #search for an artist and count entries OR minutes listened to return
    pass

def top_5_artist_month(df, month):
    #max heap??
    #user passes in month they want to know their top artists for
    #filters the
    pass


if __name__ == '__main__':
    file_name = 'spotify_data.json'

    # 1. load the data
    spotify_df = load_spotify_data(file_name)