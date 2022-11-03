import sqlite3
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
    loginPrompt = f"Welcome to UAtify\n"\
                    f"How would you like to login?\n"\
                    f"\t/user\n"\
                    f"\t/artist\n"\
                    f"\t/signup\n"\
                    f"\t/exit\n"
                    
    userOrArtist = input(loginPrompt)
    userOrArtist = userOrArtist.lower()

    if userOrArtist == "/user":
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
                print("Welcome", row[1])
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

    elif userOrArtist == "/artist":
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
                print("Welcome", row[1])
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

    elif userOrArtist == "/signup":
        connection = sqlite3.connect(databaseFile)
        cur = connection.cursor()
        newuid = input("Enter uid: ")
        newName = input("Enter name: ")
        newPassword = input("Enter password: ")

        connection.execute("INSERT into users(uid, name, pwd) VALUES (:nId,:nName,:nPW)", 
                            {"nId":newuid, "nName":newName, "nPW":newPassword})

        connection.commit()
        cur.close()
        connection.close()

        return login(databaseFile)
    elif userOrArtist == "/exit":
        exit()
    else:
        print("Invalid command, please try again")
        return login(databaseFile)


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
    connection.execute("INSERT into sessions(uid, sno, start, end) VALUES (:id,:s, date('now'), Null)", {"id":id, "s":maxsno})
    connection.commit()
    cursor.close()
    connection.close()

    clearScreen()
    print("Session started successfully")
    return maxsno


def endSession(id, sno):
    connection = sqlite3.connect(databaseFile)
    cur = connection.cursor()

    connection.execute(f"UPDATE sessions SET "
                       f"end = datetime('now')"
                       f"WHERE uid = ? AND sno = ?"
                       , [id, sno])
    connection.commit()
    
    cur.close()
    connection.close()
    clearScreen()
    print("Session ended")


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

        # load artist or user interface
        if loginData[1] == "artist":
            artist.artistInterface(databaseFile, loginData[0][0])
        else:
            # Loop for user interface
            sno = 0
            while 1: 
                userMenu =  f"User Actions:"\
                            f"\n\t/exit"\
                            f"\n\t/logout"

                initialMenu = f"\t/startsession"

                sessionMenu = f"\t/endsession"\
                                f"\n\t/searchsongs"\
                                f"\n\t/searchartists"

                actionPrompt = f"\nEnter an action: "
                print(userMenu)
                if sno == 0:
                    print(initialMenu)
                    randomInput = input(actionPrompt)
                else:
                    print(sessionMenu)
                    randomInput = input(actionPrompt)

                if randomInput.lower() == "/logout":
                    endSession(loginData[0][0], sno)
                    sno = 0
                    # end session here
                    break

                # start a session
                if randomInput.lower() == "/startsession":
                    if sno == 0:
                        sno = startSession(loginData[0][0])
                    else:
                        restart = ''
                        while (restart != 'y') and (restart != 'n'):
                            restart = input("You are already in a session. Would you like to end and start a new one now? Y/N: ")
                            if restart.lower() == 'y':
                                endSession(loginData[0][0], sno)
                                sno = startSession(loginData[0][0])
                            elif restart.lower() == 'n':
                                sno = 0
                
                #end a session if one is open            
                if randomInput.lower() == "/endsession":
                    if sno == 0:
                        print("You are not currently in a session")
                    else:
                        endSession(loginData[0][0], sno)
                        sno = 0
                    
                # search for songs using function from search.py
                if randomInput.lower() == "/searchsongs":
                    if sno == 0:
                        start = input("You are not currently in a session, so this command is not valid. Start session and execute this command now? y/N: ")
                        if start.lower == 'y':
                            sno = startSession(loginData[0][0])
                            search.setupSearch(sqlite3.connect(databaseFile), sqlite3.connect(databaseFile).cursor(), loginData[0][0], sno)
                            search.searchSongs()
                            search.cleanUpSearch()
                    else:    
                        search.setupSearch(sqlite3.connect(databaseFile), sqlite3.connect(databaseFile).cursor(), loginData[0][0], sno)
                        search.searchSongs()
                        search.cleanUpSearch()


                # search for artists using function from search.py
                if randomInput.lower() == "/searchartists":
                    if sno == 0:
                        start = input("You are not currently in a session, so this command is not valid. Start session and execute this command now? y/N: ")
                        if start.lower == 'y':
                            sno = startSession(loginData[0][0])
                            search.setupSearch(sqlite3.connect(databaseFile), sqlite3.connect(databaseFile).cursor(), loginData[0][0],sno)
                            search.searchArtists()
                    else:
                        search.setupSearch(sqlite3.connect(databaseFile), sqlite3.connect(databaseFile).cursor(), loginData[0][0],sno)
                        search.searchArtists()
                
                if randomInput.lower() == "/exit":
                    exit()

            

