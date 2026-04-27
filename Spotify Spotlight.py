'''
Using Personal Spotify data from the past year to extract insights into my listening habits.
Names: Cassie Nesheim and Jake Ostdiek
'''

import pandas as pd

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

def print_clean(results, title):
    print("\n" + title)
    print("-------------")
    if len(results) == 0:
        print("No data found.")
    for i in range(len(results)):
        value, item = results[i]
        print(f"{i+1}. {item} - {value}")


def dictionary_songs(df, sort_by):
    # combine with 'track' and 'artist', checking to make sure not null
    df = df[df['track'].notna() & df['artist'].notna()]

    #  create a new column adding them into one string
    df = df.copy()
    df['track_artist'] = df['track'] + " by " + df['artist']

    if sort_by == 'minutes':
        #group by track, add up minutes, and turn it into dictionary
        return df.groupby('track_artist')['minutes_played'].sum().to_dict()
    elif sort_by == 'entries':
        #count how many times track appears and turn into dictionary
        return df['track_artist'].value_counts().to_dict()
    else:
        return {}


def dictionary_artists(df, sort_by):
    if sort_by == 'minutes':
        return df.groupby('artist')['minutes_played'].sum().to_dict()
    elif sort_by == 'entries':
        return df['artist'].value_counts().to_dict()
    else:
        return {}

def build_artist_dict(df):
    artist_dict = {}

    artist_grouped_df = df.groupby('artist')

    for artist, group in artist_grouped_df:
        artist_dict[artist.lower()] = {
            'total_entries': len(group),
            'total_minutes': group['minutes_played'].sum(),
        }

    return artist_dict

def get_month(month):
    user_month = month.lower().strip()
    months = {
        "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6, "july": 7,
        "august": 8, "september": 9, "october": 10, "november": 11, "december": 12
    }
    month = months[user_month]

    return month

#approved by instructor to use this as our sorting algorithm
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

#approved by instructor to use this as sorting algorithm
def min_heap_creation(df, sort_by, criterion):
    #create a min heap based on the criterion set by user (minutes, entries, etc.)
    heap = []

    # essentially same as max
    if sort_by == 'artist':
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

def pop_max_heap(heap):
    # get the top value by popping and return to heap by sifting next largest to top
    if len(heap) == 0:
        return None

    root = heap[0]

    if len(heap) == 1:
        heap.pop()
        return root

    # make the very last element the top now
    heap[0] = heap.pop()

    # sift down
    parent = 0
    while True:
        left_child = 2 * parent + 1
        right_child = 2 * parent + 2
        largest = parent

        # check if left child exists and is larger
        if left_child < len(heap) and heap[left_child][0] > heap[largest][0]:
            largest = left_child

        # check if right child exists and is larger
        if right_child < len(heap) and heap[right_child][0] > heap[largest][0]:
            largest = right_child

        # if largest isn't parent, swap em
        if largest != parent:
            heap[parent], heap[largest] = heap[largest], heap[parent]
            parent = largest
        else:
            # if parent is larger than both then break
            break

    return root

def pop_min_heap(heap):
    if len(heap) == 0:
        return None
    #get the bottom value by popping and return to min heap by sifting next smallest to top
    root = heap[0]

    if len(heap) == 1:
        heap.pop()
        return root

    # make the last element the top
    heap[0] = heap.pop()

    # sift down
    parent = 0
    while True:
        left_child = 2 * parent + 1
        right_child = 2 * parent + 2
        smallest = parent

        # check if left child exists and is smaller
        if left_child < len(heap) and heap[left_child][0] < heap[smallest][0]:
            smallest = left_child

        #check if right child exists and is smaller
        if right_child < len(heap) and heap[right_child][0] < heap[smallest][0]:
            smallest = right_child

        # if smallest isn't parent, swap em
        if smallest != parent:
            heap[parent], heap[smallest] = heap[smallest], heap[parent]
            parent = smallest
        else:
            break

    return root

#return the top ten songs
def top_5_songs(df, month, criterion):
    top = []
    #use a max heap to sort the songs by most entries in the dataframe
    #remove the root (top song) 5 times and then songs in top list are the top 10 songs

    # filter by month
    df_month = df[df['month'] == month]

    # create max heap with 'entries'
    max_heap = max_heap_creation(df_month, sort_by='track', criterion=criterion)

    # remove the root 5 times
    for i in range(5):
        song = pop_max_heap(max_heap)
        if song:
            top.append(song)

    return top

def bottom_5_songs(df, month, criterion):
    bottom = []
    # filter by month
    df_month = df[df['month'] == month]

    # create dictionary {track: value} based on chosen criterion
    song_data = dictionary_songs(df_month, criterion)

    #sorts the data by values in the dictionary lowest to highest (lambda x: x[1] just retrieves the value for each song)
    sorted_songs = sorted(song_data.items(), key=lambda x: x[1])

    #returns the first 5 songs (first 5 = the lowest 5 values)
    return sorted_songs[:5]

def search_artist(df, artist_name, artist_dict=None):
   #use the artist dictionary created to find artist and return values
    if artist_dict is not None:
        artist_name = artist_name.lower().strip()
        #if the artist is not in the dictionary, it is not in listening history so there is no data
        if artist_name not in artist_dict:
            return None
        #search dictionary with artist_name as key
        data = artist_dict[artist_name]
        return {
            'artist': artist_name,
            'total_entries': data['total_entries'],
            'total_minutes': data['total_minutes']
        }
    #if for some reason the artist is not in the artist_dict, use pandas filtering to find artist
    artist_df = df[df['artist'].str.lower() == artist_name.lower()]
    if artist_df.empty:
        return None
    return{
        'artist': artist_name,
        'total_entries': len(artist_df),
        'total_minutes': artist_df['total_minutes'].sum(),
    }

def top_5_artist_month(df, month, criterion):
    #user passes in month they want to know their top artists for
    top = []

    # filter by month
    df_month = df[df['month'] == month]

    # create max heap with 'minutes'
    max_heap = max_heap_creation(df_month, sort_by='artist', criterion=criterion)

    # create max heap with 'minutes'
    for i in range(5):
        if max_heap:
            top.append(pop_max_heap(max_heap))

    return top

def compare_artists(artist_dict, artist_name1, artist_name2):
    result1 = artist_dict.get(artist_name1.lower().strip())
    result2 = artist_dict.get(artist_name2.lower().strip())

    if result1 is None:
        return(f"{artist_name1} not found. Try again.")
    if result2 is None:
        return(f"{artist_name2} not found. Try again.")

    artist1_entries = result1['total_entries']
    artist1_minutes = result1['total_minutes']
    artist2_entries = result2['total_entries']
    artist2_minutes = result2['total_minutes']

   #case 1: artist 1 wins both entries and minutes
    if (artist1_entries > artist2_entries) and (artist1_minutes > artist2_minutes):
        return(f"{artist_name1} wins!\n"
               f"{artist_name1}: {artist1_minutes:.2f} total minutes, {artist1_entries} total entries.\n"
               f"{artist_name2}: {artist2_minutes:.2f} total minutes, {artist2_entries} total entries.")
    #case 2: artist 2 wins both entries and minutes
    elif (artist1_entries < artist2_entries) and (artist1_minutes < artist2_minutes):
        return(f"{artist_name2} wins!\n"
               f"{artist_name1}: {artist1_minutes:.2f} total minutes, {artist1_entries} total entries.\n"
               f"{artist_name2}: {artist2_minutes:.2f} total minutes, {artist2_entries} total entries.")
    #case 3: tied (artist 1 higher minutes, artist 2 higher entries)
    elif (artist1_entries < artist2_entries) and (artist1_minutes > artist2_minutes):
        return(f"{artist_name1} and {artist_name2} tie!\n"
               f"{artist_name1} has more total minutes ({artist1_minutes:.2f})\n"
               f"{artist_name2} has more total entries ({artist2_entries}).")
    #case 4: tied (artist 1 higher entries, artist 2 higher minutes)
    elif (artist1_entries > artist2_entries) and (artist1_minutes < artist2_minutes):
        return(f"{artist_name1} and {artist_name2} tie!\n"
               f"{artist_name1} has more total entries ({artist1_entries}).\n"
               f"{artist_name2} has more total minutes ({artist2_minutes:.2f}).")
    else:
        return(f"Results are tied or very close.\n"
               f"{artist_name1}: {artist1_minutes:.2f} total minutes, {artist1_entries} total entries.\n"
               f"{artist_name2}: {artist2_minutes:.2f} total minutes, {artist2_entries} total entries.")

def overall_summary(df):
    if df.empty:
        return "No data found."
    total_entries = len(df)
    total_minutes = df['minutes_played'].sum()

    total_artists = len(df['artist'].unique())
    total_tracks = len(df['track'].unique())

    songs_df = df[df['track'].notna()]
    if not songs_df.empty:
        top_artist = songs_df['artist'].value_counts().idxmax()
        top_artist_count = songs_df['artist'].value_counts().max()
        top_track = songs_df['track'].value_counts().idxmax()
        top_track_count = songs_df['track'].value_counts().max()
    else:
        top_artist = 'N/A'
        top_artist_count = 'N/A'
        top_track = 'N/A'
        top_track_count = 'N/A'

    podcast_df = df[df['episode_show_name'].notna()]
    if not podcast_df.empty:
        top_podcast = podcast_df['episode_show_name'].value_counts().idxmax()
        top_podcast_count = podcast_df['episode_show_name'].value_counts().max()
    else:
        top_podcast = 'N/A'
        top_podcast_count = 'N/A'

    return(
        f"Summary of your listening history for this year:\n"
        f"---------------------------------------------------\n"
        f"Total number of songs/podcasts: {total_entries}\n"
        f"Total minutes listened: {total_minutes}\n"
        f"Total number of unique artists: {total_artists}\n"
        f"Total number of unique songs: {total_tracks}\n"
        f"Top artist: {top_artist}, {top_artist_count} listens\n"
        f"Top song: {top_track}, {top_track_count} listens\n"
        f"Top podcast: {top_podcast}, {top_podcast_count} listens\n"
    )

def main_menu(df):
    # display an interactive menu for user
    while True:
        print("\n" + "+++++++++++++++++++++++++")
        print("Specialty Spotify Stats")
        print("+++++++++++++++++++++++++")
        print("1) Find your Top 5 Songs in a given month")
        print("2) Find your Bottom 5 Songs in a given month")
        print("3) Search for a specific artist in your listening history")
        print("4) Find your Top 5 Artists in a given month")
        print("5) Compare two artists to see who you listen to more")
        print("6) Get an overall listening history summary for your entire year")
        print("7) Quit")
        print("-------------------------")

        option = input("Enter an option (1-7): ")

        #
        if option == "1":
            while True:
                user_sort = input("Do you want to sort by entries or minutes listened? Enter either 'entries' or 'minutes': ")
                sort_method = user_sort.lower().strip()
                if sort_method not in ['entries', 'minutes']:
                    print("Sort method must be either 'entries' or 'minutes'. Please try again.")
                    continue
                user_month = input("Enter the full month name (e.g., January): ")
                month = user_month.lower().strip()
                try:
                    num_month = get_month(month)
                    break
                except Exception:
                    print("Invalid month. Please try again.")
            print(f"\nFinding top 5 songs for {user_month}...")
            results = top_5_songs(df, month=num_month, criterion=sort_method)
            print_clean(results, f"Top 5 songs in {user_month} by {sort_method}:")


        elif option == "2":
            while True:
                user_sort = input(
                    "Do you want to sort by entries or minutes listened? Enter either 'entries' or 'minutes': ")
                sort_method = user_sort.lower().strip()
                if sort_method not in ['entries', 'minutes']:
                    print("Sort method must be either 'entries' or 'minutes'. Please try again.")
                    continue
                user_month = input("Enter the full month name (e.g., January): ")
                month = user_month.lower().strip()
                try:
                    num_month = get_month(month)
                    break
                except Exception:
                    print("Invalid month. Please try again.")
            print(f"\nFinding bottom 5 songs for {user_month}...")
            results = bottom_5_songs(df, month=num_month, criterion=sort_method)
            print_clean(results, "Bottom 5 songs:")


        elif option == "3":
            artist = input("Enter the full artist name (e.g., Mac Miller): ")
            result = search_artist(df, artist, artist_dict)
            print(f"\nSearching for {artist}...\n")
            if result is None:
                print("Artist not found. Please try again.")
            else:
                print(f"{artist} found! Summary:")
                print(f"Total Plays: {result['total_entries']}")
                print(f"Total Minutes: {result['total_minutes']:.2f}")


        elif option == "4":
            while True:
                user_sort = input(
                    "Do you want to sort by entries or minutes listened? Enter either 'entries' or 'minutes': ")
                sort_method = user_sort.lower().strip()
                if sort_method not in ['entries', 'minutes']:
                    print("Sort method must be either 'entries' or 'minutes'. Please try again.")
                    continue
                user_month = input("Enter the full month name (e.g., January): ")
                month = user_month.lower().strip()
                try:
                    num_month = get_month(month)
                    break
                except Exception:
                    print("Invalid month. Please try again.")
            print(f"\nFinding top 5 artists for {user_month}...")
            results = top_5_artist_month(df, month=num_month, criterion=sort_method)
            print_clean(results, f"Top 5 artists in {user_month}:")


        elif option == "5":
            while True:
                first_artist = input("Enter the first artist's full name (e.g., Mac Miller): ")
                second_artist = input("Enter the second artist's full name (e.g., Mac Miller): ")
                try:
                    result = compare_artists(artist_dict, first_artist, second_artist)
                    print(result)
                    break
                except Exception:
                    print(f"{first_artist} or {second_artist} or both were not found. Please try again.")
                    continue
            print()


        elif option == "6":
            result = overall_summary(df)
            print(result)


        elif option == "7":
            print("\nExiting...")
            break

        else:
            print("\nInvalid input. Please try again.")
            continue

        if option in ["1", "2", "3", "4", "5", "6"]:
            input("\nPress Enter to continue...")


if __name__ == '__main__':
    files = [
        'Streaming_History_Audio_2025.json',
        'Streaming_History_Audio_2025_1.json',
        'Streaming_History_Audio_2025_2.json',]

    # 1. load the data
    print("Loading 2025 data...")
    spotify_df = load_spotify_data(files)
    artist_dict = build_artist_dict(spotify_df)

    # 2. open menu
    main_menu(spotify_df)
