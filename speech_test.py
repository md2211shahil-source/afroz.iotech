import sounddevice as sd
import numpy as np
import speech_recognition as sr

print("\n🎤 say  8 secand...")
print("🎙️ say near microphone.")

duration = 8
sample_rate = 16000

audio = sd.rec(
    int(duration * sample_rate),
    samplerate=sample_rate,
    channels=1,
    dtype="float32",
    device=1
)

sd.wait()

print("✅ Recording complete!")

# Microphone level check
level = np.max(np.abs(audio))

print("🎚️ Microphone level:", level)

if level < 0.02:
    print("⚠️ very low voice say near microphone.")
   
    exit()

# Float32 → Int16
audio_int16 = (audio * 32767).astype(np.int16)
audio_bytes = audio_int16.tobytes()

recognizer = sr.Recognizer()

audio_data = sr.AudioData(
    audio_bytes,
    sample_rate,
    2
)

print("🔄 now convert voice to text...")

try:
    text = recognizer.recognize_google(
    audio_data,
    language="en-IN"
)

    print("\n📝 You said:")
    print(text)

except sr.UnknownValueError:
    print("\n❌ voice is not undestand ")

except sr.RequestError as e:
    print("\n❌ Speech service error:", e)