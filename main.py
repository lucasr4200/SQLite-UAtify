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
    clearScreen()
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
            clearScreen()
            for row in result:
                print("Welcome:", row[1])
            cur.close()
            connection.close()
        else:
            print("Login failed")
            cur.close()
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
            clearScreen()
            for row in result:
                print("Welcome:", row[1])
            cur.close()
            connection.close()
        else:
            cur.close()
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
        cur.close()
        connection.close()

        return login(databaseFile)
    elif userOrArtist == "exit":
        exit()
    else:
        print("Neither answer selected")
        return login(databaseFile)


def startSession(id):
    connection = sqlite3.connect(databaseFile)
    sno = random.randint(0, 100000)

    # Start a session by inserting values into  sessions table, initialize the end date as a NULL value
    connection.execute("INSERT into sessions(uid, sno, start, end) VALUES (:id,:s, date('now'), Null)", {"id":id, "s":sno})
    connection.commit()
    connection.close()

    return sno


def endSession(id, sno):
    connection = sqlite3.connect(databaseFile)
    cur = connection.cursor()

    cur.execute("SELECT s.sno, s.start, s.uid FROM sessions s, users u" \
                " WHERE s.uid = u.uid;")
    # y is a temporary variable to store the results of the query
    y = cur.fetchall()

    # update the sessions table to include coresponding end date
    updateSessions(connection, (id, sno, y[0][1]))

    cur.close()
    connection.close()


def updateSessions(connection, data):
    # function to update the sessions table

    connection.execute(" UPDATE sessions "\
                       "set uid = :id,"\
                       "sno = :sn,"\
                       "start = :st,"\
                       "end = date('now')"\
                       "WHERE sno = :s"
                       , {"id":data[0], "sn":data[1], "st":data[2], "s":data[1]})

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
        loginData = login(databaseFile)

        # Establish login type \ data[1] is login type
        if loginData[1] == "artist":
            artist.artistInterface(databaseFile, loginData[0][0])
        else:
            while 1:          
                # Start session here
                sno = startSession(loginData[0][0])
                userMenu = "Welcome to UAtify\n"\
                        "To search for an artist, enter /search artists\n"\
                        "To search for a song, enter /search songs\n"\
                        "To logout, enter /logout\n"
                randomInput = input(userMenu)

                if randomInput.lower() == "/logout":
                    endSession(loginData[0][0], sno)
                    # end session here
                    break

                # search for songs using function from search.py
                if randomInput.lower() == "/search songs":
                    search.setupSearch(sqlite3.connect(databaseFile), sqlite3.connect(databaseFile).cursor(), loginData[0][0], sno)
                    search.searchSongs()
                # search for artists using function from search.py
                if randomInput.lower() == "/search artists":
                    search.setupSearch(sqlite3.connect(databaseFile), sqlite3.connect(databaseFile).cursor(), loginData[0][0],sno)
                    search.searchArtists()

            

