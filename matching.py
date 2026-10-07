from databaseconn import results
from mp3_to_wav import wavFilesPaths
from test import allHashes


timeDiffDict={}    
def time_difference():
    song_ids = set(row['song_id'] for row in results) 
    for id in song_ids:
        
        
        timeDiffDict[id]=[]
        for j in range(len(results)):
            hash = results[j]['hash']
            
            if hash in allHashes and results[j]['song_id']==id:
                
                testTime = allHashes[hash]
                databaseTime = results[j]['time_offset_ms']
                timeDifference = (databaseTime - testTime)
                timeDiffDict[id].append(timeDifference)
    
    return timeDiffDict
time_differenceCache=time_difference()

finalDict={}
def sliding(timeDiffDict, gap):
    right=0
    left=0
    for i in timeDiffDict:
        
        timeDiffList = timeDiffDict[i]
        timeDiffList.sort()
        right=left+1
        finalDict[i]=[]
        while right<len(timeDiffList) and left<len(timeDiffList):
            obsgap=timeDiffList[right]-timeDiffList[left]
            if obsgap<=200:
                if timeDiffList[left] not in finalDict[i]:   
                    finalDict[i].append(timeDiffList[left])
                if timeDiffList[right] not in finalDict[i]:  
                    finalDict[i].append(timeDiffList[right])
              

                right+=1
               
            elif obsgap>200:
                left=left+1  
                if left == right:
                    right = left + 1    


        left=0
        right=0 
       
    return finalDict
slidingCache=sliding(time_differenceCache,gap=200)


def get_max_count(timeDiffDict, finalDict):
    grouping={}
    maxCount=0
    for i in timeDiffDict:
        timeDiffList = timeDiffDict[i]
        grouping[i]=[]
        for x in timeDiffList:
            if x in finalDict[i]:
                grouping[i].append(x)
    for i in grouping:
        count=len(grouping[i])
        if count>maxCount:
            maxCount=count
    return maxCount, grouping

get_max_countCache=get_max_count(time_differenceCache, slidingCache)

        

def  result(maxCount, grouping):
    for i in grouping:
        if maxCount==len(grouping[i]) and maxCount>0:
            return i
    return "No match found"

matchedSong=result(*get_max_countCache)
print("song:",matchedSong)     