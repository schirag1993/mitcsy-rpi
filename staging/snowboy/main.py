from lib.luisHelper.luisHelper import getIntentAndEntities
from lib.med.medHelper import medicalQuery
from lib.ocr.ocr import getRecognizedText
from lib.face.face import faceHandler
from lib.bingSpeech.textToSpeech import tts
from lib.bingSpeech.speechToText import stt
from lib.azureblob.azureblob import sendToAzure
from lib.ibm.discovery import askDiscovery
from lib.mail.mail import mailGun
from pprint import pprint
import re

def handleAudio():
    print("Inside handleAudio()")
    medPattern = re.compile(pattern='med.*')
    errorResponse = "I'm sorry. Something went wrong."
    noneHandler = "My apologies. I do not have that kind of functionality yet."
    print("Getting STT data")
    result = stt()
    print("Got STT data")
    if(type(result) != tuple):
        tts(errorResponse)
    elif(result[0]):
        textCommand = result[1]
        luisResponse = getIntentAndEntities(textCommand)
        print("LUIS Intent: {0}".format(luisResponse['intent']))
        print("LUIS Entities: ")
        pprint(luisResponse['entities'])
        print("Performing RegEx")
        if(re.search(medPattern, luisResponse['intent'])):
            print("Checking med patterns")
            if(luisResponse['intent'] == 'medical.findDisease'):
                tts(medicalQuery(luisResponse))
            elif(luisResponse['intent'] == 'medical.getDescription'):
                tts(medicalQuery(luisResponse))
            elif(luisResponse['intent'] == 'medical.getSymptoms'):
                tts(medicalQuery(luisResponse))
            elif(luisResponse['intent'] == 'medical.identifyPatient'):
                tts(faceHandler(luisResponse))
            elif(luisResponse['intent'] == 'medical.registerPatient'):
                faceHandler(luisResponse)
            elif(luisResponse['intent'] == 'medical.discovery'):
                print("Inside medical.discovery handler")
                tts(askDiscovery())
        elif(luisResponse['intent'] == 'None'):
            print("None recognized")
            tts(noneHandler)
        elif(luisResponse['intent'] == 'Communication.SendEmail'):
            print("Inside mail intent")
            mailGun()
        elif(luisResponse['intent'] == 'Camera.CapturePhoto'):
            sendToAzure()
    else:
        tts(result[1])
    print("Returning to KWS mode")
    return