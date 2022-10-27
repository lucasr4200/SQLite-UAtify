
import sqlite3
from sqlite3 import Error

import artist






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
        passwordEntered = input("Input password: ")

        connection = sqlite3.connect(databaseFile)
        cur = connection.cursor()
        query = f"SELECT u.uid, u.name FROM users u" \
                f" WHERE u.uid = '{uidEntered}' AND u.pwd = '{passwordEntered}';"
        cur.execute(query)
        result = cur.fetchall()
        if result:
            for row in result:
                print("Welcome:", row[1])
        else:
            print("Login failed")
            connection.close()
            x = input("Would you like to try again? y/n: ")
            if x == "y":
                login(databaseFile)
            else:
                print("Goodbye!")

        # add to list if login type is user
        print("right before appending:", result)
        print("result: ", result)
        result.append("user")

        return result

    elif userOrArtist == "a":
        aidEntered = input("Input aid: ")
        passwordEntered = input("Input password: ")

        connection = sqlite3.connect(databaseFile)
        cur = connection.cursor()
        query = f"SELECT a.aid, a.name FROM artists a" \
                f" WHERE a.aid = '{aidEntered}' AND a.pwd = '{passwordEntered}';"
        cur.execute(query)

        # x is a temporary variable
        x = cur.fetchall()
        if x:
            for row in x:
                print("Welcome:", row[1])
        else:
            print("Login failed")
        connection.close()

        # add to list if login type is artist
        x.append("artist")

        return x

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

    else:
        print("Neither answer selected")
        login(databaseFile)


def startSession(id):
    connection = sqlite3.connect(databaseFile)
    cur = connection.cursor()
    # What to do about end time in start session function?
    # How to get unique session number?
    # What to do about end date initially?
    #connection.execute(f"INSERT into sessions(uid, sno, start, end) VALUES (?,?,?,?)", (id, sno, sqlite3.Date('now')))
    #connection.commit()
    #connection.close()

    return


def endSession(id):
    connection = sqlite3.connect(databaseFile)
    cur = connection.cursor()

    query = f"SELECT s.sno, s.start FROM sessions s, users u" \
            f" WHERE s.uid = u.uid;"
    cur.execute(query)
    y = cur.fetchall()
    print("yyyyyyy: ", y)


    updateSessions(connection, (id,y[0][1], y[0][2], y[0][3]))

    #?????
    #connection.execute(f"INSERT into sessions(uid, sno, start, end) VALUES (?,?,?,?)", (uid, sno, ?, sqlite3.Date('now')))
    #connection.commit()

    connection.close()


def updateSessions(connection, data):
    # function to update a table

    query = """ UPDATE sessions
                set uid = ?,
                    sno = ?,
                    start = ?,
                    end = ?
                WHERE sno = ?
    """
    cur = connection.cursor()
    cur.execute(query, data)
    connection.commit()


if __name__ == '__main__':
    databaseFile = "./miniProject1.db"
    createDatabaseConnection(databaseFile)

    data = login(databaseFile)

    print("we made it here")

    print(data)

    print("name: ", data[0][1])

    #Start session here
    print("Time to start the session #1")
    print("data[0][0]: ", data[0][0])
    startSession(data[0][0])

    if data[1] == "user":
        loginType = "user"
    else:
        loginType = "artist"

    logout = False
    while 1:
        randomInput = input("Whatever input:")
        if randomInput == "logout":
            endSession(data[0][0])
            # end session here

            logout = True
        if randomInput == "exit":
            # end session here as well
            break
        print("logout: ", logout)
        if logout:
            print("Thank you for using UAtify!")
            data = login(databaseFile)
            if data[1] == "user":
                loginType = "user"
            else:
                loginType = "artist"

            # Start session here
            print("Time to start the session 2")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
