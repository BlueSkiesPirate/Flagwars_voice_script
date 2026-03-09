import sounddevice as sd
import queue
import json
from vosk import Model, KaldiRecognizer
from rapidfuzz import process

print("Program started")
print("Running file:", __file__)

word_library = ["sword", "three", "four", "five"]

model = Model("vosk-model-small-en-us-0.15")
print("Model loaded")

grammar = json.dumps(word_library)
print("Grammar created")

rec = KaldiRecognizer(model, 16000, grammar)
print("Recognizer created")

audio_queue = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print("Audio status:", status)
    audio_queue.put(bytes(indata))

print("Queue ready")

with sd.RawInputStream(
    samplerate=16000,
    blocksize=8000,
    dtype="int16",
    channels=1,
    callback=callback
):
    print("Listening...")

    while True:
        data = audio_queue.get()
        print("Received audio chunk")

        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())

            if result.get("text"):
                spoken_word = result["text"]
                match = process.extractOne(spoken_word, word_library)

                print("Heard:", spoken_word)
                print("Closest match:", match[0])
                print()