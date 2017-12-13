
# coding: utf-8

# In[3]:


import requests, wave, json, base64, wave, pygame
from xml.etree import ElementTree
from pprint import pprint


# In[4]:


def getBingCreds():
    credentials = json.load(open('../credentials.json'))
    bingCreds = credentials['cognitiveServices']['bingSpeech']
    return bingCreds


# In[5]:


def getBingEndpoint():
    return getBingCreds()['endPoint']

def getTTSEndpoint():
    return("https://speech.platform.bing.com/synthesize")

def getBingKey():
    return getBingCreds()['key']


# In[6]:


def getToken():
    url = getBingEndpoint() + '/issueToken'
    headers = {
        "Ocp-Apim-Subscription-Key" : getBingKey()
    }
    req = requests.post(url=url, headers=headers)
    data = req.content
    accessToken = data.decode("UTF-8")
    return(accessToken)


# In[7]:


def createBody(text):
    body = ElementTree.Element('speak', version='1.0')
    body.set('{http://www.w3.org/XML/1998/namespace}lang', 'en-us')
    voice = ElementTree.SubElement(body, 'voice')
    voice.set('{http://www.w3.org/XML/1998/namespace}lang', 'en-US')
    voice.set('{http://www.w3.org/XML/1998/namespace}gender', 'Female')
    voice.set('name', 'Microsoft Server Speech Text to Speech Voice (en-US, ZiraRUS)')
    voice.text = text
    return(ElementTree.tostring(body))


# In[8]:


def createTTSHeaders(accessToken):
    headers = {"Content-Type": "application/ssml+xml", 
			"X-Microsoft-OutputFormat": "riff-16khz-16bit-mono-pcm", 
			"Authorization": "Bearer " + accessToken, 
			"X-Search-AppId": "07D3234E49CE426DAA29772419F436CA", 
			"X-Search-ClientID": "1ECFAE91408841A480F00935DC390960", 
			"User-Agent": "testApp"}
    return(headers)


# In[9]:


def sendToBing(text):
    accessToken = getToken()
    print("access token obtained")
    print("Access token type: ")
    print(type(accessToken))
    body = createBody(text)
    headers = createTTSHeaders(accessToken)
    url = getTTSEndpoint()
    req = requests.post(url=url, data=body, headers=headers)
    if(req.status_code == 200):
        print("Successfully converted text to speech")
        return(req.content)
    else:
        print("Something went wrong when sending the data to bing. Status Code:")
        print(req.status_code)
        print(req.reason)
        return(False)


# In[10]:


# def createAudioResponse(audioData):
#     try:
#         with wave.open('./response.wav', mode='wb') as audioResponse:
#             audioResponse.setnchannels(1)
#             audioResponse.setframerate(16000)
#             audioResponse.setsampwidth(2)
#             audioResponse.writeframes(audioData)
#         return(True)
#     except:
#         print("Audio file creation failed")
#         return(False)


# In[11]:


def createAudioResponse(audioData):
    with wave.open('./response.wav', mode='wb') as audioResponse:
        audioResponse.setnchannels(1)
        audioResponse.setframerate(16000)
        audioResponse.setsampwidth(2)
        audioResponse.writeframes(audioData)
        audioResponse.close()
        return(True)        


# In[12]:


def playAudioResponse():
    pygame.mixer.init(frequency=16000, channels=1, size=-16)
    pygame.mixer.music.load('response.wav')
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue
    pygame.mixer.quit()
    pygame.quit()


# In[13]:


def tts(text):
    print(text)
    rawAudio = sendToBing(text)
    if(rawAudio == False):
        print("Something went wrong with Bing TTS")
    else:
        audioCreationResult = createAudioResponse(rawAudio)
        if(audioCreationResult == False):
            print("Something went wrong with audio file creation")
        else:
            print("Successfully created audio file")
            playAudioResponse()

