# Sabrina AI

```{=html}
<p align="center">
```
`<img width="300" src="https://res.cloudinary.com/dbjaxxkkf/image/upload/v1774338827/sabrinaAI_h6iprh.png">`{=html}`<br>`{=html}
```{=html}
</p>
```
```{=html}
<p align="center">
```
`<a href="https://github.com/Lovish-Thukral/Sabrina/stargazers">`{=html}
`<img src="https://img.shields.io/github/stars/Lovish-Thukral/Sabrina?style=for-the-badge"/>`{=html}
`</a>`{=html} `<a href="LICENSE">`{=html}
`<img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge"/>`{=html}
`</a>`{=html}
```{=html}
</p>
```

------------------------------------------------------------------------

## Overview

Sabrina AI is a local voice-based assistant for Linux that listens,
processes, responds, and executes commands directly on your system.

------------------------------------------------------------------------

## Workflow

1.  Speech → Vosk (STT)
2.  Text → LLM processing
3.  Response → NeuTTS (TTS)
4.  Execution → Terminal actions

------------------------------------------------------------------------

## Features

-   Offline speech recognition
-   Local LLM support
-   Voice responses
-   Terminal command execution
-   Fully local and private

------------------------------------------------------------------------

## Quickstart

### Clone

``` bash
git clone https://github.com/Lovish-Thukral/Sabrina.git
cd Sabrina
```

### Setup

``` bash
python -m venv venv
source venv/bin/activate
pip install -r requirement.txt
```

### Model Setup

Download model from HuggingFace and place in:

    models/

### Run

``` bash
python main.py
```

------------------------------------------------------------------------

## Architecture

User → Vosk → LLM → NeuTTS → Terminal

------------------------------------------------------------------------

## License

MIT
