import pythoncom
import win32com.client

pythoncom.CoInitialize()

speaker = win32com.client.Dispatch("SAPI.SpVoice")
speaker.Speak("If you hear this, SAPI works.")