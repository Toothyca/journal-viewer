import os
import re
from PIL import Image
import PIL.ExifTags
from PIL.ExifTags import TAGS
import sqlite3
from datetime import datetime

def isYear(fileName):
    '''
    Takes a file name and checks if it is a year
    Only takes into account folders
    '''
    print(fileName)
    yearPattern = re.compile("[1-3][0-9]{3}")
    if len(fileName) == 4 and yearPattern.match(fileName):
        return True
    return False

def xpkeywordsToDict(XPKeywords):
    '''
    Takes in XPKeywords (tags) with album listening
    information and converts them to a dictionary
    '''
    #print(XPKeywords)
    musicDict = {}
    # split album list into a string. XPKeywords comes in the form: album1; album2; album3
    albums = XPKeywords.split(";")
   
    # pattern for matching the number of plays an album has. ex. [3] for played three times
    # also used to get the contents between two brackets
    playPattern = re.compile("\[[0-9]+\]")
   
    # pattern for matching when two albums have the same numbre of plays since identical tags aren't allowed
    # ex. album1; [*]; album2; [3] means that both album1 and album2 were played the same amount
    extensionPattern = re.compile("\[\*\]")

    index = 0
    while index < len(albums):
        albumName = albums[index]
        # check one index ahead to see if the album has number of plays or extension
        if (index + 1) < (len(albums)):
            # if playPattern matches, add album to the dictionary with the number of plays
            if playPattern.match(albums[index + 1]):
                # the split crap is for getting the numbers between the brackets
                musicDict[albumName] = albums[index + 1].split('[', 1)[1].split(']')[0]
                index +=1
            # if extensionPattern matches, look ahead two for the album and then the number of plays for both
            # only need to look two ahead because only two albums can have the same number of plays
            elif extensionPattern.match(albums[index + 1]):
                albumName2 = albums[index + 2]
                musicDict[albumName] = albums[index + 3].split('[', 1)[1].split(']')[0]
                musicDict[albumName2] = albums[index + 3].split('[', 1)[1].split(']')[0]
                index += 3

            # ugly
            else:
                musicDict[albumName] = 1
        else:
                musicDict[albumName] = 1
        
        index += 1

    return musicDict

conn = sqlite3.connect("journals.db")

cur = conn.cursor()

# create a table for journal entries
cur.execute('''CREATE TABLE IF NOT EXISTS journal
            (date TIMESTAMP PRIMARY KEY, entry TEXT)''')

# create a table for albums
cur.execute('''CREATE TABLE IF NOT EXISTS albums
            (album_id INTEGER PRIMARY KEY AUTOINCREMENT, album_name TEXT UNIQUE)''')

# create a table for album occurences
cur.execute('''CREATE TABLE IF NOT EXISTS listens_per_day
            (date TIMESTAMP PRIMARY KEY, album_name TEXT, listens INTEGER,
            FOREIGN KEY(date) REFERENCES journal(date),
            FOREIGN KEY(album_name) REFERENCES albums(album_name))''')

path = "aryday"
years = [os.path.join(path, file) for file in os.listdir(path) if isYear(file)]
# loop through all year folders in "aryday" 
for yearFolder in years:
    days = list()
    content = list()
    albums = list()
    # search year folder (ex. 2020) for photos 
    for day_name in os.listdir(yearFolder):
        day_path = os.path.join(yearFolder, day_name)
        if day_path.endswith(".jpg"):
            
            try:
                days.append(day_name)
                image = Image.open(day_path)
                #print(image.info.keys())
                exif = {
                    PIL.ExifTags.TAGS[k]: v
                    for k, v in image._getexif().items()
                    if k in PIL.ExifTags.TAGS
                }

                #print(day_name)
                datetime_object = datetime.strptime(day_name.split(".jpg")[0], "%m.%d.%Y")

                #print(exif.keys())
                if("XPComment" in exif):
                    journal_entry = exif["XPComment"].decode('utf-16')
                    content.append(journal_entry)

                    #print(exif["XPComment"].decode('utf-16'))

                    cur.execute("INSERT OR REPLACE INTO journal (date, entry) VALUES (?, ?)", (datetime_object, exif["XPComment"].decode('utf-16'),))
                else:
                    content.append("")
                
                if("XPKeywords" in exif):
                    raw_albums = xpkeywordsToDict(exif["XPKeywords"].decode('utf-16'))
                    
                    # remove null terminater '\x00' from end of album names
                    processed_albums = {k.rstrip('\x00'):v for k, v in raw_albums.items()}
                    
                    # k = album name, v = number of plays
                    for k, v in processed_albums.items():
                        # insert album into album db
                        cur.execute("INSERT INTO albums (album_name) VALUES (?) ON CONFLICT (album_name) DO NOTHING", (k,))

                        cur.execute("INSERT OR REPLACE INTO listens_per_day (date, album_name, listens) VALUES (?, ?, ?)", (datetime_object, k, v,))

                else:
                    albums.append({})

            except Exception as e:
                print(e)

conn.commit()
conn.close()