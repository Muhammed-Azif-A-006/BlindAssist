import multiprocessing as mp
import queue

def _tts_worker(q: mp.Queue, rate: int):
    # Windows-only: use SAPI directly (stable)
    import win32com.client

    speaker = win32com.client.Dispatch("SAPI.SpVoice")
    # Rate: -10 to +10 typically
    # Map your 175-ish to something reasonable:
    speaker.Rate = 0  # try 0 first

    while True:
        text = q.get()
        if text is None:
            break
        try:
            speaker.Speak(text)
        except Exception:
            # Try recreating speaker
            try:
                speaker = win32com.client.Dispatch("SAPI.SpVoice")
                speaker.Rate = 0
            except Exception:
                pass

class TTS:
    """
    Robust offline TTS using Windows SAPI via pywin32 (recommended on Windows).
    """
    def __init__(self, rate: int = 175):
        self._q: mp.Queue = mp.Queue()
        self._p = mp.Process(target=_tts_worker, args=(self._q, rate), daemon=True)
        self._p.start()

    def speak(self, text: str):
        if not text:
            return

        # Drop backlog so we don't speak outdated guidance
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
        except Exception:
            pass
