import twitter, requests, json, random
from bingSpeech.textToSpeech import playSelfieAudioResponse, tweetAck
from azure.storage.blob import BlockBlobService
import random
from random_words import RandomWords
from pprint import pprint
from azure.storage.blob import ContentSettings

# def getTwitterCreds():
#     credentials = json.load(open('../credentials.json'))
#     twitterCreds = credentials['twitter']
#     return(twitterCreds)

# def getTwitterAPI():
#     twitterCreds = getTwitterCreds()
#     twitterAPI = twitter.Api(consumer_key=twitterCreds['consumerKey'],
#                          consumer_secret=twitterCreds['consumerSecret'],
#                          access_token_key=twitterCreds['accessToken'],
#                          access_token_secret=twitterCreds['accessTokenSecret'])
#     return(twitterAPI)

# def getStatus():
#     statusList = ['Its a great time to be alive! #IoTShow2018 #CloudThat #MoveUp',
#                   '#CloudThat is at the #IoTShow2018,come meet us! #MoveUp',
#                   'Come check out #Cloudthat at the #IoTShow2018',
#                   'Want to know more about IoT? #CloudThat is the booth to be at! #IoTShow2018'
#                  ]
#     return(random.choice(statusList))

# def postStatus():
#     api = getTwitterAPI()
#     with open('selfie.jpg', 'rb') as mediaImage:
#         res = api.PostUpdate(status=getStatus(), media=mediaImage)
#         return(res)

def captureSelfie():
    print("Selfie captured!")
    #Add camera code here
    playSelfieAudioResponse()

def getStorageCredentials():
    credentials = json.load(open('../credentials.json'))
    storageCreds = credentials["storageAccount"]
    return(storageCreds)

def connectToAzure():
    storageCreds = getStorageCredentials()
    pprint(storageCreds)
    block_blob_service = BlockBlobService(account_name=storageCreds['account_name'], account_key=storageCreds['account_key'])
    return(block_blob_service)

def randomName():
    num = random.randrange(0, 1000)
    rw = RandomWords()
    return(rw.random_word() + str(num) + ".jpg")    
    
def sendToBlob():
    block_blob_service = connectToAzure()
    block_blob_service.create_blob_from_path(
    'mitcsyimages',
    randomName(),
    'selfie.jpg',
    content_settings=ContentSettings(content_type='image/jpg')
            )
    return(True)

def storeImage():
    print("Storing image")
#     captureSelfie()
    print("Sending to blob")
    sendToBlob()
    print("Sent!")
    
storeImage()