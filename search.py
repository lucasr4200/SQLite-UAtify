
import os
import sqlite3

connection = None
cursor = None

def clearScreen():
    # Clear the output
    if(os.name == "nt"):
        os.system('cls')
    else:
        os.system('clear')
    return


# Creates a database connection
def createDatabaseConnection(databaseFile):
    global connection, cursor

    connection = sqlite3.connect(databaseFile)
    cursor = connection.cursor()
    
    cursor.execute(' PRAGMA foreign_keys=ON; ')
    connection.commit()

    return


# Closes the connection to the DB and exits the program
def closeAndExit():
    connection.close()
    exit()


# Takes input, and creates a query to search songs and playlists for matching keywords
# Calls DisplayResults() to display the query's results
# Assumes connection, cursor are variables that connect to the database
def searchSongs():
    global connection, cursor

    keywords = input("Search keywords:\n").split()


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

    keywords = input("Search keywords:\n").split()

    query = "WITH "
    for i in range(len(keywords)):
        query += '''
        a''' + str(i) + '(type, aid, name, nationality) AS (' + '''
        SELECT 'artist', artists.aid, artists.name, artists.nationality
        FROM artists
        INNER JOIN perform ON artists.aid = perform.aid
        INNER JOIN songs ON perform.sid = songs.sid
        WHERE lower(artists.name) LIKE \'%''' + keywords[i].lower() + '%\' OR lower(songs.title) LIKE \'%' + keywords[i].lower() + '''%\'
        GROUP BY artists.aid
        ),'''

    query = query[:-1] + "\nSELECT t.type, t.aid, t.name, t.nationality, COUNT(DISTINCT perform.sid) as num_songs FROM (\n"
    for i in range(len(keywords)):
        query += "\tSELECT * FROM a" + str(i) + " UNION ALL\n"
    query = query[:-10] + '''\n) as t
    INNER JOIN perform ON t.aid = perform.aid
    GROUP BY t.aid
    ORDER BY COUNT(*)/1.0/num_songs DESC;'''

    cursor.execute(query)
    displaySearchInterface(keywords, cursor.fetchall(), ['type', 'id', 'name', 'nationality', 'songs'])


# Creates the interface to view search results
# Assume Cursor has a query with collumns (type, id, title, duration)
#   keywords: the list of keywords the user searched for
#   results: the results of the query in a list
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
                clearScreen()
                print("You selected artist with ID " + str(row[1]))
                closeAndExit()
            if(command[0:4] == "song" and command[5:] == str(row[1])):
                clearScreen()
                print("You Selected song with ID " + str(row[1]))
                closeAndExit()
            if(command[0:8] == "playlist" and command[9:] == str(row[1])):
                clearScreen()
                print("You Selected playlist with ID " + str(row[1]))
                closeAndExit()


def main():
    global connection, cursor
    createDatabaseConnection('./miniProject1.db')
    x = input("Search songs or artists?\n\t/s or /a?\n")
    if(x == "/s"):
        searchSongs()
    elif(x == "/a"):
        searchArtists()

    closeAndExit()

if __name__ == "__main__":
    main()
