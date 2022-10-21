
import sqlite3
from sqlite3 import Error







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


#
if __name__ == '__main__':
    databaseFile = "/Users/lucasrasmusson/Documents/CMPUT291/miniProject1/miniProject1.db"
    createDatabaseConnection(databaseFile)

    data = login(databaseFile)

    print("we made it here")

    print(data)

    print("name: ", data[0][1])

    if data[1] == "user":
        loginType = "user"
    else:
        loginType = "artist"

    logout = False
    while 1:
        randomInput = input("Whatever input:")
        if randomInput == "logout":
            logout = True
        if randomInput == "exit":
            # end session here as well
            break
        print("logout: ", logout)
        if logout:
            print("Thank you for using UAtify!")
            login(databaseFile)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
