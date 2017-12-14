import snowboydecoder, sys, signal
from pathlib import Path
from audioRecorder import record_to_file

from main import handleAudio

interrupted = False
modelPath = Path('./resources/hey_mitsy.pmdl')
model = str(modelPath)

def recordAudio():
    print("Recording audio now...")
    record_to_file('query.wav')
    print("Recording complete!")
    handleAudio()
    print("Command handling done!")

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
