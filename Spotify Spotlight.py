'''
Using Personal Spotify data from the past year to extract insights into my listening habits.

1. JSON file from spotify to be read in
2. Separate data into duplicated dataframes depending on k insight
3. Sort for most/least listened
4. See what time of day a song is most listened to
'''

import pandas as pd
import heapq

#load the data
def load_spotify_data(filename):
    #read the json file into a dataframe
    dataframes = []

    for file in filename:
        df = pd.read_json(file)
        dataframes.append(df)

    #ignore index so the original indices are not kept
    combined_df = pd.concat(dataframes, ignore_index=True)

    # 1. convert timestamp into column of datetime objects
    combined_df['ts'] = pd.to_datetime(combined_df['ts'])

    # 2. convert milliseconds played to minutes
    combined_df['minutes_played'] = combined_df['ms_played'] / 60000

    # 3. get month
    combined_df['month'] = combined_df['ts'].dt.month

    renamed = combined_df.rename(columns={
        'master_metadata_album_artist_name': 'artist',
        'master_metadata_track_name': 'track',
        'master_metadata_album_name': 'album',
    })

    renamed = renamed.drop_duplicates()

    return renamed


def dictionary_songs(df, sort_by):
    if sort_by == 'minutes':
        #group by track, add up minutes, and turn it into dictionary
        return df.groupby('track')['minutes_played'].sum().to_dict()

    elif sort_by == 'appearances':
        #count how many times track appears and turn into dictionary
        return df['track'].value_counts().to_dict()

    else:
        return {}


def dictionary_artists(df, sort_by):
    if sort_by == 'minutes':
        return df.groupby('artist')['minutes_played'].sum().to_dict()

    elif sort_by == 'appearances':
        return df['artist'].value_counts().to_dict()

    else:
        return {}


def get_month(df, month):
    user_month = month


def first_dictionary_songs(df, sort_by):
    #empty dictionary to add data into
    track_song_data = {}
    # for each song entry in the data, grab the track title and minutes
    for i in range(len(df)):
        track = df.iloc[i]['track']
        minutes = df.iloc[i]['minutes_played']
        # adds track and criterion if not already in dictionary
        if track not in song_data:
            # if user wants to know minutes then adds the minutes listened
            if sort_by == 'minutes':
                song_data[track] = minutes
            # if user wants to know number of times, adds 1 to signify 1 entry
            elif sort_by == 'appearances':
                song_data[track] = 1
        # if track already in the song_data dict then adds num. of min or 1 to its value entry
        else:
            if sort_by == 'minutes':
                song_data[track] += minutes
            elif sort_by == 'appearances':
                song_data[track] += 1
    #returns our dictionary of track summaries to use for heap creation
    return track_song_data


def first_dictionary_artists(df, sort_by):
    # empty dictionary to add data into
    artist_song_data = {}

    #for each song entry in the data, grab the artist and minutes
    for i in range(len(df)):
        artist = df.iloc[i]['artist']
        minutes = df.iloc[i]['minutes_played']
        #adds artist and criterion if not already in dictionary
        if artist not in song_data:
            #if user wants to know minutes then adds the minutes listened
            if sort_by == 'minutes':
                song_data[artist] = minutes
            #if user wants to know number of times, adds 1 to signify 1 entry
            elif sort_by == 'appearances':
                song_data[artist] = 1
        #if artist already in the song_data dict then adds num. of min or 1 to its value entry
        else:
            if sort_by == 'minutes':
                song_data[artist] += minutes
            elif sort_by == 'appearances':
                song_data[artist] += 1
    #returns our dictionary to use for heap creation later
    return artist_song_data


def max_heap_creation(df, sort_by, criterion):
    #create a max heap based on the criterion set by user (minutes, entries, etc.)
    heap = []

    if sort_by == 'artist':
        song_data = dictionary_artists(df, criterion)
    elif sort_by == 'track':
        song_data = dictionary_songs(df, criterion)

    for item, value in song_data.items():
        #get the minutes or appearances from dictionary
        heap.append((value, item))

        #sifting up
        index = len(heap) - 1
        while index > 0:
            parent = (index - 1) // 2

            #compare the values and swap if needed
            if heap[index][0] > heap[parent][0]:
                heap[index], heap[parent] = heap[parent], heap[index]
                index = parent
            else:
                # if not bigger, then it is in the correct spot
                break

    return heap


def pop_max_heap(heap):
    # get the top 5 values by popping and sifting next largest to top
    root = heap[0]

    # make the very last element the top now
    heap[0] = heap.pop()

    # sift down
    index = 0
    while True:
        left_child = 2 * index + 1
        right_child = 2 * index + 2
        largest = index

        # check if left child exists and is larger
        if left_child < len(heap) and heap[left_child][0] > heap[largest][0]:
            largest = left_child

        # check if right child exists and is larger
        if right_child < len(heap) and heap[right_child][0] > heap[largest][0]:
            largest = right_child

        # if largest isn't parent, swap em
        if largest != index:
            heap[index], heap[largest] = heap[largest], heap[index]
            index = largest
        else:
            # if parent is larger than both then break
            break

    return root

def pop_min_heap(heap):
    # get the bottom 5 values by popping and sifting
    root = heap[0]

    # make the last element the top
    heap[0] = heap.pop()

    # sift down
    index = 0
    while True:
        left_child = 2 * index + 1
        right_child = 2 * index + 2
        smallest = index

        # check if left child exists and is smaller
        if left_child < len(heap) and heap[left_child][0] < heap[smallest][0]:
            smallest = left_child

        #check if right child exists and is smaller
        if right_child < len(heap) and heap[right_child][0] < heap[smallest][0]:
            smallest = right_child

        # if smallest isn't parent, swap em
        if smallest != index:
            heap[index], heap[smallest] = heap[smallest], heap[index]
            index = smallest
        else:
            break

    return root


def first_max_heap_creation(df, sort_by, criterion):
    #create a max heap based on the criterion set by user (minutes, entries, etc.)
    heap = []

    if sort_by == 'artist':
        song_data = dictionary_artists(df, criterion)
    elif sort_by == 'track':
        song_data = dictionary_songs(df, criterion)

    for track in song_data:
        #get the minutes or appearances from the dictionary function
        value = dictionary_songs(df, sort_by)

        heap.append((value, track))

        index = len(heap) - 1
        while index > 0:
            parent = (index - 1) // 2

            if heap[index][0] > heap[parent][0]:
                #swap the parent and child
                temp = heap[index]
                heap[index] = heap[parent]
                heap[parent] = temp
                index = parent
            else:
                break
    return heap


def min_heap_creation(df, sort_by, criterion):
    #create a min heap based on the criterion set by user (minutes, entries, etc.)
    heap = []

    # essentially same as max
    if sort_by == 'arist':
        song_data = dictionary_artists(df, criterion)
    elif sort_by == 'track':
        song_data = dictionary_songs(df, criterion)

    for item, value in song_data.items():
        heap.append((value, item))

        #sift up
        index = len(heap) - 1
        while index > 0:
            parent = (index - 1) // 2

            # if child is less than parent, swap
            if heap[index][0] < heap[parent][0]:
                heap[index], heap[parent] = heap[parent], heap[index]
                index = parent
            else:
                break

    return heap


#return the top ten songs
def top_5_songs(df, month):
    top = []
    #use a max heap to sort the songs by most entries in the dataframe
    #remove the root (top song) 5 times and then songs in top list are the top 10 songs

    # filter by month
    df_month = df[df['month'] == month]

    # create max heap with 'entries'
    max_heap = max_heap_creation(df_month, criterion='entries')

    # remove the root 5 times
    for i in range(5):
        if max_heap: # make sure it ain't empty
            top.append(heapq.heappop(max_heap)) # What is heapq ????

    return top

def bottom_5_songs(df, month):
    bottom = []
    #use a min heap to sort the songs by least entries in dataframe
    #remove the root (bottom song) 10 times and then songs in that list are the bottom 10

    # filter by month
    df_month = df[df['month'] == month]

    # create min heap with 'entries'
    min_heap = min_heap_creation(df_month, sort_factor='entries')

    # remove the root 5 times
    for i in range(5):
        if min_heap:
            bottom.append(heapq.heappop(min_heap))

    return bottom

def search_artist(df, artist_name):
    #data structure??? Really only need standard filtering here
    #search for an artist and count entries OR minutes listened to return

    # filter for artist (case-sensitive)
    artist_df = df[df['artist'].str.lower() == artist_name.lower()]

    # count entries and total minutes
    total_entries = len(artist_df)
    total_minutes = artist_df['minutes_played'].sum()

    return {
        'artist': artist_name,
        'total_entries': total_entries,
        'total_minutes': total_minutes,
    }

def top_5_artist_month(df, month):
    #max heap??
    #user passes in month they want to know their top artists for
    top = []

    # filter by month
    df_month = df[df['month'] == month]

    # create max heap with 'minutes'
    max_heap = max_heap_creation(df_month, criterion='minutes')

    # create max heap with 'minutes'
    for i in range(5):
        if max_heap:
            top.append(heapq.heappop(max_heap))

    return top



def main_menu(df):
    # display an interactive menu for user
    while True:
        print("\n" + "+++++++++++++++++++++++++")
        print("Specialty Spotify Stats")
        print("+++++++++++++++++++++++++")
        print("1) Find Top 5 Songs in a given month")
        print("2) Find Bottom 5 Songs in a given month")
        print("3) Search for a specific Artist")
        print("4) Find Top 5 Artists in a given month")
        print("5) Quit")
        print("-------------------------")

        option = input("Enter an option (1-5): ")

        # TODO need to figure out the month shit
        if option == "1":
            month = int(input("Enter the month: "))
            print(f"\nFinding top 5 songs for {month}...")
            results = top_5_songs(df, month)
            print(results)

        elif option == "2":
            month = int(input("Enter the month: "))
            print(f"\nFinding bottom 5 songs for {month}...")
            results = bottom_5_songs(df, month)
            print(results)

        elif option == "3":
            artist = input("Enter the name of an artist: ")
            print(f"\nSearching for {artist}...")
            results = search_artist(df, artist)
            print(f"Total Plays: {results['total_entries']}")
            print(f"Total Minutes: {results['total_minutes']:.2f}")

        elif option == "4":
            month = int(input("Enter the month: "))
            print(f"\nFinding top 5 artists for {month}...")
            results = top_5_artist_month(df, month)
            print(results)

        elif option == "5":
            print("\nExiting...")
            break

        else:
            print("\nInvalid input. Please try again.")


if __name__ == '__main__':
    files = [
        'Streaming_History_Audio_2025.json',
        'Streaming_History_Audio_2025_1.json',
        'Streaming_History_Audio_2025_2.json',]

    # 1. load the data
    print("Loading 2025 data...")
    spotify_df = load_spotify_data(files)

    # 2. open menu
    #main_menu(spotify_df)

    print(dictionary_artists(spotify_df, sort_by='appearances'))
