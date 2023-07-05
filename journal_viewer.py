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

path = "aryday"
years = [os.path.join(path, file) for file in os.listdir(path) if isYear(file)]
for yearFolder in years:
    #days = [file.strip(".jpg") for file in os.listdir(yearFolder) if file.endswith(".jpg")]
    #print(days)
    days = list()
    content = list()
    albums = list()
    for day_name in os.listdir(yearFolder):
        day_path = os.path.join(yearFolder, day_name)
        if day_path.endswith(".jpg"):
            days.append(day_name)
            image = Image.open(day_path)
            try:
                #print(image.info.keys())
                exif = {
                    PIL.ExifTags.TAGS[k]: v
                    for k, v in image._getexif().items()
                    if k in PIL.ExifTags.TAGS
                }
                print(day_name)
                print(exif["XPComment"].decode('utf-16'))
                print("\n\n")
            except Exception as e:
                print(e)
        break
    #print(days)
        