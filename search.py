
import os
import sqlite3

connection = None
cursor = None
uid = None


# Below function is important for any program that imports search.py

# Initialises the global variables connection and cursor in this file
#   Use this to make the functions in this file callable from another file
# Without setupSearch(), connection and cursor are None
#   which causes crashes when using any function from this file
def setupSearch(con, cur, userid):
    global connection, cursor, uid

    connection = con
    cursor = cur
    uid = userid

    return


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

    # Print the interface
    clearScreen()
    print("Songs in playlist " + str(pid))
    for row in results:
        print("ID: " + str(row[0]) + "\t " + row[1] + "\t  " + str(row[2]) + 's')
    print("\nSelect a song by typing it's ID, or /exit to exit the program")

    # Get and process input
    while(True):
        command = input("./Uatify$ ")
        if(command == "/exit"):
            closeAndExit()
        for row in results:
            if(command == str(row[0])):
                viewSongs(row[0])


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

    # Print the interface
    clearScreen()
    print("Songs by artist " + results[0][0]) # First collumn of every row has artist name
    for row in results:
        print("ID: " + str(row[1]) + "\t " + row[2] + "\t  " + str(row[3]) + 's')
    print("\nSelect a song by typing it's ID, or /exit to exit the program")

    # Get and process input
    while(True):
        command = input("./Uatify$ ")
        if(command == "/exit"):
            closeAndExit()
        for row in results:
            if(command == str(row[1])):
                viewSongs(row[1])


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
    query = "WITH "
    for i in range(len(keywords)):
        query += "s" + str(i) + "(type, id, title, duration) AS (" + '''
        SELECT 'song', sid, title, duration
        FROM songs
        WHERE lower(title) LIKE \'%''' + keywords[i].lower() + '%\'\n),\n'

        query += "p" + str(i) + "(type, id, title, duration) AS (" + '''
        SELECT 'playlist', playlists.pid, playlists.title, SUM(songs.duration)
        FROM playlists
        INNER JOIN plinclude ON playlists.pid = plinclude.pid
        INNER JOIN songs ON plinclude.sid = songs.sid
        WHERE lower(playlists.title) LIKE \'%''' + keywords[i].lower() + '%\'\nGROUP BY playlists.pid\n),\n'

    query = query[:-2] + '\n SELECT type, id, title, duration FROM (\n'
    for i in range(len(keywords)):
        query += "\tSELECT * FROM s" + str(i) + " UNION ALL SELECT * FROM p" + str(i) + "\nUNION ALL\n"
    query = query[:-10] + ")\nGROUP BY type, id ORDER BY COUNT(*) DESC;"
 

    # Execute the query and display it
    cursor.execute(query)
    displaySearchInterface(keywords, cursor.fetchall(), ['type', 'id', 'title', 'duration'])


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


# Creates the interface to view search results
# Assume Cursor has a query with collumns (type, id, title, duration)
#   keywords: the list of keywords the user searched for
#   results: array of results of the search query
#   cols: the collumns of the query
def displaySearchInterface(keywords, results, collumns):

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
        print("\nWhat would you like to do?\n\t/f or /b to load pages\n\t/exit to exit the system\n\tInput the type and ID of an entry to select it")
        command = input("/UAtify$ ").strip()

        # Process it
        if command == "/exit":
            closeAndExit()
        elif command == "/f":
            if(index <= len(results)-5):
                index += 5
        elif command == "/b":
            if(index >= 5):
                index -= 5

        # Check if the command is a name or title in the results
        for row in results[index:index+5]:
            if(command[0:6] == "artist" and command[7:] == str(row[1])):
                viewArtist(row[1])

            if(command[0:4] == "song" and command[5:] == str(row[1])):
                viewSongs(row[1])

            if(command[0:8] == "playlist" and command[9:] == str(row[1])):
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
    print(title + "\nID: " + str(sid) + "\nPerforming artists:")
    for row in artists:
        print('\t' + row[0])
    print("Featured in playlists:")
    for row in cursor.fetchall():
        print('\t' + row[0])

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
    clearScreen()
    print("Add song with id " + str(sid) + " to a playlist.\nYour playlists are dispayed below")
    for row in playlists:
        print('\tID: ' + str(row[0]) + '  ' + row[1])
    print("\nType a song ID to add the song to a playlist, or\n\t/new [name] to create a new playlist with this song\n\t/cancel to cancel")

    # Get user input
    while(True):
        command = input("./Uatify$ ")
        if(command == "/cancel"):
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
            print("New playlist created with this song!")
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

                print("Song successfully added to playlist!\n")
                return



# Given a song's id, promts the viewer to either
# listen to it, see more info, or add it to a playlist
# Throws a TypeError if sid does not exist in db
def viewSongs(sid):
    global connection, cursor, uid # TODO: GET THE USER'S UID
    
    cursor.execute("SELECT title FROM songs WHERE sid=?", [sid,])
    title = cursor.fetchone()[0]

    prompt = '''\nWhat would you like to do?
        /listen to play it
        /info to see information about it
        /playlist to add it to a playlist
        /exit to exit'''

    clearScreen()
    print("You Selected: " + title + prompt)

    # Get and process user input
    while(True):
        command = input("./Uatify$ ")
        if(command == "/listen"):
            clearScreen()
            print("♪ ♪ ♪ ♪")
            print("Wow that sure was good!")
            closeAndExit()
        elif(command == "/info"):
            clearScreen()
            printSongsInfo(sid)
            print(prompt)
        elif(command == "/playlist"):
            addSongToPlaylist(sid, uid)
            print("You selected: " + title + prompt)
        elif(command == "/exit"):
            closeAndExit()


if __name__ == "__main__":
    connection = sqlite3.connect("./miniProject1.db")
    cursor = connection.cursor()
    
    cursor.execute(' PRAGMA foreign_keys=ON; ')
    connection.commit()

    uid = input("Which user are you? ")
    x = input("Search songs or artists?\n\t/s or /a?\n")
    if(x == "/s"):
        searchSongs()
    elif(x == "/a"):
        searchArtists()

    closeAndExit()
