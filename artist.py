'''
[] Searches and comparisons are case insensitive [use .lower()]
[] Protect against SQL injections [use connection.prepareStatement()]
[] Ensure database can be passed as a command line argument
[L] Make password non-visible while typing
[] Option to exit the program from login screen
[] Show user options on login
[] Combine our work together

'''

import main

#Artist should be able to add a song by providing Title and Duration
# Needed schema:
#   songs(sid, title, duration)
#   perform(aid, sid)
def publishSong(aid):
    #connect
    connection = createDatabaseConnection(databasefile)
    cursor = connection.cursor()

    #get title & duration
    title = input("Please input song title:")
    duration = input("Please enter song duration [MM:SS] :")


    #check if song already exists
    query = f"SELECT * FROM songs s" \
            f" WHERE s.title == ? AND s.duration == ?;" , (title, duration)
    cursor.execute(query)

    exists = cursor.fetchall()
    response = ""

    #warn the artist and give option to add it again
    while exists and not response.lower() == ("y" or "n"):
        #warn the user, reject request
        warning = "Your song with this title and duration already exists in the system. Are you sure you want to create it again? Y/N"
        response = input(warning)
        if (response.lower() == "y"):
            addSongToDB(cursor, title, duration, aid)
        elif (response.lower() == "n"):
            print("Song not added")

    addSongToDB(cursor, title, duration, aid)

#add song to database
def addSongToDB(cursor, title, duration, aid):
    #get artist collab
    artists = [aid]
    collab = ""
    collabPrompt = "Would you like to add another artist to this song? y/N"
    while collab != 'n':
        collab = input(collabPrompt)
        collab = collab.lower()
        if collab == 'y':
            addArtist = input("Input the collaborating artist's aid:")
            cursor.execute("SELECT aid FROM artists WHERE aid == ?", (addArtist))
            if (cursor.fetch()):
                artists.append(addArtist)
                print("Artist added")
            else:
                print("Invalid aid")

    #get new sid
    sidQuery = "SELECT MAX(sid) FROM songs;"
    cursor.execute(sidQuery)
    max = cursor.fetchall()
    ++max
    #add song to database
    songQuery = "INSERT INTO songs VALUES (?,?,?);"
    performQuery = "INSERT INTO perform VALUES (?,?);"
    cursor.execute(songQuery, (max, title, duration, aid))
    #add collabs (if any) to perform
    for id in artists:
        cursor.execute(performQuery, (max, id))
    print(f"Song ? ? has been added successfully.", (title, duration))

#Artist should be able to find top Fans & Playlists
# Top 3 Fans by artist duration listened
# if there are not >3, return less
def biggestFans(aid):
    pass

# Top 3 Playlists by number of artist songs included
# if there are not >3, return less
def topPlaylists(aid):
    pass


if __name__ == '__main__':
    pass

