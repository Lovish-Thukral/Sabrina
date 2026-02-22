from neutts import NeuTTS
import sounddevice as sd
import json
import numpy as np
import threading
import queue

# Initialize TTS
tts = NeuTTS(
    backbone_repo="/home/nullbyte/Desktop/Sabrina/models/neutts/neutss-air-BF16.gguf",
    backbone_device="gpu",
    language="en-us",
    codec_repo="neuphonic/neucodec-onnx-decoder-int8",
    codec_device="cpu"
)

# Load reference
with open("CoreTTS/Samples/codec.json", "r") as f:
    codec_data = json.load(f)

ref_codes = np.array(codec_data["Lily"]["Audio"], dtype=np.int32)
ref_text = codec_data["Lily"]["Script"]

samplerate = 22000

# Queue for streaming audio chunks
audio_queue = queue.Queue(maxsize=20)

# Flag to signal playback start
playback_started = threading.Event()

# Buffer storage
buffer_chunks = []

# Generator thread (producer)
def generate_audio():
    audio_stream = tts._infer_stream_ggml(
        input_text="Good evening, Lovish! It's February twenty-second, 2026. How's your day going so far? I'm feeling quite well, thank you! What about you?",
        ref_codes=ref_codes,
        ref_text=ref_text
    )

    total_chunks = 0

    for chunk in audio_stream:
        audio_queue.put(chunk)
        buffer_chunks.append(chunk)
        total_chunks += 1

        # Start playback once 50% buffer threshold reached
        if total_chunks == 3:   # adjust based on chunk size (5–10 ideal)
            playback_started.set()
    audio_queue.put(None)  # signal end


# Playback thread (consumer)
def play_audio():
    playback_started.wait()

    stream = sd.OutputStream(
        samplerate=samplerate,
        channels=1,
        dtype="float32",
        blocksize=1024
    )

    stream.start()
    x = 0
    while True:
        chunk = audio_queue.get()

        if chunk is None:
            break
        print(chunk)
        x += 1
        stream.write(chunk)

    stream.stop()
    stream.close()
    print(x)


# Run threads
producer = threading.Thread(target=generate_audio)
consumer = threading.Thread(target=play_audio)

producer.start()
consumer.start()

producer.join()
consumer.join()

tts.backbone.close()