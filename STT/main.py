import threading
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel


class STT:
    """Speech-to-text handler with silence detection and timeout."""
    def __init__(
        self,
        model_size: str = "medium.en",
        device: str = "cpu",
        compute_type: str = "int8",
        language: str = "en",
        silence_threshold: float = 3000.0,
        silence_duration: float = 5.0,
        max_duration: float = 20.0,
        samplerate: int = 16000,
    ):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.language = language
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.max_duration = max_duration
        self.samplerate = samplerate
        self._model: WhisperModel | None = None

    def start(self) -> None:
        """Load the model into memory."""
        self._model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)

    def stop(self) -> None:
        """Release the model from memory."""
        self._model = None

    def _rms(self, chunk: np.ndarray) -> float:
        return float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)))

    def listen(self) -> str:
        """
         Record audio until silence or timeout, then transcribe with Whisper.

        Returns the recognised text string (may be empty if nothing was said)."""
        if self._model is None:
            raise RuntimeError("Call start() before listen().")

        chunks: list[np.ndarray] = []
        stop_event = threading.Event()
        silence_timer: list[threading.Timer | None] = [None]

        def callback(indata, frames, time_info, status):
            chunk = np.frombuffer(bytes(indata), dtype=np.int16).copy()
            chunks.append(chunk)

            if self._rms(chunk) > self.silence_threshold:
                if silence_timer[0]:
                    silence_timer[0].cancel()
                    silence_timer[0] = None
            else:
                if not silence_timer[0]:
                    silence_timer[0] = threading.Timer(self.silence_duration, stop_event.set)
                    silence_timer[0].start()

        hard_timer = threading.Timer(self.max_duration, stop_event.set)
        hard_timer.start()

        with sd.RawInputStream(samplerate=self.samplerate, blocksize=4000, dtype="int16", channels=1, callback=callback):
            stop_event.wait()

        hard_timer.cancel()
        if silence_timer[0]:
            silence_timer[0].cancel()

        if not chunks:
            return ""

        audio = np.concatenate(chunks).astype(np.float32) / 32768.0
        segments, _ = self._model.transcribe(
            audio,
            language=self.language,
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
        )

        return " ".join(seg.text.strip() for seg in segments).strip()


if __name__ == "__main__":
    stt = STT( 
        device="cuda",            # change to "cuda" if you have an NVIDIA GPU
        compute_type="float16",     # "float16" recommended on GPU
    )
    stt.start()
    recognised = stt.listen()
    print(f"Recognised: {recognised}")
    stt.stop()