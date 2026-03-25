from vosk import Model, KaldiRecognizer, SetLogLevel
import sounddevice as sd
import numpy as np
import json
import threading
import os

class STT:
    """Speech-to-text handler using Vosk with silence detection and timeout."""

    def __init__(
        self,
        model="models/vosk/vosk-model-small-en-in-0.4",
        silence_threshold=2200,
        silence_duration=1.0,
        max_duration=20.0,
        
    ):
        """Initialize model and audio/silence parameters."""
        self.model = None
        if os.path.exists(model):
            self.model_path = model
        else:
            raise FileNotFoundError("Please Download and Add a Model in models/vosk folder")
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.max_duration = max_duration
        self.recorder = None

    def _get_rms(self, indata: bytes) -> float:
        """Compute RMS amplitude from raw audio buffer."""
        audio = np.frombuffer(bytes(indata), dtype=np.int16).astype(np.float32)
        return float(np.sqrt(np.mean(audio ** 2)))

    def listen(self) -> str:
        """Capture audio, stop on silence or timeout, and return recognized text."""
        result_text = ""
        recorder = self.recorder
        stop_event = threading.Event()
        silence_clock = [None]

        def callback(indata, frames, time, status):
            nonlocal result_text
            rms = self._get_rms(indata)

            if rms > self.silence_threshold:
                if silence_clock[0] is not None:
                    silence_clock[0].cancel()
                    silence_clock[0] = None
            else:
                if silence_clock[0] is None:
                    silence_clock[0] = threading.Timer(
                        self.silence_duration, stop_event.set
                    )
                    silence_clock[0].start()

            if recorder.AcceptWaveform(bytes(indata)):
                result = json.loads(recorder.Result())
                if result.get("text"):
                    result_text = result["text"]

        hard_timer = threading.Timer(self.max_duration, stop_event.set)
        hard_timer.start()

        print("Listening...")
        with sd.RawInputStream(
            samplerate=16000,
            blocksize=8000,
            dtype='int16',
            channels=1,
            callback=callback,
        ):
            stop_event.wait()

        hard_timer.cancel()
        if silence_clock[0]:
            silence_clock[0].cancel()

        if not result_text:
            result_text = json.loads(recorder.FinalResult()).get("text", "")

        return result_text

    def start(self):
        "Starts the STT"
        SetLogLevel(-1)  # Suppress Vosk logs
        self.model = Model(self.model_path)
        self.recorder = KaldiRecognizer(self.model, 16000)
        return

    def stop(self):
        "Stops the STT"
        self.model = None
        self.recorder = None
        return

if __name__ == "__main__":
    stt = STT()
    stt.start()
    text = stt.listen()
    print(f"Recognized: {text}")
    stt.stop()