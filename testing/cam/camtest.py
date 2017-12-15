import os
import pygame, sys
import pygame.camera
import time
import os
import sys

from pprint import pprint
from pygame.locals import *

# def takeSelfie():
#     pygame.init()
#     pygame.camera.init()
#     try:
#         cam = pygame.camera.Camera("/dev/video0",(width,height))
#         cam.start()
#         image = cam.get_image()
#         cam.stop()
#         pygame.image.save(image,'selfie.jpg')
#         pygame.quit()
#     except:
#         print('Something went wrong with the camera unit. Please reboot Pi')
#     return

def takeTrainingImages():
    width = 1280
    height = 720
    dimensions = (width, height)
    pygame.init()
    count = 0
    flag = False
    imageName = "training{0}.jpg"
    print("Initializing PyGame")
    pygame.camera.init()
    for i in range(0,11):
        imageName = imageName.format(count)
        while(!flag):
            try:
                cam = pygame.camera.Camera("/dev/video0",dimensions)
                cam.start()

def captureSelfie():
    width = 1280
    height = 720
    pygame.init()
    print("Initialized pygame. Listing cameras")
    pygame.camera.init()
    pprint(pygame.camera.list_cameras())
    print("Checking camera status")
    if(len(pygame.camera.list_cameras()) == 0):
        print("Camera locked. Attempting capture...")
        for i in range(0,6):
            try:
                cam = pygame.camera.Camera("/dev/video0",(width,height))
                cam.start()
                print("Camera active")
                image = cam.get_image()
                print("Photo captured!")
                pygame.image.save(image,'selfie.jpg')
                cam.stop()
                print("Unlocking resource...")
                pygame.quit()
                print("Done!")
                return
            except:
                print("Camera locked! Waiting for unlock")
                time.sleep(2)
    else:
        print("Camera active")
        cam = pygame.camera.Camera("/dev/video0",(width,height))
        cam.start()
        print("Camera started")
        image = cam.get_image()
        print("Photo captured!")
        pygame.image.save(image,'selfie.jpg')
        cam.stop()
        print("Unlocking resource...")
        pygame.quit()
        print("Done!")
        return