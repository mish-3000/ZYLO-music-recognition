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
        finalDict[i]=[]
        timeDiffList = timeDiffDict[i]
        timeDiffList.sort()
        right=left+1
        obsgap=timeDiffList[right]-timeDiffList[left]
        while right<len(timeDiffList) and left<len(timeDiffList):
            if obsgap<=200:
                finalDict[i].append(timeDiffList[left])
                finalDict[i].append(timeDiffList[right])
                right+=1
                obsgap=timeDiffList[right]-timeDiffList[left]
            elif obsgap>200:
                left=right
                right=left+1
                obsgap=timeDiffList[right]-timeDiffList[left]  
        left=0
        right=0 
       
    return finalDict

def get_max_count(finalDict):
    maxCount=0
    for i in range(len(finalDict)):
        count=len(finalDict[i])
        if count>maxCount:
            maxCount=count
    return maxCount

def  result(maxcount, finalDict):
    for i in range(len(finalDict)):
        if maxcount==len(finalDict[i]):
            return i

result(get_max_count(sliding(time_difference(), gap=200)),sliding(time_difference(), gap=200))