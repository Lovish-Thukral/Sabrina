from neutts import NeuTTS
import sounddevice
import json
import numpy
import queue
import threading

class TTSModel:

    def __init__(
        self,
        modelPath="models/neutts/neutss-air-BF16.gguf",
        decoderPath="neuphonic/neucodec-onnx-decoder-int8"
    ):

        self.model = NeuTTS(
            backbone_device="cpu",
            backbone_repo=modelPath,
            language="en-us",
            codec_repo=decoderPath,
            codec_device="cpu"
        )
        self.running = False

    def play(self, text:str, cloningchar = "Lily"):
        """
        main Loop To Run the model
        """
        player = threading.Event()
        with open("CoreTTS/Samples/codec.json", "r") as f:
            voiceData = json.load(f)
        cloningCodec = numpy.array(voiceData[cloningchar]["Audio"], dtype=numpy.int32)
        cloningScript = voiceData[cloningchar]["Script"]
        
        while self.running:
            chunks = self.model._infer_stream_ggml(input_text= text, ref_codes=cloningCodec, ref_text=cloningScript)
            chunksSize = 0
            stream = sounddevice.OutputStream(
                samplerate=23000,
                channels=1,
                dtype="float32",
                blocksize=256
            )
            streamQueue = queue.Queue()
            stream.start()
            for chunk in chunks:
               streamQueue.put(chunk)
               chunksSize += 1
               if chunksSize == 3:
                   player.set()
            streamQueue.put(None)
            

    
if __name__ == "__main__":
    tts = TTSModel()
    tts.running = True
    tts.play(text="Wait… did you hear that? No, listen carefully. It’s fine, don’t worry. Things are under control now. Stay alert, and let’s continue")
    tts.running = False
    tts.model.backbone.close()