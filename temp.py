from neutts import NeuTTS
import soundfile as sf

# Initialize
tts = NeuTTS(backbone_repo="models/neutts/neutts-air-Q8_0.gguf", backbone_device="gpu", language="en-us")

# Use the default "Dave" reference included in the repo
ref_audio = "CoreTTS/Samples/jo.wav"
ref_text = "Dans les zones rurales où de nombreuses communautés n'ont pas accès à l'électricité, l'énergie solaire peut faire une énorme différence."

# Encode and Infer
ref_codes = tts.encode_reference(ref_audio)
audio = tts.infer_stream(
    text="Um, looking for the passport site? Planning a trip, maybe? Let me handle that search for you and boom! I've got those results pulled up on your screen.",
    ref_codes=ref_codes,
    ref_text=ref_text
)

for chunk in audio:
    print(chunk.dtype)
    break


# Proper cleanup to avoid the NoneType error
tts.backbone.close()
