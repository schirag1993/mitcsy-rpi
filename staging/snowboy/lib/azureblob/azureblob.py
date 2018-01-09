import requests, json, random
from .bingSpeech.textToSpeech import playSelfieAudioResponse, tweetAck
from azure.storage.blob import BlockBlobService
import random
import pygame, sys
import pygame.camera
from random_words import RandomWords
from pprint import pprint
from pygame.locals import *
from azure.storage.blob import ContentSettings

def captureSelfie():
    width = 1280
    height = 720
    dimensions = (width, height)
    pygame.init()
    print("Initializing PyGame")
    pygame.camera.init()
    flag = True
    count = 0
    while(flag):
        try:
            cam = pygame.camera.Camera("/dev/video0",dimensions)
            cam.start()
            print("Camera started")
            imageName = 'selfie.jpg'
            image = cam.get_image()
            print("Image saved")
            pygame.image.save(image,imageName)
            cam.stop()
            pygame.quit()
            flag = False
            return
        except:
            print("Camera busy. Stand by.")
            time.sleep(1)
            count = count + 1
            if(count>9):
                print("You might need to reconnect the camera. My apologies.")
                pygame.quit()
                flag = False
                return
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
    
def sendToAzure():
    captureSelfie()
    storeImage()