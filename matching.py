from databaseconn import all_rows
from mp3_to_wav import wavFilesPaths
from test import allHashes


    
def time_difference():
    for i in range(len(wavFilesPaths)):
        id=i
        timeDiffDict={}
        timeDiffDict[id]=[]
        for j in range(len(all_rows)):
            hash = all_rows[j]['hash']
            
            if hash in allHashes and all_rows[j]['song_id']==id:
                
                testTime = allHashes[hash]
                databaseTime = all_rows[j]['time_offset_ms']
                timeDifference = int(abs(databaseTime - testTime))
                timeDiffDict[id].append(timeDifference)
    
    return timeDiffDict

finalDict={}
def sliding(timeDiffDict, gap):
    right=0
    left=0
    for i in range(len(timeDiffDict)):
        
        timeDiffList = timeDiffDict[i]
        timeDiffList.sort()
        right=left+1
        
        while right<len(timeDiffList) and left<len(timeDiffList):
            obsgap=timeDiffList[right]-timeDiffList[left]
            if obsgap<=200:
                finalDict[timeDiffList[left]]=i
                finalDict[timeDiffList[right]]=i

                right+=1
                obsgap=timeDiffList[right]-timeDiffList[left]
            elif obsgap>200:
                left=right
                right=left+1
                obsgap=timeDiffList[right]-timeDiffList[left]  
        left=0
        right=0 
       
    return finalDict

def get_max_count(timeDiffDict, finalDict):
    grouping={}
    maxCount=0
    for i in range(len(timeDiffDict)):
        timeDiffList = timeDiffDict[i]
        grouping[i]=[]
        for x in timeDiffList:
            if x in finalDict:
                grouping[i].append(x)
    for i in range(len(grouping)):
        count=len(grouping[i])
        if count>maxCount:
            maxCount=count
    return maxCount, grouping



        

def  result(maxCount, grouping):
    for i in range(len(grouping)):
        if maxCount==len(grouping[i]):
            return i

matchedSong=result(*get_max_count(time_difference(), sliding(time_difference(), gap=200)))
       