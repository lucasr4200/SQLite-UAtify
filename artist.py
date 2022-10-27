'''
[] Searches and comparisons are case insensitive [use .lower()]
[] Protect against SQL injections [use connection.prepareStatement()]
[] Ensure database can be passed as a command line argument
[] Make password non-visible while typing
[] Option to exit the program from login screen
[] Show user options on login

'''

#Artist should be able to add a song by providing Title and Duration
# Needed schema:
#   songs(sid, title, duration)
#   perform(aid, sid)
def publishSong(aid):
    #get title & duration
    pass
    #check if song already exists
    if ('''song exists'''):
        #warn the user, reject request
        pass
    else :
        #add song to db


#Artist should be able to find top Fans & Playlists
# Top 3 Fans by artist duration listened
# if there are not >3, return less
def biggestFans(aid):
    pass

# Top 3 Playlists by number of artist songs included
# if there are not >3, return less
def topPlaylists(aid):
    pass


