
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


# Takes input, and searches all songs and playlists for matching keywords
# Calls DisplayResults() to display the query's results
# Assumptions:
#   Variables connection, cursor have been initialized, and connect to the database
def searchSongs():
    global connection, cursor

    keywords = input("Search keywords:\n").split()


    # Build the Query to search for songs
    query = "WITH "
    for i in range(len(keywords)):
        query += "s" + str(i) + "(type, id, title, duration) AS (" + '''
        SELECT 'song', sid, title, duration
        FROM songs
        WHERE title LIKE \'%''' + keywords[i] + '%\'\n),\n'

        query += "p" + str(i) + "(type, id, title, duration) AS (" + '''
        SELECT 'playlist', playlists.pid, playlists.title, SUM(songs.duration)
        FROM playlists
        INNER JOIN plinclude ON playlists.pid = plinclude.pid
        INNER JOIN songs ON plinclude.sid = songs.sid
        WHERE playlists.title LIKE \'%''' + keywords[i] + '%\'\nGROUP BY playlists.pid\n),\n'

    query = query[:-2] + '\n SELECT type, id, title, duration FROM (\n'
    for i in range(len(keywords)):
        query += "\tSELECT * FROM s" + str(i) + " UNION ALL SELECT * FROM p" + str(i) + "\nUNION ALL\n"
    query = query[:-10] + ")\nGROUP BY type, id ORDER BY COUNT(*) DESC;"
 

    # Execute the query and display it
    cursor.execute(query)
    results = cursor.fetchall()
    displaySearchInterface(keywords, results)


# Creates the interface to view search results
# Assume Cursor has a query with collumns (type, id, title, duration)
#   keywords: the list of keywords the user searched for
#   resutls: the results of the query in a list
def displaySearchInterface(keywords, results):

    index = 0
    while(True):
        clearScreen()

        # Print the search keywords & results
        print("Search Results For: " + ' '.join(keywords))
        for row in results[index:index+5]:
            print(row)
        print("Displaying page " + str(int(index/5)+1) + " of " + str(int(len(results)/5)+1))

        # Get user input
        print("\nWhat would you like to do?\n\t/f or /b to load pages\n\t/new to start a new search\n\texit to exit the system\n\tType the ID to select a song or playlist")
        command = input("/UAtify$ ")

        # Process it
        if command == "exit":
            closeAndExit()
        elif command == "/f":
            if(index <= len(results)-5):
                index += 5
        elif command == "/b":
            if(index >= 5):
                index -= 5
        elif command == "/new":
            clearScreen()
            searchSongs()
            return

        # Check if the command is a title in the results
        for row in results[index:index+5]:
            if(command == row[2]):
                clearScreen()
                print("You selected: " + row[2] + ", with ID: " + str(row[1]))
                closeAndExit()


def main():
    global connection, cursor
    createDatabaseConnection('./miniProject1.db')
    searchSongs()
    closeAndExit()

if __name__ == "__main__":
    main()
