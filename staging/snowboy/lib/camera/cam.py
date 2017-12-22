import os
import pygame, sys
import pygame.camera
import time
import os
import sys

from pprint import pprint
from pygame.locals import *

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
    
def captureTrainingImages():
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
            for i in range(0,11):
                imageName = "training{0}.jpg"
                imageName = imageName.format(str(i))
                print(imageName)
                image = cam.get_image()
                pygame.image.save(image,imageName)
                time.sleep(2)
            cam.stop()
            pygame.quit()
            print("DONE!")
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
            
captureSelfie()