
import twitter, requests, json, random
from .bingSpeech.textToSpeech import playSelfieAudioResponse

def getTwitterCreds():
    credentials = json.load(open('../credentials.json'))
    twitterCreds = credentials['twitter']
    return(twitterCreds)

def getTwitterAPI():
    twitterCreds = getTwitterCreds()
    twitterAPI = twitter.Api(consumer_key=twitterCreds['consumerKey'],
                         consumer_secret=twitterCreds['consumerSecret'],
                         access_token_key=twitterCreds['accessToken'],
                         access_token_secret=twitterCreds['accessTokenSecret'])
    return(twitterAPI)

def getStatus():
    statusList = ['Its a great time to be alive #IoTShow2017 #CloudThat #MoveUp',
                  '#CloudThat is at the #IoTShow2017,come meet us! #MoveUp',
                  'Come check out #Cloudthat at the #IoTShow2017',
                  'Want to know more about IoT? #CloudThat is the booth to be at! #IoTShow2017'
                 ]
    return(random.choice(statusList))

def postStatus():
    api = getTwitterAPI()
    with open('selfie.jpg', 'rb') as mediaImage:
        res = api.PostUpdate(status=getStatus(), media=mediaImage)
        return(res)

def captureSelfie():
    print("Selfie captured!")
    #Add camera code here
    playSelfieAudioResponse()

def tweet():
    captureSelfie()
    postStatus()
    return(True)
