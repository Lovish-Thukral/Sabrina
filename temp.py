from neutts import NeuTTS
import sounddevice as sd
import json
import numpy as np
from CoreTTS.encodeSaver import encode_Saver
# Initialize
tts = NeuTTS(
    backbone_repo="neuphonic/neutts-nano",
    backbone_device="cuda",
    language="en-us",
    codec_repo="neuphonic/neucodec-onnx-decoder-int8",
    codec_device="cpu"
)

with open("CoreTTS/Samples/codec.json", "r") as f:
    codec_data = json.load(f)

ref_codes = np.array(codec_data["jo"]["Audio"], dtype=np.int32)
ref_text = codec_data["jo"]["Script"]

# Generate stream
audio_stream = tts.infer_stream(
    text="looking for the passport site? Planning a trip, maybe? Let me handle that search for you and boom! I've got those results pulled up on your screen.",
    ref_codes=ref_codes,
    ref_text=ref_text
)

samplerate = 28000

chunks = []

for chunk in audio_stream:
    chunks.append(chunk)

# Merge into single continuous array
audio = np.concatenate(chunks, axis=0)

# Play properly
sd.play(audio, samplerate)
sd.wait()

tts.backbone.close()