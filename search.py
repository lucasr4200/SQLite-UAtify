
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

    keywords = input("Search keywords:\n").lower().split()

    # Build the Query to search for songs
    query = '''
        SELECT 'song' as p_s, sid as id, title, duration
        FROM songs WHERE\n'''

    # Add each keyword into the WHERE clause, chained with OR statements
    for key in keywords:
        query += "lower(title) LIKE '%" + key + "%' OR\n"
    query = query[:-4] + "\nUNION"

    # Union the query with a new query, that searches playlists
    query += '''
        SELECT 'playlist' as p_s, playlists.pid as id, playlists.title, SUM(songs.duration) as duration
        FROM playlists
        INNER JOIN plinclude ON playlists.pid = plinclude.pid
        INNER JOIN songs ON plinclude.sid = songs.sid
        WHERE\n'''

    for key in keywords:
        query += "lower(playlists.title) LIKE '%" + key + "%' OR\n"
    query = query[:-4] + "\nGROUP BY id;"

    print(query + "\n\n")
    cursor.execute(query)
    for row in cursor.fetchall():
        print(row)

    return

def displayResults():
    return



def main():
    createDatabaseConnection('./miniProject1.db')
    searchSongs()

# songs(sid, title, duration)
# playlists(pid, title, uid)

# users(uid, name, pwd)
# sessions(uid, sno, start, end)
# listen(uid, sno, sid, cnt)
# plinclude(pid, sid, sorder)
# artists(aid, name, nationality, pwd)
# perform(aid, sid)
if __name__ == "__main__":
    main()
