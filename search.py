
import os
import sqlite3

connection = None
cursor = None

# Creates a database connection
def createDatabaseConnection(databaseFile):
    global connection, cursor

    connection = sqlite3.connect(databaseFile)
    cursor = connection.cursor()
    
    cursor.execute(' PRAGMA foreign_keys=ON; ')
    connection.commit()

    return

# Takes input, and searches all songs and playlists for matching keywords
# Calls DisplayResults() to display the query's results
# Assumptions:
#   Variables connection, cursor have been initialized, and connect to the database
def searchSongs():
    global connection, cursor

    keywords = input("Search keywords:\n").split()

    # Build the Query to search for songs
    query = '''
        SELECT 'song' as type, sid as id, title, duration
        FROM songs WHERE '''

    # Add each keyword into the WHERE clause, chained with OR statements
    for key in keywords:
        query += "lower(title) LIKE '%" + key.lower() + "%' OR\n"
    query = query[:-4] + "\nUNION"

    # Union the query with a new query, that searches playlists
    query += '''
        SELECT 'playlist' as type, playlists.pid as id, playlists.title, SUM(songs.duration) as duration
        FROM playlists
        INNER JOIN plinclude ON playlists.pid = plinclude.pid
        INNER JOIN songs ON plinclude.sid = songs.sid
        WHERE '''

    for key in keywords:
        query += "lower(playlists.title) LIKE '%" + key + "%' OR\n"
    query = query[:-4] + "\nGROUP BY id;"

    cursor.execute(query)
    results = cursor.fetchall()
    displaySearchInterface(keywords, results)



# Creates the interface to view search results
# Assume Cursor has a query with collumns (type, id, title, duration)
# Uses printSearchScreen
# Parameters:
#   keywords: the list of keywords the user searched for
#   resutls: the results of the query in a list
def displaySearchInterface(keywords, results):

    index = 0
    while(True):
        
        # Clear the output =
        if(os.name == "nt"):
            os.system('cls')
        else:
            os.system('clear')

        # Print the search keywords & results
        print("Search Results For: " + ' '.join(keywords))
        for row in results[index:index+5]:
            print(row)
        print("Displaying page " + str(int(index/5)+1) + " of " + str(int(len(results)/5)+1))

        # Get user input
        print("\nWhat would you like to do?\n\t/f or /b to load pages\n\texit to exit the system\n\tType the ID to select a song or playlist")
        command = input("/UAtify$ ")

        # Process it
        if command == "exit":
            exit()
        elif command == "/f":
            if(index <= len(results)-5):
                index += 5
        elif command == "/b":
            if(index >= 5):
                index -= 5


def main():
    global connection, cursor
    createDatabaseConnection('./miniProject1.db')
    searchSongs()

    close(connection)

if __name__ == "__main__":
    main()
