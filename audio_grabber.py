import re

import pyaudio
import wave
import requests

strip_non_alphanumeric = lambda s: re.sub(r'[^a-zA-Z0-9]', '', s)

def record_audio(file_name, record_seconds):
    # Audio configuration
    format = pyaudio.paInt16
    channels = 1
    rate = 16000
    chunk = 1024

    audio = pyaudio.PyAudio()

    # Start recording
    stream = audio.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)
    print("Recording...")

    frames = []
    for _ in range(0, int(rate / chunk * record_seconds)):
        data = stream.read(chunk)
        frames.append(data)

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save to file
    with wave.open(file_name, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(audio.get_sample_size(format))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
    print(f"Recording saved to {file_name}")


def play_audio(file_name):
    # Open the file
    wf = wave.open(file_name, 'rb')

    audio = pyaudio.PyAudio()

    # Open stream
    stream = audio.open(format=audio.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

    # Read data
    data = wf.readframes(1024)

    # Play stream
    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(1024)

    # Stop stream
    stream.stop_stream()
    stream.close()

    # Close PyAudio
    audio.terminate()
    print(f"Playback finished for {file_name}")

def analyze_audio(file_path):
    url = "http://127.0.0.1:8080/inference"

    multipart_form_data = {
        'file': (file_path, open(file_path, 'rb')),
        'temperature': ('', '0.2'),
        'response-format': ('', 'json')
    }

    # Send the request
    response = requests.post(url, files=multipart_form_data)

    # Close the file
    multipart_form_data['file'][1].close()

    # Return the response
    return re.sub(r'[^a-zA-Z0-9 ]', '', response.json()["text"].strip())


# record_audio("test.wav", 2)
# play_audio("test.wav")
# response = analyze_audio("/Users/dyusha/fun_things/doemod/test.wav")
# print(response)
