from stt.sarvam import SarvamSTT


stt = SarvamSTT()

text = stt.transcribe("test_audio.wav")

print("\nBRAHMA heard:")
print(text)