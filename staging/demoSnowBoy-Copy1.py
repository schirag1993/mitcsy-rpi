
# coding: utf-8

# In[13]:


import sys, signal
from pathlib import Path
from snowboylib import snowboydecoder

# In[14]:


interrupted = False
modelPath = Path('./snowboylib/resources/hey_mitsy.pmdl')
model = str(modelPath)


# In[1]:


def recordAudio():
    print("Listening...")


# In[ ]:


def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted

# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5)
print('Listening... Press Ctrl+C to exit')

# main loop
detector.start(detected_callback=recordAudio,
               interrupt_check=interrupt_callback,
               sleep_time=0.03)

detector.terminate()

