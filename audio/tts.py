import multiprocessing as mp
import queue


def _tts_worker(q: mp.Queue, rate: int):
    """
    Dedicated TTS process using Windows SAPI.
    Completely isolated from OpenCV / main loop.
    """

    import pythoncom
    pythoncom.CoInitialize()

    import win32com.client

    try:
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        speaker.Rate = 0  # Stable default (-10 to +10)
    except Exception as e:
        print("Failed to initialize SAPI:", e)
        return

    while True:
        text = q.get()

        if text is None:
            break

        try:
            speaker.Speak(text)
        except Exception:
            # Attempt recovery if SAPI crashes
            try:
                speaker = win32com.client.Dispatch("SAPI.SpVoice")
                speaker.Rate = 0
                speaker.Speak(text)
            except Exception:
                pass


class TTS:
    """
    Robust offline Windows TTS using multiprocessing.
    Safe for real-time OpenCV loops.
    """

    def __init__(self, rate: int = 175):
        self._q: mp.Queue = mp.Queue()
        self._p = mp.Process(
            target=_tts_worker,
            args=(self._q, rate)
        )
        self._p.start()

    def speak(self, text: str):
        if not text:
            return

        # Drop old queued messages (keep it real-time)
        dropped = 0
        while True:
            try:
                self._q.get_nowait()
                dropped += 1
                if dropped >= 2:
                    break
            except queue.Empty:
                break

        self._q.put(text)

    def close(self):
        try:
            self._q.put(None)
            self._p.join(timeout=2)
        except Exception:
            pass