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


def login(databaseFile):
    # Decide whether to activate user or artist login
    userOrArtist = input("Would you like to log in as a user, artist or signup? u/a/s: ")

    if userOrArtist == "u":
        uidEntered = input("Input uid: ")
        passwordEntered = getpass.getpass("Input password: ")

        connection = sqlite3.connect(databaseFile)
        cur = connection.cursor()
        cur.execute("SELECT u.uid, u.name FROM users u" \
                    " WHERE u.uid = :uid AND u.pwd = :pw;", {"uid": uidEntered, "pw":passwordEntered})
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
        cur.execute("SELECT a.aid, a.name FROM artists a" \
                    " WHERE a.aid = :aid AND a.pwd = :pw;", {"aid":aidEntered, "pw":passwordEntered})

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

        connection.execute("INSERT into users(uid, name, pwd) VALUES (nId,nName,nPW)", 
                            {"nId":newuid, "nName":newName, "nPW":newPassword})

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
    cursor = connection.cursor()

    # Get the user's greatest sno, and add 1 to it to ensure uniqueness
    cursor.execute("SELECT MAX(sno) FROM sessions WHERE uid=?", [id])

    maxsno = cursor.fetchone()[0]
    if(maxsno == None):
        maxsno = 1
    else:
        maxsno += 1

    # Start a session by inserting values into  sessions table, initialize the end date as a NULL value
    connection.execute(f"INSERT into sessions(uid, sno, start, end) VALUES (?,?, datetime('now'), Null)", (id, maxsno))
    connection.commit()
    connection.close()

    return maxsno


def endSession(id, sno):
    connection = sqlite3.connect(databaseFile)
    cur = connection.cursor()

    connection.execute(f"UPDATE sessions SET "
                       f"end = datetime('now')"
                       f"WHERE uid = ? AND sno = ?"
                       , [id, sno])
    connection.commit()
    connection.close()


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("Please provide exactly one database file!")
        exit()

    databaseFile = sys.argv[1]

    # Main loop for running program
    while 1:

        # data stores id, loginType
        data = login(databaseFile)

        clearScreen()

        # Establish login type
        if data[1] == "user":
            loginType = "user"
        else:
            loginType = "artist"

        # declare sno for later
        sno = None
        randomInput = None


        while 1:
            if loginType == "artist":
                artist.artistInterface(databaseFile, data[0][0])
                randomInput = "exit"
                break

            print(f"User Actions:"
                f"\n\texit"
                f"\n\tlogout"
                f"\n\tstart session"
                f"\n\tend session"
                f"\n\tsearch songs"
                f"\n\tsearch artists"
                )

            randomInput = input("./UAtify$ ")

            if randomInput == "logout":
                
                # end session if one was started
                if(sno != None):
                    endSession(data[0][0], sno)
                clearScreen()
                break

            if randomInput == "exit":
                # end session if one was started
                if(sno != None):
                    endSession(data[0][0], sno)
                clearScreen()
                break

            if randomInput == "start session":
                sno = startSession(data[0][0])
                clearScreen()
                print("Session started!")

            if randomInput == "end session":
                if(sno == None):
                    clearScreen()
                    continue

                endSession(data[0][0], sno)
                sno = None
                clearScreen()
                print("Session Ended")


            if randomInput == "search songs":
                clearScreen()
                if sno == None:
                    print("Start a session first!")
                else:
                    search.setupSearch(sqlite3.connect(databaseFile), sqlite3.connect(databaseFile).cursor(), data[0][0], sno)
                    search.searchSongs()

            if randomInput == "search artists":
                clearScreen()
                if sno == None:
                    print("Start a session first!")
                else:
                    search.setupSearch(sqlite3.connect(databaseFile), sqlite3.connect(databaseFile).cursor(), data[0][0],sno)
                    search.searchArtists()

        # is exit is entered break out of the outer loop
        if randomInput == "exit":
            break
