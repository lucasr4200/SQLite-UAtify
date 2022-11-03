import sqlite3
import random
from sqlite3 import Error
import getpass
import os
import search
import artist
import sys


# Code from group member Jonathen Adsit
def clearScreen():
    # Clear the output
    if (os.name == "nt"):
        os.system('cls')
    else:
        os.system('clear')
    return


# Creates a database connection
def createDatabaseConnection(databaseFile):
    connection = None
    try:
        connection = sqlite3.connect(databaseFile)
    except Error as error:
        print(error)
    finally:
        if connection:
            connection.close()


def login(databaseFile):
    # Decide whether to activate user or artist login
    userOrArtist = input("Would you like to log in as a user, artist or signup? u/a/s: ")

    if userOrArtist == "u":
        uidEntered = input("Input uid: ")
        passwordEntered = getpass.getpass("Input password: ")

        connection = sqlite3.connect(databaseFile)
        cur = connection.cursor()
        cur.execute(f"SELECT u.uid, u.name FROM users u" \
                    f" WHERE u.uid = '{uidEntered}' AND u.pwd = '{passwordEntered}';")
        result = cur.fetchall()
        if result:
            for row in result:
                print("Welcome:", row[1])
        else:
            print("Login failed")
            connection.close()
            x = input("Would you like to try again? y/n: ")
            if x == "y":
                result = login(databaseFile)
            else:
                print("Goodbye!")
                exit()

        # add to list if login type is user
        result.append("user")

        return result

    elif userOrArtist == "a":
        aidEntered = input("Input aid: ")
        passwordEntered = getpass.getpass("Input password: ")

        connection = sqlite3.connect(databaseFile)
        cur = connection.cursor()
        # query = f"SELECT a.aid, a.name FROM artists a" \
        #     f" WHERE a.aid = '{aidEntered}' AND a.pwd = '{passwordEntered}';"
        cur.execute(f"SELECT a.aid, a.name FROM artists a" \
                    f" WHERE a.aid = '{aidEntered}' AND a.pwd = '{passwordEntered}';")

        result = cur.fetchall()
        if result:
            for row in result:
                print("Welcome:", row[1])
        else:
            connection.close()
            print("Login failed")
            x = input("Would you like to try again? y/n: ")
            if x == "y":
                result = login(databaseFile)
            else:
                print("Goodbye!")
                exit()

        # add to list if login type is user
        result.append("artist")

        return result

    elif userOrArtist == "s":
        connection = sqlite3.connect(databaseFile)
        cur = connection.cursor()
        newuid = input("Enter uid: ")
        newName = input("Enter name: ")
        newPassword = input("Enter password: ")

        connection.execute(f"INSERT into users(uid, name, pwd) VALUES (?,?,?)", (newuid, newName, newPassword))

        connection.commit()
        connection.close()

        return login(databaseFile)
    elif userOrArtist == "exit":
        exit()
    else:
        print("Neither answer selected")
        login(databaseFile)


def startSession(id):
    connection = sqlite3.connect(databaseFile)
    sno = random.randint(0, 100000)

    # Start a session by inserting values into  sessions table, initialize the end date as a NULL value
    connection.execute(f"INSERT into sessions(uid, sno, start, end) VALUES (?,?, date('now'), Null)", (id, sno))
    connection.commit()
    connection.close()

    return sno


def endSession(id, sno):
    connection = sqlite3.connect(databaseFile)
    cur = connection.cursor()

    cur.execute(f"SELECT s.sno, s.start, s.uid FROM sessions s, users u" \
                f" WHERE s.uid = u.uid;")
    # y is a temporary variable to store the results of the query
    y = cur.fetchall()

    # update the sessions table to include coresponding end date
    updateSessions(connection, (id, sno, y[0][1]))

    connection.close()


def updateSessions(connection, data):
    # function to update the sessions table

    connection.execute(f" UPDATE sessions "
                       f"set uid = ?,"
                       f"sno = ?,"
                       f"start = ?,"
                       f"end = date('now')"
                       f"WHERE sno = ?"
                       , (data[0], data[1], data[2], data[1]))

    connection.commit()


if __name__ == '__main__':

    # Main loop for running program
    while 1:
        if len(sys.argv) > 1:
            databaseFile = sys.argv[1]
        else:
            databaseFile = "./miniProject1.db"
        createDatabaseConnection(databaseFile)

        # data stores id, loginType
        data = login(databaseFile)

        clearScreen()

        # Establish login type
        if data[1] == "user":
            loginType = "user"
        else:
            loginType = "artist"

        # set logout initially
        logout = False

        if loginType == "artist":
            artist.artistInterface(databaseFile, data[0][0])
        else:
            while 1:          
                # Start session here
                sno = startSession(data[0][0])
                randomInput = input("Whatever input:")

                if randomInput == "logout":
                    endSession(data[0][0], sno)
                    # end session here
                    logout = True
                if randomInput == "exit":
                    # end session here as well
                    # is exit is entered break out of the inner loop
                    endSession(data[0][0], sno)
                    break
                # search for songs using function from search.py
                if randomInput == "search songs":
                    search.setupSearch(sqlite3.connect(databaseFile), sqlite3.connect(databaseFile).cursor(), data[0][0], sno)
                    search.searchSongs()
                # search for artists using function from search.py
                if randomInput == "search artists":
                    search.setupSearch(sqlite3.connect(databaseFile), sqlite3.connect(databaseFile).cursor(), data[0][0],sno)
                    search.searchArtists()

                # restart loop at login if logout is true
                if logout:
                    break

