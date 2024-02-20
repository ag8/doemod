import pyaudio
import webrtcvad
import whisper
import numpy as np

class SpeechRecognizer:
    def __init__(self, model="base.en"):
        print("Loading whisper model...")
        self.model = whisper.load_model(model)
        self.vad = webrtcvad.Vad()
        self.audio = pyaudio.PyAudio()

    def record_and_transcribe(self, prompt=None):
        RATE = 16000
        CHUNK = int(RATE / 1000 * 30)

        # Start recording
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )

        # start recording
        frames = []
        no_speech_count = -10 # start at -300ms

        while len(frames) < 400 and no_speech_count < 33: # stop after no speech for 1s or after 12s of audio
            # read the audio data
            buffer = stream.read(CHUNK) # 30ms
            # add the data to the frames list
            frames.append(np.frombuffer(buffer, dtype=np.int16))
            # check if the user has stopped speaking
            is_speech = self.vad.is_speech(buffer, RATE)
            if not is_speech:
                no_speech_count += 1
            else:
                no_speech_count = 0
        # stop recording
        stream.stop_stream()
        stream.close()

        if len(frames) == 50: # no audio picked up for first 1.5s; stall
            return ""
        
        signal = np.hstack(frames).astype(np.float32) / 32768.0
        return self.model.transcribe(signal, initial_prompt=prompt, fp16=False)["text"]
    
    def __del__(self):
        self.audio.terminate()
