import time
import pyttsx3

engine = pyttsx3.init(driverName="sapi5")
engine.setProperty("rate", 175)

for i in range(5):
    text = f"Test number {i}"
    print("Saying:", text)
    engine.say(text)
    engine.runAndWait()
    time.sleep(0.5)

print("DONE")
