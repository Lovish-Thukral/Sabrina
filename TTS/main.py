from neutts import NeuTTS
import sounddevice
import json
import numpy
import queue
import threading
import os

class TTS:
    """Persistent NeuTTS text-to-speech engine with streaming playback."""
    def __init__(
        self,
        modelPath="models/neutts/neutts-air-Q4_0.gguf",
        cloningChar = "Lily"
    ):
        self.decoderPath = "neuphonic/neucodec-onnx-decoder-int8"
        self.model = None
        self.running = False
        if os.path.exists(modelPath):
            self.modelPath = modelPath
        else:
            self.modelPath = "neuphonic/neutts-air-q4-gguf"
        try:
            with open("TTS/Samples/codec.json", "r") as f:
                self.voiceData = json.load(f)
        except FileNotFoundError as e:
            raise FileNotFoundError("codec.json missing in TTS/Samples") from e
        self.cloningChar = cloningChar
    
    def start(self):
        "Loads The Model To Memory, Must Be Called before play()"
        self.running = True
        self.model = NeuTTS(
            backbone_device="gpu",
            backbone_repo=self.modelPath,
            language="en-us",
            codec_repo=self.decoderPath,
            codec_device="cpu"
        )
        return
    
    def stop(self):
        """Unloads the model."""
        self.running = False
        self.model.backbone.close()
        self.model = None
        return

    def play(self, text:str, cloningChar = None):
        """Generate and play speech from text.

        Parameters
        ----------
        text : str
            Input text to synthesize.

        cloningchar : str
            Voice profile name from codec.json.
        """
        cloning = cloningChar if cloningChar is not None else self.cloningChar
        cloningCodec = numpy.array(self.voiceData[cloning]["Audio"], dtype=numpy.int32)
        cloningScript = self.voiceData[cloning]["Script"]
        streamQueue = queue.Queue()
        player = threading.Event()
        
        def generate_audio():
            chunks = self.model._infer_stream_ggml(input_text= text, ref_codes=cloningCodec, ref_text=cloningScript)
            chunksSize = 0
            for chunk in chunks:
               streamQueue.put(chunk)
               chunksSize += 1
               if chunksSize == 3:
                   player.set()
            streamQueue.put(None)
            if chunksSize < 3:
                player.set()
        
        def stream_audio():
            player.wait()
            stream = sounddevice.OutputStream(
                samplerate=23000,
                channels=1,
                dtype="float32"
            )
            stream.start()
            while True:
                chunk = streamQueue.get()
                if chunk is None:
                    break
                stream.write(chunk)

            stream.stop()
            stream.close()
        generate = threading.Thread(target=generate_audio)
        consumer = threading.Thread(target=stream_audio)
        generate.start()
        consumer.start()
        generate.join()
        consumer.join()

    
if __name__ == "__main__":
    tts = TTS()
    tts.start()
    for i in range(1, 10):
        x = input()
        tts.play(x)
    tts.stop()