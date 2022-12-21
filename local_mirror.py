import sys
import glob
import json
import math
import time
import urllib.request
from os.path import exists
from KalturaClient import *
from KalturaClient.Plugins.Core import *

# constants

PAGE_SIZE=30

# globals

conf= {}
client= None

def processCommandLine():
    global conf
    for arg in sys.argv:
        nameValuePair= arg.split('=')
        if len(nameValuePair)==2:
            conf[nameValuePair[0].upper()]= nameValuePair[1]

def kalturaStart():
    global client, conf
    config = KalturaConfiguration()
    config.serviceUrl = conf['SERVICEURL']
    client = KalturaClient(config)
    ks = client.session.start(conf['ADMINSECRET'], conf['USERID'], KalturaSessionType.USER, conf['PID'], 86400, 'disableentitlement')
    client.setKs(ks)


def processEntry(entry):
    global client
    jsonFileName= entry.id+'.json'
    # check if video exists
    if not glob.glob(entry.id+'.*'):
        # get the lowest bitrate version
        filter = KalturaAssetFilter()
        filter.entryIdIn = entry.id
        filter.orderBy = KalturaAssetOrderBy.SIZE_ASC
        filter.sizeGreaterThanOrEqual = 1
        lowestBitrate = client.flavorAsset.list(filter, KalturaFilterPager()).getObjects()[0]
        videoFileName= entry.id+'.'+lowestBitrate.fileExt
        # get the download Url
        downloadUrl = client.flavorAsset.getUrl(lowestBitrate.id, 0, False, KalturaFlavorAssetUrlOptions())
        # download the file
        print('Downloading',videoFileName)
        urllib.request.urlretrieve(downloadUrl, videoFileName)
        # generate the json file
        jsonFileName= entry.id+'.json'
        jsonObj={'id':entry.id,'name':entry.name,'description':entry.description,'userId':entry.userId,'creatorId':entry.creatorId,'tags':entry.tags,'createdAt':entry.createdAt,'updatedAt':entry.updatedAt,'localFileName':videoFileName,'localMirrorAt':int(time.time())}                
        with open(jsonFileName, "w") as outfile:
            outfile.write(json.dumps(jsonObj, indent=4))
    else:
        print('skipping',entry.id)
         
processCommandLine()
kalturaStart()

# 
# find root category for KMS
# this will list only entries that were published in MediaSpace
# 

filter = KalturaCategoryFilter()
filter.fullNameEqual = "MediaSpace>site"
kmsRootId = client.category.list(filter, KalturaFilterPager()).getObjects()[0].id
print('MediaSpace Root Category ID =',kmsRootId)

# 
# loop over the media list
# 

filter = KalturaMediaEntryFilter()
filter.mediaTypeEqual = KalturaMediaType.VIDEO
filter.statusEqual = KalturaEntryStatus.READY
filter.typeEqual = KalturaEntryType.MEDIA_CLIP
filter.categoryAncestorIdIn = kmsRootId
filter.createdAtGreaterThanOrEqual = 1670907600

mainCount = client.media.list(filter, KalturaFilterPager())
mainPager= KalturaFilterPager()
mainPager.pageSize = PAGE_SIZE
count=0
for mainPager.pageIndex in range(1, math.ceil(mainCount.totalCount/mainPager.pageSize)+1):
    mediaList = client.media.list(filter, mainPager)
    for entry in mediaList.getObjects():
        processEntry(entry)
        count+= 1
        if count > 2:
            break
    break
