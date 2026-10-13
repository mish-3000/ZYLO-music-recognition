import os
from collections import Counter
from databaseconn import results, cursor
from test import allHashes


timeDiffDict={}
def time_difference():


    for row in results:
        testTime = allHashes[row['hash']]

        databaseTime = row['time_offset_ms']
        timeDifference = round(databaseTime - testTime)
        timeDiffDict.setdefault(row['song_id'], []).append(timeDifference)




    return timeDiffDict
time_differenceCache=time_difference()


def get_max_count(timeDiffDict):
    maxCount=0
    bestSong=None
    for i in timeDiffDict:
        offsetCounts = Counter(timeDiffDict[i])
        count = max(offsetCounts.values())
        if count>maxCount:
            maxCount=count
            bestSong=i
    return maxCount, bestSong

get_max_countCache=get_max_count(time_differenceCache)



def  result(maxCount, bestSong):
    if maxCount>0:
        return bestSong
    return "No match found"

matchedSong=result(*get_max_countCache)
if matchedSong == "No match found":
    print("song:",matchedSong)
else:
    cursor.execute("SELECT filename FROM songs WHERE id=%s", (matchedSong,))
    songName = os.path.splitext(os.path.basename(cursor.fetchone()['filename']))[0]
    print("song:",songName)
