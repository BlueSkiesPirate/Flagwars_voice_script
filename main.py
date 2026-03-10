                
import sounddevice as sd
import queue
import json
import time
from vosk import Model, KaldiRecognizer
from pynput.keyboard import Controller

keyboard = Controller()
audio_queue = queue.Queue()

print("Program started")

#We create a direct map between the words and their number values
word_to_key = {
    "sword": "1",
    "three": "3",
    "four": "4",
    "five": "5",
}
#We make a list of the keys ["sword", "three", "four", "five"]
word_library = list(word_to_key.keys())

model = Model("vosk-model-small-en-us-0.15")
print("Model loaded")

grammar = json.dumps(word_library)
rec = KaldiRecognizer(model, 16000, grammar)
print("Recognizer created")

#Some controls to prevent repetition
last_command = None


#Actually press a key
def press_key(key_to_press: str):
    keyboard.press(key_to_press)
    keyboard.release(key_to_press)


def callback(indata, frames, time_info, status):
    if status:
        print("Audio status:", status)
    audio_queue.put(bytes(indata))


#Begin listening for speech
with sd.RawInputStream(
    samplerate=16000,
    blocksize=4000,          # let PortAudio choose optimal callback size
    dtype="int16",
    channels=1,
    latency="low",        # request low-latency input
    callback=callback
):
    print("Listening...")

    while True:
        data = audio_queue.get()

        # Feed audio to recognizer (This is for handling full words, not neccessary, and I expect these to be slower)
        is_final = rec.AcceptWaveform(data)

        # Check partial result first for fast reactions
        partial = json.loads(rec.PartialResult()).get("partial", "").strip()

        if partial in word_to_key and partial != last_command: #This prevents unintentional switches to the same box
                key_to_press = word_to_key[partial]
                print(f"Partial heard: {partial} -> pressing {key_to_press}")
                # press_key(key_to_press)
                keyboard.press(key_to_press)
                keyboard.release(key_to_press)
                last_command = partial
                continue

     # Optional: also handle final results as a fallback
        if is_final:
            text = json.loads(rec.Result()).get("text", "").strip()
            # if text in word_to_key:
                
            #     if text :
            #         key_to_press = word_to_key[text]
            #         print(f"Final heard: {text} -> pressing {key_to_press}")
            #         press_key(key_to_press)
            #         last_command = text
             
                