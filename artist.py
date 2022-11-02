'''
[] Searches and comparisons are case insensitive [use .lower()]
[] Protect against SQL injections [use connection.prepareStatement()]
[] Ensure database can be passed as a command line argument
[/] Make password non-visible while typing
[/] Option to exit the program from login screen
[] Show user options on login
[] Combine our work together

'''

from operator import truediv
import main

databasefile = "./miniProject1.db"
#show artist options
def getOptions():
    selection = input("Enter s to publish a new song\n"
                        +"Enter f to view your top fans\n"
                        +"Enter p to view your top playlists\n"
                        +"Enter q to quit\n")
    while 1:
        selection = selection.lower()
        if (selection == 'p' or 'f' or 's'):
            return selection
        else:
            selection = input("Invalid input, please try again: ")


#Artist should be able to add a song by providing Title and Duration
# Needed schema:
#   songs(sid, title, duration)
#   perform(aid, sid)
def publishSong(aid):
    #connect
    connection = main.sqlite3.connect(databasefile)
    cursor = connection.cursor()

    #get title & duration
    main.clearScreen()
    title = input("Please input song title: ")
    duration = input("Please enter song duration (seconds): ")


    #check if song already exists 
    cursor.execute("SELECT * FROM songs s WHERE s.title == :t AND s.duration == :d;", 
                        {'t':title, 'd':duration})
    exists = cursor.fetchall()
    cursor.close()
    response = ""

    #warn the artist and give option to add it again
    while exists and not (response == "y") and not (response == "n"):
        #warn the user, reject request
        warning = "Your song with this title and duration already exists in the system. Are you sure you want to create it again? Y/N: "
        response = input(warning)
        response = response.lower()
        if (response == "y"):
            addSongToDB(title, duration, aid)
        elif (response == "n"):
            print("Song not added")

    if exists == []:
        addSongToDB(title, duration, aid)

#add song to database
def addSongToDB(title, duration, aid):
    #connect 
    connection = main.sqlite3.connect(databasefile)
    cursor = connection.cursor()

    #get artist collab
    artists = [aid]
    collab = ""
    collabPrompt = "Would you like to add another artist to this song? y/N: "
    while collab != "n":
        collab = input(collabPrompt)
        collab = collab.lower()
        if collab == "y":
            addArtist = input("Input the collaborating artist's aid: ")
            cursor.execute("SELECT aid FROM artists WHERE aid == :aid", {"aid":addArtist})
            if (cursor.fetchall()):
                artists.append(addArtist)
                print("Artist added")
            else:
                print("Invalid aid, artist not added")
    cursor = connection.cursor()

    #get new sid
    sidQuery = "SELECT MAX(sid) FROM songs;"
    cursor.execute(sidQuery)
    max = cursor.fetchall()
    max = max[0][0]
    max = max + 1

    #add song to database
    songQuery = "INSERT INTO songs VALUES (:sid, :title, :duration);"
    performQuery = "INSERT INTO perform VALUES (:sid, :aid);"
    cursor.execute(songQuery, {'sid':max, 'title':title, 'duration':duration},)
    cursor.close()
    cursor = connection.cursor()

    #add collabs (if any) to perform
    for id in artists:
        cursor.execute(performQuery, {'sid':max, 'aid':id})

    #verify data was added to db
    verifyQuery = "SELECT * FROM songs WHERE sid == :sid"
    cursor.execute(verifyQuery, {'sid':max})
    verify = cursor.fetchall()
    if verify:
        main.clearScreen()
        print(f"{title} ({duration}) has been added successfully.")
    else:
        main.clearScreen()
        print("Something went wrong, song not added.")

    #cleanup
    print()
    connection.commit()
    cursor.close()
    connection.close()

#Artist should be able to find top Fans & Playlists
# Top 3 Fans by artist duration listened
# if there are not >3, return less
def biggestFans(aid):
    connection = main.sqlite3.connect(databasefile)
    cursor = connection.cursor()
    #adapted from solution of Q4 for Assignment 2
    cursor.execute("SELECT l.uid, u.name, sum(l.cnt*s.duration) FROM listen l, songs s, perform p, users u " +
                    "WHERE l.sid=s.sid AND s.sid=p.sid AND p.aid=:aid AND l.uid=u.uid " +
                    "GROUP BY l.uid, u.name ORDER BY SUM(l.cnt*s.duration) DESC LIMIT 3;", {'aid':aid})
    fans = cursor.fetchall()
    main.clearScreen()
    print("Your top fans are:")
    for fan in fans:
        seconds = int(fan[2])
        minutes = seconds//60
        seconds = seconds%60
        hours = minutes//60
        minutes = minutes%60
        print(f"{fan[0]} {fan[1]} who listened for {hours} hours, {minutes} minutes, {seconds} seconds")
    #cleanup
    print()
    cursor.close()
    connection.close()

# Top 3 Playlists by number of artist songs included
# if there are not >3, return less
def topPlaylists(aid):
    #connect
    connection = main.sqlite3.connect(databasefile)
    cursor = connection.cursor()
    cursor.execute("SELECT p.pid, p.title, COUNT(i.sid) FROM playlists p, plinclude i, perform a "+
                    "WHERE p.pid=i.pid AND i.sid=a.sid AND a.aid=:aid "+
                    "GROUP BY p.pid, p.title ORDER BY COUNT(i.sid) DESC LIMIT 3;", {"aid":aid})
    
    main.clearScreen()
    playlists = cursor.fetchall()
    if playlists:
        print("Your top playlists are:")
        for pl in playlists:
            print(f"{pl[0]} {pl[1]} with {pl[2]} songs")
    else:
        print("There are no playlists containing a song you perform")

    #cleanup
    print()
    cursor.close()
    connection.close()


if __name__ == '__main__':
    databaseFile = "./miniProject1.db"
    main.createDatabaseConnection(databaseFile)
    option = ""
    while option != "q":
        option = getOptions()
        if option == "s":
            publishSong("a04")
        elif option == 'f':
            biggestFans("a04")
        elif option == 'p':
            topPlaylists("a04")
        elif option == 'q':
            pass
        else:
            print("invalid input, please try again")


