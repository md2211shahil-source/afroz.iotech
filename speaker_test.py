import subprocess
import time

for i in range(3):

    print(f"🔊 Speaking {i + 1}/3")

    command = (
        "Add-Type -AssemblyName System.Speech; "
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        "$s.Rate = -3; "
        "$s.Speak('ready for gromming'); "
        "$s.Dispose()"
    )

    subprocess.run([
        "powershell",
        "-NoProfile",
        "-Command",
        command
    ])

    time.sleep(3)

print("✅ Voice test completed!")