
import os
import sqlite3

connection = None
cursor = None
uid = None
sno = None


# Below function is important for any program that imports search.py

# Initialises the global variables connection and cursor in this file
#   Use this to make the functions in this file callable from another file
# Without setupSearch(), connection and cursor are None
#   which causes crashes when using any function from this file
def setupSearch(con, cur, userID, sessionID):
    global connection, cursor, uid, sno

    connection = con
    cursor = cur
    uid = userID
    sno = sessionID

    return

# Closes search session connections
def cleanUpSearch():
    cursor.close()
    connection.close()


# Clears the output in the terminal
def clearScreen():
    if(os.name == "nt"):
        os.system('cls')
    else:
        os.system('clear')
    return


# Closes the connection to the DB and exits the program
def closeAndExit():
    global connection
    connection.close()
    exit()


# Takes a playlist ID and displays all songs in the playlist
# Assumes cursor and connection are variables that connect to the database
def viewPlaylist(pid):
    global cursor, connection

    # Get the playlist from the DB
    query = '''
    SELECT songs.sid, songs.title, songs.duration
    FROM plinclude
    INNER JOIN songs ON plinclude.sid = songs.sid
    WHERE pid = ?;'''

    cursor.execute(query, [str(pid)])
    results = cursor.fetchall()

    # Print the interface and process input
    while(True):

        print("Songs in playlist " + str(pid))
        for row in results:
            print("ID: " + str(row[0]) + "\t " + row[1] + "\t  " + str(row[2]) + 's')
        print("\nSelect a song by typing it's ID, or /back to return to previous screen")

        command = input("./Uatify$ ")

        if(command == "/back"):
            clearScreen()
            return

        # Check if the input matches any song IDs
        for row in results:
            if(command == str(row[0])):
                clearScreen()
                viewSongs(row[0])

        clearScreen()


# Takes an artist's ID and displays all their songs
# Assumes cursor and connection are variables that connect to the database
def viewArtist(aid):
    global cursor, connection

    # Get the artist's songs from the DB
    query = '''
    SELECT artists.name, songs.sid, songs.title, songs.duration
    FROM artists
    INNER JOIN perform ON artists.aid = perform.aid
    INNER JOIN songs ON perform.sid = songs.sid
    WHERE artists.aid = ?;'''

    cursor.execute(query, [str(aid)])
    results = cursor.fetchall()


    # Print the interface and process input
    while(True):

        print("Songs by artist " + results[0][0]) # First collumn of every row has artist name
        for row in results:
            print("ID: " + str(row[1]) + "\t " + row[2] + "\t  " + str(row[3]) + 's')
        print("\nSelect a song by typing it's ID, or /back to return to previous screen")

        command = input("./Uatify$ ")

        if(command == "/back"):
            clearScreen()
            return

        for row in results:
            if(command == str(row[1])):
                clearScreen()
                viewSongs(row[1])

        clearScreen()


# Takes input, and creates a query to search songs and playlists for matching keywords
# Calls DisplayResults() to display the query's results
# Assumes connection, cursor are variables that connect to the database
def searchSongs():
    global connection, cursor

    # Get the input, don't accept empty input
    keywords = ''
    while(keywords == ''):
        keywords = input("Search keywords: ").strip()
    keywords = keywords.split()

    # Build the Query to search for songs
    query = "SELECT * FROM ("
    for i in keywords:
        query += '''
        SELECT 'song' as type, sid as id, title, duration
        FROM songs
        WHERE lower(title) LIKE ?
        UNION ALL

        SELECT 'playlist' as type, playlists.pid as id, playlists.title, SUM(songs.duration)
        FROM playlists
        INNER JOIN plinclude ON playlists.pid = plinclude.pid
        INNER JOIN songs ON plinclude.sid = songs.sid
        WHERE lower(playlists.title) LIKE ?
        GROUP BY playlists.pid
        UNION ALL'''

    query = query[:-9] + ''') as t
    WHERE t.id IS NOT NULL
    GROUP BY t.type, t.id
    ORDER BY COUNT(*) DESC;'''


    # Format the keywords to work with the positional parameters
    # We have ['key1', 'key2']
    # We need ['%key1%', '%key1%', '%key2%', '%key2%']
    formatted = sorted(2*keywords)
    for i in range( len(formatted) ):
        formatted[i] = '%' + formatted[i] + '%'


    # Execute the query and display the results
    cursor.execute(query, formatted)
    displaySearchInterface(keywords, cursor.fetchall(), ['type', 'id', 'title', 'duration'])
    return


# Takes input, and creates a query to search artists and their songs for matching keywords
# Calls DisplayResults() to display the query's results
# Assumes connection, cursor are variables that connect to the database
def searchArtists():
    global connection, cursor

    # Get the input, don't accept empty input
    keywords = ''
    while(keywords == ''):
        keywords = input("Search keywords: ").strip()
    keywords = keywords.split()

    # Create the query
    query = "SELECT 'artist', artists.aid, artists.name, artists.nationality, COUNT(DISTINCT perform.sid) as num_songs FROM ("
    for i in keywords:
        query += '''
        SELECT DISTINCT artists.aid
        FROM artists
        INNER JOIN perform ON artists.aid = perform.aid
        INNER JOIN songs ON perform.sid = songs.sid
        WHERE lower(artists.name) LIKE ? OR lower(songs.title) LIKE ?
        UNION ALL'''

    query = query[:-9] + ''') as t
    INNER JOIN artists ON t.aid = artists.aid
    INNER JOIN perform ON t.aid = perform.aid
    GROUP BY t.aid
    ORDER BY COUNT(*)/num_songs DESC;'''


    # Format the keywords to work with the positional parameters
    # We have ['key1', 'key2']
    # We need ['%key1%', '%key1%', '%key2%', '%key2%']
    formatted = sorted(2*keywords)
    for i in range( len(formatted) ):
        formatted[i] = '%' + formatted[i] + '%'

    cursor.execute(query, formatted)
    displaySearchInterface(keywords, cursor.fetchall(), ['type', 'id', 'name', 'nationality', 'songs'])
    return


# Creates the interface to view search results
# Assume Cursor has a query with collumns (type, id, title, duration)
#   keywords: the list of keywords the user searched for
#   results: array of results of the search query
#   cols: the collumns of the query
def displaySearchInterface(keywords, results, collumns):

    # Index points to the first song to be displayed in the results
    # I.E. rows (index) to (index+5) are displayed at a time
    index = 0
    while(True):
        clearScreen()

        # Print the search keywords & results
        print("Search Results For: " + ' '.join(keywords))
        for row in results[index:index+5]:
            entry = ""
            for i in range(len(collumns)):
                entry += collumns[i] + ": " + str(row[i]) + '\t'
            print(entry)
        print("Displaying page " + str(int(index/5)+1) + " of " + str(int(len(results)/5)+1))

        # Get user input
        print("\nWhat would you like to do?\n\t/f or /b to load pages\n\t/back to return to previous screen\n\tInput the type and ID of an entry to select it")
        command = input("/UAtify$ ").strip()

        # Process it
        if command == "/back":
            clearScreen()
            return
        elif command == "/f":
            if(index <= len(results)-5):
                index += 5
        elif command == "/b":
            if(index >= 5):
                index -= 5

        # Check if the command is a name or title in the results
        for row in results[index:index+5]:
            if(command[0:6] == "artist" and command[7:] == str(row[1])):
                clearScreen()
                viewArtist(row[1])

            if(command[0:4] == "song" and command[5:] == str(row[1])):
                clearScreen()
                viewSongs(row[1])

            if(command[0:8] == "playlist" and command[9:] == str(row[1])):
                clearScreen()
                viewPlaylist(row[1])


# Takes a song ID and prints the id, title, performing artists, and playlists
# Throws: TypeError if sid does not exist in database
def printSongsInfo(sid):
    global connection, cursor

    # First get the title & duration
    query = "SELECT title, duration FROM songs WHERE sid=?;"
    cursor.execute(query, [sid])

    title, duration = cursor.fetchone()

    # Get all the performing artists
    query = '''
        SELECT artists.name
        FROM perform
        INNER JOIN artists ON perform.aid = artists.aid
        WHERE perform.sid = ?;'''

    cursor.execute(query, [sid])
    artists = cursor.fetchall()

    # Then get all the matching playlists
    query = '''
        SELECT playlists.title
        FROM plinclude
        INNER JOIN playlists ON plinclude.pid = playlists.pid
        WHERE plinclude.sid = ?;'''

    cursor.execute(query, [sid])

    # Display it all
    clearScreen()
    print(title + "\nID: " + str(sid) + "\nLength: " + str(duration) + "s" + "\nPerforming artists:")
    for row in artists:
        print('\t' + row[0])
    print("Featured in playlists:")
    for row in cursor.fetchall():
        print('\t' + row[0])

    input("\nEnter anything to return to song selection\n./UAtify$ ")
    clearScreen()
    return


# Display's all of a user's playlists,
# and allows them to add a song to one, or create a new playlist
def addSongToPlaylist(sid, uid):
    global connection, cursor

    # Get this user's playlists
    query = "SELECT pid, title FROM playlists WHERE uid=?;"
    cursor.execute(query, [uid,])
    playlists = cursor.fetchall()

    # Output the interface
    print("Add song with id " + str(sid) + " to a playlist.\nYour playlists are dispayed below")
    for row in playlists:
        print('\tID: ' + str(row[0]) + '  ' + row[1])
    print("\nType a song ID to add the song to a playlist, or\n\t/new [name] to create a new playlist with this song\n\t/cancel to cancel")

    # Get user input
    while(True):
        command = input("./Uatify$ ")

        if(command == "/cancel"):
            clearScreen()
            return

        elif(command[:4] == "/new"):
            # Must first create a new playlist ID
            query = "SELECT MAX(pid) FROM playlists"
            cursor.execute(query)
            newPID = cursor.fetchone()[0] + 1

            query = "INSERT INTO playlists VALUES (?, ?, ?)"
            cursor.execute(query, [ newPID, command[5:], uid ])

            query = "INSERT INTO plinclude VALUES (?, ?, 1)"
            cursor.execute(query, [ newPID, sid ])

            connection.commit()

            clearScreen()
            print("Created playlist " + command[5:] + " with this song!\n")
            return 

        # Check if the input matches a playlist ID
        # If it does, add the song to the playlist
        for row in playlists:
            if(command == str(row[0])):

                # First check that the song is not in the playlist already
                query = " SELECT EXISTS( SELECT * FROM plinclude WHERE pid=? AND sid=?)"
                cursor.execute(query, [ row[0], sid ])

                if(cursor.fetchone()[0] == 1):
                    print("That song is already in this playlist!")
                    continue


                # Get the number of songs in the playlist, for the sorder
                query = "SELECT MAX(sorder) FROM plinclude WHERE pid=?"
                cursor.execute(query, [ row[0] ])

                sorder = cursor.fetchone()[0] + 1

                # Update the database
                query = "INSERT INTO plinclude VALUES (?, ?, ?)"
                cursor.execute(query, [ row[0], sid, sorder])
                connection.commit()

                clearScreen()
                print("Song successfully added to playlist!\n")
                return



# Given a song's id, promts the viewer to either
# listen to it, see more info, or add it to a playlist
# Throws a TypeError if sid does not exist in db
def viewSongs(sid):
    global connection, cursor, uid
    
    cursor.execute("SELECT title FROM songs WHERE sid=?", [sid,])
    title = cursor.fetchone()[0]

    prompt = '''\nWhat would you like to do?
        /listen to play it
        /info to see information about it
        /playlist to add it to a playlist
        /back to return to previous screen'''

    

    # Get and process user input
    while(True):
        global uid, sno

        print("You Selected: " + title + prompt)

        command = input("./Uatify$ ")
        if(command == "/listen"):

            # Get the current song's count from the session table
            cursor.execute("SELECT cnt FROM listen WHERE uid=? AND sno=? AND sid=?", [uid, sno, sid])


            # If the query returns None, the song is not yet in the session, so insert it into the session
            # Otherwise, get the cnt and increment it by 1, and update the table
            cnt = cursor.fetchone()
            if(cnt == None):
                cursor.execute("INSERT INTO listen VALUES (?, ?, ?, 1)", [uid, sno, sid])
            else:
                cnt = cnt[0] + 1
                cursor.execute("UPDATE listen SET cnt=? WHERE uid=? AND sno=? AND sid=?", [cnt, uid, sno, sid])


            connection.commit()

            clearScreen()
            print("♪ ♪ ♪ ♪")
            print("Wow that sure was good!\n")
        elif(command == "/info"):
            printSongsInfo(sid)
        elif(command == "/playlist"):
            clearScreen()
            addSongToPlaylist(sid, uid)
        elif(command == "/back"):
            clearScreen()
            return
        else:
            clearScreen()


if __name__ == "__main__":
    print("This is not the main program! please run main.py!")
    exit()
    # connection = sqlite3.connect("./miniProject1.db")
    # cursor = connection.cursor()
    
    # cursor.execute(' PRAGMA foreign_keys=ON; ')
    # connection.commit()

    # uid = 'u02'
    # sno = 1
    # # listen to song 2 Hotline (cnt=0.9), and song 4 Power (cnt=None)
    # while(True):
    #     x = input("Search songs, artists, or exit?\n\t/s or /a or /e?\n")
    
    #     if(x == "/s"):
    #         searchSongs()
    #     elif(x == "/a"):
    #         searchArtists()
    #     elif(x == "/e"):
    #         break

    # closeAndExit()
