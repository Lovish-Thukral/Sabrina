from pathlib import Path
import json
def encode_Saver(audio, Character, Script, model):
    ParentPath = Path(__file__).parent.parent.absolute()
    filepath = ParentPath / "CoreTTS" / "Samples" / "codec.json"
    if not Path.exists(filepath):
        raise FileNotFoundError(f"Can't Find {filepath}")
    with open(filepath, "r") as f:
        prevData = json.load(f)
    audio_codec = model.encode_reference(audio)
    prevData[Character.strip()] = {"Script": Script.strip(), "Audio": audio_codec.tolist()}
    with open(filepath, "w") as f:
        json.dump(prevData, f, indent=4)  
if __name__ == "__main__":
    encode_Saver("test", "test", "test text")
    
    