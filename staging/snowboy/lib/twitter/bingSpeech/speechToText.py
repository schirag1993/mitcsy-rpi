
# coding: utf-8

# In[3]:


import requests, json, wave
from pprint import pprint


# In[4]:


def getBingCreds():
    '''
    This function takes no arguments. It retrieves the credentials stored in the credentials file and returns it in dict format.
    The keys for the resulting dictionary are:
    1. key
    2. endPoint
    '''
    credentials = json.load(open('../credentials.json'))
    bingCreds = credentials['cognitiveServices']['bingSpeech']
    return bingCreds

def getBingKey():
    return getBingCreds()['key']


# In[5]:


def getBingEndpoint():
    '''
    Returns the endpoint specified in the Azure resource page
    '''
    return getBingCreds()['endPoint']

def getSTTEndpoint(mode, lang):
    return("https://speech.platform.bing.com/speech/recognition/" + mode + "/cognitiveservices/v1?language=" + lang + "&format=simple")


# In[6]:


def createHeaders():
    bingCreds = getBingCreds()
    key = bingCreds['key']
    headers = {
        'Content-Type' : "audio/wav; codec=audio/pcm; samplerate=16000",
        'Ocp-Apim-Subscription-Key' : key,
    }
    return(headers)


# In[27]:


def handleSTTResponse(req):
    result = req.json()
    if(result['RecognitionStatus'] == 'Success'):
        return(True, result['DisplayText'])
    elif(result['RecognitionStatus'] == 'NoMatch'):
        return(False, "Unable to match words with target langauge. Try again.")
    elif(result['RecognitionStatus'] == 'InitialSilenceTimeout'):
        return(False, "Say something, I'm giving up on you.")
    elif(result['RecognitionStatus'] == 'BabbleTimeout'):
        return(False, "Quit your babbling. Too much noise here")
    elif(result['RecognitionStatus'] == 'Error'):
        return(False, "Oops! Looks like something went wrong on the server side.")


# In[25]:


def stt():
    with open('./query.wav', 'rb') as audioFile:
        body = audioFile.read()
        url = getSTTEndpoint('dictation', 'en-US')
        headers = createHeaders()
        req = requests.post(url=url, headers=headers, data=body)
    if(req.status_code != 200):
        print("Something went wrong.")
        print("Error Code: " + str(req.status_code))
        print("Reason: " + str(req.reason))
        return(False)
    else:
        print("Response Success")
        result = handleSTTResponse(req)
        return(result)

