import speech_recognition as sr

def listen_for_command(timeout=5, phrase_time_limit=4, device_index=None):
    r = sr.Recognizer()

    try:
        with sr.Microphone(device_index=device_index) as source:
            print("Listening...")
            r.adjust_for_ambient_noise(source, duration=0.5)
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
    except sr.WaitTimeoutError:
        print("Listening timed out.")
        return None
    except Exception as e:
        print("Microphone error:", e)
        return None

    try:
        text = r.recognize_google(audio)
        print("Heard:", text)
        return text.lower()
    except sr.UnknownValueError:
        print("Could not understand audio.")
    except sr.RequestError as e:
        print("Speech service error:", e)

    return None
