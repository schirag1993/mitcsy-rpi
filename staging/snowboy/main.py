from lib.luisHelper.luisHelper import getIntentAndEntities
from lib.med.medHelper import medicalQuery
from lib.ocr.ocr import getRecognizedText
from lib.face.face import faceHandler
from lib.bingSpeech.textToSpeech import tts
from lib.bingSpeech.speechToText import stt
from lib.twitter.twitter import tweet
import re

def handleAudio():
    print("Inside handleAudio()")
    medPattern = re.compile(pattern='med.*')
    errorResponse = "I'm sorry. Something went wrong."
    noneHandler = "My apologies. I do not have that kind of functionality yet."
    print("Getting TTS data")
    result = stt()
    print("Got TTS data")
    if(type(result) != tuple):
        tts(errorResponse)
    elif(result[0]):
        textCommand = result[1]
        luisResponse = getIntentAndEntities(textCommand)
        if(re.search(medPattern, luisResponse['intent'])):
            if(luisResponse['intent'] == 'medical.findDisease'):
                medicalQuery(luisResponse)
            elif(luisResponse['intent'] == 'medical.getDescription'):
                medicalQuery(luisResponse)
            elif(luisResponse['intent'] == 'medical.getSymptoms'):
                medicalQuery(luisResponse)
            elif(luisResponse['intent'] == 'medical.identifyPatient'):
                faceHandler(luisResponse)
            elif(luisResponse['intent'] == 'medical.registerPatient'):
                faceHandler(luisResponse)
        elif(luisResponse['intent'] == 'None'):
            tts(noneHandler)
        elif(luisResponse['intent'] == 'Camera.CapturePhoto'):
            tweet()
    else:
        tts(result[1])
    return