import os
import pygame, sys
import pygame.camera

from pprint import pprint
from pygame.locals import *

width = 1280
height = 720

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

# def takeTrainingImages():
#     pygame.init()
#     print("Initialized pygame")
#     pygame.camera.init()
#     cam = pygame.camera.Camera("/dev/video0",(width,height))
#     cam.start()
#     print("Camera started")
#     for i in range(0,6):
#         pprint(i)
#         imageName = "image0{}.jpg".format(i)
#         try:
#             image = cam.get_image()
#             pygame.image.save(image,imageName)
#             time.sleep(1)
#         except Exception as e:
#             pprint(type(e))
#             cam.stop()
#             pygame.quit()
#             print('Something went wrong with the camera unit. Please reboot Pi')
#             return
#     cam.stop()
#     return

