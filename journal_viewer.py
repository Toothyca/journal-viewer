import os
import re
from PIL import Image
import PIL.ExifTags
from PIL.ExifTags import TAGS
import sqlite3

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
    print(XPKeywords)
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
                #print("playPattern match:", albums[index + 1][1:-1])
                musicDict[albumName] = albums[index + 1].split('[', 1)[1].split(']')[0]
                index +=1
            # if extensionPattern matches, look ahead two for the album and then the number of plays for both
            # only need to look two ahead because only two albums can have the same number of plays
            elif extensionPattern.match(albums[index + 1]):
                #print("extensionPattern match")
                #if index + 2 < len(albums) - 1:
                albumName2 = albums[index + 2]
                    #if index + 3 < len(albums) - 1:
                    #    if playPattern.match(albums[index + 3]):
                musicDict[albumName] = albums[index + 3].split('[', 1)[1].split(']')[0]
                musicDict[albumName2] = albums[index + 3].split('[', 1)[1].split(']')[0]
                index += 3

            else:
                musicDict[albumName] = 1
        else:
                musicDict[albumName] = 1
        
        index += 1

    for keys,values in musicDict.items():
        print(keys, values)
    print("")
    return musicDict

path = "aryday"
years = [os.path.join(path, file) for file in os.listdir(path) if isYear(file)]
# loop through all year folders in "aryday" 
for yearFolder in years:
    #days = [file.strip(".jpg") for file in os.listdir(yearFolder) if file.endswith(".jpg")]
    #print(days)
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
                #print(exif.keys())
                if("XPComment" in exif):
                    content.append(exif["XPComment"].decode('utf-16'))
                else:
                    content.append("")
                
                if("XPKeywords" in exif):
                    albums.append(xpkeywordsToDict(exif["XPKeywords"].decode('utf-16')))
                else:
                    albums.append({})
                #print(exif["XPComment"].decode('utf-16'))
                #print(exif["XPKeywords"].decode('utf-16'))
                #print("\n\n")
            except Exception as e:
                print(e)
        #break
    #print(days)
        