import sqlite3
from sqlite3 import Error
import getpass
import os
import search
import artist
import sys


connection = None
cursor = None

def clearScreen():
    # Clear the output
    if (os.name == "nt"):
        os.system('cls')
    else:
        os.system('clear')
    return


def closeAndExit():
    if(cursor != None):
        cursor.close()
    if(connection != None):
        connection.close()
    exit()


def login(databaseFile):
    global connection, cursor

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

        cursor.execute("SELECT u.uid, u.name FROM users u" \
                    " WHERE u.uid = :uid AND u.pwd = :pw;", {"uid": uidEntered, "pw":passwordEntered})
        result = cursor.fetchall()
        if result:
            clearScreen()
            for row in result:
                print("Welcome", row[1])
        else:
            print("Login failed")
            x = input("Would you like to try again? y/n: ")
            if x == "y":
                result = login(databaseFile)
            else:
                print("Goodbye!")
                closeAndExit()

        # add to list if login type is user
        result.append("user")

        return result

    elif userOrArtist == "/artist":
        aidEntered = input("Input aid: ")
        passwordEntered = getpass.getpass("Input password: ")

        cursor.execute("SELECT a.aid, a.name FROM artists a" \
                    " WHERE a.aid = :aid AND a.pwd = :pw;", {"aid":aidEntered, "pw":passwordEntered})

        result = cursor.fetchall()
        if result:
            clearScreen()
            for row in result:
                print("Welcome", row[1])
        else:
            print("Login failed")
            x = input("Would you like to try again? y/n: ")
            if x == "y":
                result = login(databaseFile)
            else:
                print("Goodbye!")
                closeAndExit()

        # add to list if login type is user
        result.append("artist")

        return result

    elif userOrArtist == "/signup":
        newuid = input("Enter uid: ")
        newName = input("Enter name: ")
        newPassword = input("Enter password: ")

        cursor.execute("INSERT into users(uid, name, pwd) VALUES (:nId,:nName,:nPW)", 
                            {"nId":newuid, "nName":newName, "nPW":newPassword})

        connection.commit()

        return login(databaseFile)
    elif userOrArtist == "/exit":
        closeAndExit()
    else:
        print("Invalid command, please try again")
        return login(databaseFile)


def startSession(id):
    global connection, cursor

    # Get the user's greatest sno, and add 1 to it to ensure uniqueness
    cursor.execute("SELECT MAX(sno) FROM sessions WHERE uid=?", [id])

    maxsno = cursor.fetchone()[0]
    if(maxsno == None):
        maxsno = 1
    else:
        maxsno += 1
    
    # Start a session by inserting values into  sessions table, initialize the end date as a NULL value
    cursor.execute("INSERT into sessions(uid, sno, start, end) VALUES (:id,:s, datetime('now'), Null)", {"id":id, "s":maxsno})
    connection.commit()

    clearScreen()
    print("Session started successfully")
    return maxsno


def endSession(id, sno):
    global connection, cursor

    cursor.execute(f"UPDATE sessions SET "
                       f"end = datetime('now')"
                       f"WHERE uid = ? AND sno = ?"
                       , [id, sno])
    connection.commit()
    
    clearScreen()
    print("Session ended")


if __name__ == '__main__':

    
    if len(sys.argv) > 1:
        databaseFile = sys.argv[1]
    else:
        databaseFile = "./miniProject1.db"

    connection = sqlite3.connect(databaseFile)
    cursor = connection.cursor()


    # Main loop for running program
    while 1:
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

                actionPrompt = f"\n./Uatify$ "
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
                                pass
                            else:
                                sno = 0
                
                #end a session if one is open            
                if randomInput.lower() == "/endsession":
                    if sno == 0:
                        print("You are not currently in a session")
                    else:
                        endSession(loginData[0][0], sno)
                        sno = 0
                    
                # search for songs or artists using function from search.py
                if (randomInput.lower() == "/searchsongs") or (randomInput.lower() == "/searchartists"):
                    if sno == 0:
                        start = input("You are not currently in a session, so this command is not valid. Start session and execute this command now? y/N: ")
                        if start.lower() == 'y':
                            sno = startSession(loginData[0][0])
                            search.setupSearch(connection, cursor, loginData[0][0], sno)
                            if randomInput.lower() == "/searchsongs":  
                                search.searchSongs()
                            else:
                                search.searchArtists()
                    else:  
                        search.setupSearch(connection, cursor, loginData[0][0], sno)
                        if randomInput.lower() == "/searchsongs":  
                            search.searchSongs()
                        else:
                            search.searchArtists()
                
                if randomInput.lower() == "/exit":
                    closeAndExit()

    closeAndExit()            

