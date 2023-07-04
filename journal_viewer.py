import os
import re
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

years = [file for file in os.listdir('aryday') if isYear(file)]
for yearFolder in years:
    pass