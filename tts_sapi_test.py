import time
from audio.tts import TTS

def main():
    tts = TTS()
    for i in range(5):
        tts.speak(f"Hello {i}")
        time.sleep(1)
    tts.close()

if __name__ == "__main__":
    main()
