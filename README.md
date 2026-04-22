# Spotify Spotlight: CSCE 311 Final Project

## Project Overview:
This program gives users a way to look into their Spotify listening history in a interactive and personalized way than ever before.

## Dataset:
- Our dataset: downloaded listening history from Spotify.com. Personalized per user.
- What the dataset contains:
  - A JSON file with thousands of entries, one entry representing one song/episode/chapter of a track/podcast/audiobook.
  - One entry looks like this: "{
    "ts": "2025-02-05T00:23:15Z",
    "platform": "ios",
    "ms_played": 892451,
    "conn_country": "US",
    "ip_addr": "2600:1014:b18e:b204:a50f:69ea:e502:bb8d",
    "master_metadata_track_name": null,
    "master_metadata_album_artist_name": null,
    "master_metadata_album_album_name": null,
    "spotify_track_uri": null,
    "episode_name": "James Marsden",
    "episode_show_name": "Armchair Expert with Dax Shepard",
    "spotify_episode_uri": "spotify:episode:12FTez5OfZ3Jdub5oVmMbV",
    "audiobook_title": null,
    "audiobook_uri": null,
    "audiobook_chapter_uri": null,
    "audiobook_chapter_title": null,
    "reason_start": "clickrow",
    "reason_end": "endplay",
    "shuffle": false,
    "skipped": true,
    "offline": false,
    "offline_timestamp": 1738689844,
    "incognito_mode": false
  }"
  - ts is timestamp, ms_played is milliseconds played, and the others are self-explanatory
  - Our problem:
    - Spotify Wrapped is only a once a year feature for users to uncover insights on their listening history. Additionally, Spotify Wrapped does not tell users whether it is counting your "top songs/artists" by how many total minutes you listened to them or by how many times they appear in your listening history. For example, one could have a ton of entries of a specific song in their history, but every time that song comes on they skip it within 5 seconds. So, while this song may have the most appearances in their listening history, they certainly aren't listening to it for the most time of all their songs. Our program solves these issues. Users can interact with our program and filter for specific months, to help glean more specific insights, and tell the program whether to determine top artist/song by minutes listened or by number of entries in their listening history. Our goal is to help Spotify users be more in tune with their listening habits.
  - Our intended users:
    - Music nerds with Spotify accounts and enough listening history to be able to analyze.

## Data Structures:
1. Dictionaries (hash maps)
   - Why used:
     - Since our dataframe has so many variables, we decided to pull the ones we needed most and create dictionaries. This way, when finding top artists or top songs, the only information passed in is the song/artist and either its number of entries or total number of minutes.
     - Also, dictionaries provide fast lookup and easy aggregation (total number of minutes), which is what our program needed.
   - What role:
     - Mapping songs and total number of minutes or times played (entries) through dictionary_songs function
     - Mapping artists and total number of minutes or times played (entries) through dictionary_artists function
     - Mapping in this way allows each song/artist to be attached to a number value to support heap creation later on.
     - Creating a month dictionary that maps each month to its numeric value through get_month function
     - Creating an artist dictionary so that each artist has a total number of entries and minutes in the data that can be easily found (using the build_artist_dict)
   - Why appropriate:
     - Dictionaries provide a time complexity of O(1) making them good for quick access when retrieving values before ranking operations.
     - One limitation of the artist_dict that is created is that it requires a preprocessing step to create this dictionary. However, once created the lookup time of artists is O(1) which is much faster than using the built in Pandas DataFrame features to find an artist, which takes O(n). 
2. Heaps
   - Why used:
     - Heaps support efficient ranking operations by constantly updating so that the root node always contains either the largest or smallest value.
   - What role:
     - Max heaps used to find top 5 songs by month and top 5 artists by month (by popping the root 5 times and thus retrieving the top 5 values)
     - Min heaps used to find bottom 5 songs by month (by popping the root 5 times and thus getting the smallest 5 values)
   - Why appropriate:
     - Heaps allow for efficient extraction of the highest or lowest values by just updating the root node and sifting up as needed. This operation ends up taking O(log n) time complexity and is fairly efficient at doing repeated rankings. 
3. Lists
   - Why used:
     - We used lists to store the values we were popping from each heap in our top/bottom functions. 
   - What role: 
     - In our top/bottom functions we first store an empty list and then append each popped value to the list. 
   - Why appropriate:
     - Lists are mutable and have dynamic growth, making them a prime feature to continually add items to. Especially since we only append 5 items at most to our lists, so each lists allocated space stays somewhat small. Additionally, lists support the addition of tuples, which is what we are appending.
4. Pandas DataFrame
   - This program also uses the Pandas DataFrame to load in the data since it naturally supported structured, tabular data like we have in the JSON files.
   - This DataFrame is the core storage structure for the entire system. It is used to filter by conditions (month/artist or track), convert timestamps into months, convert milliseconds into minutes, perform aggregations (groupby .sum()) for total minutes and entries (len). 
   - Why it was appropriate:
     - This supports large datasets and makes it easy to manipulate and transform our large data. Though, it can be inefficient for searching because it requires scanning/filtering the DataFrame each time. Hence, the build_artist_dict was used to create an artist dictionary early on to avoid scanning the entire DataFrame when a search operation was performed.

## Algorithm Deep Dive:
- Algorithm explored: Heaps
- Explain behavior and tradeoffs:
  - A heap is a complete binary tree stored as an array. A key tradeoff is that heaps don't keep elements fully sorted which makes them faster than full sorting when we only need a few of the top or bottom values.
- Connect heaps directly to how our system uses it:
  - We connected heaps into our system in order to keep track of most or least listened. Explained further in next question.
- Where heaps are in our system:
  - We use heaps in all of our top/bottom functions. So, to find top 5 songs, top 5 artists, and bottom 5 songs each for a given month.
- Why heaps fit our problem:
  - Our problem was to use total entries or total minutes listened to discover the top and bottom 5 values for songs and/or artists. Heaps perfectly fit this problem because they store the largest or smallest value (depending on whether using max or min heaps) at the root node (first index) of their data structure, making it easy to know which song/artist has the largest or smallest entries or minutes played (depending on which the user indicated). Additionally, with heaps only the root node may be deleted, which again fits our use case well. We want to remove the root node (either the largest or smallest value), store this as the top or bottom-most song/artist and then update the heap so that the root node contains the second-largest or second-smallest value. Then, we want to do this process 4 more times, until our top or bottom list has 5 instances and thus we have our top or bottom 5 songs or artists.
- Time complexity and what factors influence performance:
  - Building the heap takes O(n), since we have to insert each value once. Accessing the maximum or minimum value takes O(1) since it is always the root node. Finally, deleting the max/min value takes O(logn) since the value that replaces the root node has to be sifted down, taking O(logn) time. 
  - One factor that influences performance is how big our dictionary that we are making into a heap is. If there are a ton of song entries, then building the heap will take a long time. Another factor that influences performance is how well sorted our values are when they are inputted into the heap. If the values are already sorted by their numeric value in the correct order (e.g., lowest to highest for a min heap) then the deleting time is increased as the replacement node has to be sifted all the way down each time it is replaced. 
- 3 deeper characteristics of heaps:
  - memory usage:
    - Since our heaps use a list-based structure, the memory usage is O(n).
  - stability:
    - Heaps are not very stable. When the root element is deleted, the last element replaces it and is then sifted down until the heap properties are restored. Due to this sifting and replacing, the elements do not stay in their inserted order, and thus the data structure is relatively unstable.
  - how it scales with large datasets:
    - Heaps are efficient for ranking on large datasets. They scale better than full sorting when only the top or bottom certain number of values are needed. For example, in our problem where we only want the top or bottom 5 of each thing, performing a full sort on a large dataset would be highly inefficient since it sorts the values we wouldn't ever need sorted. A heap sorts only one value at a time, and thus performs better when a small number of sorts is needed.
- Limitation/Scenario where heaps perform poorly:
  - Heaps are inefficient when the list is already fully sorted. This negates the time that is saved by storing the min/max element at the top. 

## System Features:
1. Ranking Operation: Top 5 Songs by Month
   - User Input: month, sort method (entries, minutes)
   - Return: Top 5 Songs in the month selected using the sort criteria selected in a user-friendly output (e.g., 1. song - number)
   - Data structure/algorithm: list, heap, dictionary (used in heap function)
2. Ranking Operation: Bottom 5 Songs by Month
   - User Input: month, sort method (entries, minutes)
   - Return: Bottom 5 Songs in the month selected with stat using the sort criteria selected in a user-friendly output (e.g., 1. song - number)
   - Data structure/algorithm: list, heap, dictionary (used in heap function)
3. Search Operation: Artist Lookup
   - User Input: artist name
   - Return: Artist name, total entries, total minutes listened
   - Data structure/algorithm: dictionary, (Pandas DataFrame filtering as fall back) 
4. Filtering Operation: Top 5 Artist by Month
   - All of our ranking operations are also inherently filtering operations as we have the user select the month they want to analyze.
   - User Input: month, sort method (entries, minutes)
   - Return: Top 5 Artists with stat associated (minutes or entries) selected in a user-friendly output (e.g., 1. Artist - Number)
   - Data structure/algorithm: list, heap, dictionary (used in heap function)
5. Comparison Operation (additional):
   - User Input: two artist's names
   - Return: which artist won (or they tied, if applicable) and each artist's stats
   - Data structure/algorithm: dictionaries
6. Aggregation Operation: Overall Summary 
   - User Input: N/A
   - Return: an overall summary of their listening history for the entire year including total entries, total minutes, number of unique artists, number of unique songs, top artist and number of listens, top song and number of listens, top podcast and number of listens.
   - Data structure/algorithm: Pandas DataFrame grouping/aggregation operations

## Compare Two Approaches:
- Feature chosen for comparison: Top 5 Songs by Month ranking system
  - This feature takes a user-selected month and sort criterion and returns the 5 highest-ranked songs. Our current code solves this using a manually built max heap.
  - Approach 1: Full sort using Python's sorted()
    - How it works: The simplest alternative to what we did is to convert the song dictionary into a list of song/value pairs, sort the entire list using Python's sorted() function, and then slice the first 5 items.
    - Tradeoffs: This approach uses Timsort which runs in O(n log(n)) time. The main issue is that is sorts all n songs in the dataset, even though we only are looking for 5 songs total. The extra work spent sorting songs that we do not need makes this approach less efficient as the dataset gets larger, which is a big part of this project.
  - Approach 2: Heapq library with nlargest()
    - How it works: Python's heapq module includes a function, nlargest(), which takes k as an argument, essentially saying "find the top k items". It stores a heap of size k with the largest values, and whenever a value is larger than the heap's minimum, the root, it replaces the root. This way the full dataset does not get stored or sorted.
    - Tradeoffs: This approach runs in O(n log(k)) time, where k would be 5. This simplifies down to just O(n) time which matches our manually built heap's efficiency without needing all of the extra functions we have written.
  - Performance Comparison:
    - Our manually built max heap runs O(n) overall, O(n) to insert the songs one by one, and O(log n) per pop, which simplifies down to O(n). The sorted() approach runs in O(n log(n)) because it full sorts all songs, and nlargest() from heapq runs in O(n log(k)) which simplifies to O(n). In the end, our manually built system matches the performance of nlargest().
    - In terms of implementation, sorted() is by far the simplest, simply inputted the data and returning the top 5 in very few lines of code. Using heapq and nlargest() is nearly as easy, requiring similar length of code but adding in an import line. Our manually built heap is the most complex, spanning four functions and requiring understanding of heap insertion, sift-down, and sift-up operations.
  - Final Choice and Justification:
    - For the purposes of this project, our manually built heap is the right choice for our goal of testing and showing our understanding of how heaps work. Writing a heap from scratch forced us to implement and understand sifting during insertion and sifting after deletion. These operations are what give heaps their efficiency.
    - That being said, as datasets grow, or if we wanted to get lifetime information, the heapq module and nlargest() function would be the better choice. It retains the same O(n) time complexity as our manually built heap and it would be far easier to read and maintain.

## Testing & System Robustness:
- Normal Cases:
  - Entering a valid month like 'January' or artist like 'Mac Miller' successfully returns a ranked list or number of entries.
- Edge Cases:
  - If a month has very few entries. For example, if a month has fewer than 5 songs, our top_5_songs handles this pop_max_heap would return None and we check 'if song' before appending.
  - Searching for an artist with only one entry is valid.
- Invalid Inputs:
  - The menu handles these well. Entering an incorrect month will prompt the user to anter it again, and entering something other than 'entries' or 'minutes' will do the same.
  - Entering an artist name incorrectly is handled the same way as entering an artist that is not present in the dictionary. The dictionary will return None and print 'Artist not found.'
- Unusual/Extreme Inputs:
  - Entering an artist's name with different capitalization is handled due to our artist_dict storing the names as .lower(), and our search_artist calls .lower() as well.
- Scenario where the system performs poorly:
  - If a user were to enter a month, where no songs exist in the data (either no songs listened or only podcasts listened), the heap will be built on an empty dictionary and return an empty list. Due to that, the output would only say "No data found", which is correct, but is not very helpful. For improvement we could offer insight to the user by outputting why no data was found.
- One Limitation:
  - The system requires the user to know the exact artist name as it shows up in Spotify's system. If someone wants to search for 'Tyler the Creator", instead of the correct 'Tyler, the Creator', the artist won't be found.
- What we learned:
  - The most important piece we learned is having strong input validation. Offering examples in the input text and prompting a second time if invalid inputs are given. Working around these issues with try/except blocks in our loops solves this with great ease.
  - There is not much opportunity for guidance when it comes to inputting valid artist names. Again, we did our best by using .lower() and .strip(), but mispelling an artist name is our of our control and up to the user inputting the names.
  - Lastly, our manual heap implementation reinforced our knowledge of how heaps work. When initially concerned with there not being enough data for a certain month, we call, for example, pop_min_heap which would return None if the heap is empty. The function catches this so that it doesn't break completely.
  - 
