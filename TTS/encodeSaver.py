from neutts import NeuTTS
import os
from pathlib import Path
import json
from neutts import NeuTTS
import os
from pathlib import Path
import json


def codecSaver(audioPath: str, Script: str, Character: str) -> str:
    """
    Encode a reference audio file into a neural codec and store it for voice cloning.

    This function:
    - Loads the NeuTTS model
    - Encodes the given audio file into a codec representation
    - Stores the codec and its associated script under a character name
    - Safely updates the codec JSON file

    Args:
        audioPath (str): Absolute path to the reference audio file.
        Script (str): Sample dialogue associated with the voice.
        Character (str): Unique identifier for the voice profile.

    Returns:
        str: Confirmation message after successful save.

    Raises:
        FileExistsError: If the provided audio file does not exist.
    """
    tts = NeuTTS(
        backbone_repo="/home/nullbyte/Desktop/Sabrina/models/neutts/neutss-air-BF16.gguf",
        backbone_device="gpu",
        language="en-us",
        codec_repo="neuphonic/neucodec",
        codec_device="cpu"
    )

    CurrentPath = Path(__file__).parent.parent.absolute()

    if not os.path.isfile(audioPath):
        raise FileExistsError("Given Audio Path Does'nt Exists")

    codecPath = f"{CurrentPath}/CoreTTS/Samples/codec.json"
    with open(codecPath, mode="r") as f:
        data = json.load(f)

    if not data:
        data = {}

    audio = tts.encode_reference(audioPath)

    data[Character] = {
        "Script": Script,
        "Audio": audio.tolist()
    }

    tempPath = f"{CurrentPath}/CoreTTS/Samples/temp.json"
    with open(tempPath, mode="w") as f:
        json.dump(data, f, indent=4)

    os.replace(tempPath, codecPath)
    tts.backbone.close()

    return f"Cloning Codec Saved for {Character}"


if __name__ == "__main__":
    path = "/home/nullbyte/Desktop/Sabrina/CoreTTS/Samples/nitin.mp3"
    script = "Wait… did you hear that? No, listen carefully. It’s fine, don’t worry. Things are under control now. Stay alert, and let’s continue"
    Character = "Nitin"

    print(codecSaver(audioPath=path, Script=script, Character=Character))

def codecSaver(audioPath: str, Script: str, Character: str) -> str:
    """
    Encode a reference audio file into a neural codec and store it for voice cloning.

    This function:
    - Loads the NeuTTS model
    - Encodes the given audio file into a codec representation
    - Stores the codec and its associated script under a character name
    - Safely updates the codec JSON file

    Args:
        audioPath (str): Absolute path to the reference audio file.
        Script (str): Sample dialogue associated with the voice.
        Character (str): Unique identifier for the voice profile.

    Returns:
        str: Confirmation message after successful save.

    Raises:
        FileExistsError: If the provided audio file does not exist.
    """
    tts = NeuTTS(
        backbone_repo="/home/nullbyte/Desktop/Sabrina/models/neutts/neutss-air-BF16.gguf",
        backbone_device="gpu",
        language="en-us",
        codec_repo="neuphonic/neucodec",
        codec_device="cpu"
    )

    CurrentPath = Path(__file__).parent.parent.absolute()

    if not os.path.isfile(audioPath):
        raise FileExistsError("Given Audio Path Does'nt Exists")

    codecPath = f"{CurrentPath}/CoreTTS/Samples/codec.json"
    with open(codecPath, mode="r") as f:
        data = json.load(f)

    if not data:
        data = {}

    audio = tts.encode_reference(audioPath)

    data[Character] = {
        "Script": Script,
        "Audio": audio.tolist()
    }

    tempPath = f"{CurrentPath}/CoreTTS/Samples/temp.json"
    with open(tempPath, mode="w") as f:
        json.dump(data, f, indent=4)

    os.replace(tempPath, codecPath)
    tts.backbone.close()

    return f"Cloning Codec Saved for {Character}"


if __name__ == "__main__":
    path = "/home/nullbyte/Desktop/Sabrina/CoreTTS/Samples/nitin.mp3"
    script = "Wait… did you hear that? No, listen carefully. It’s fine, don’t worry. Things are under control now. Stay alert, and let’s continue"
    Character = "Nitin"

    print(codecSaver(audioPath=path, Script=script, Character=Character))