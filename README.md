<p align="center">
  <img src="https://res.cloudinary.com/dbjaxxkkf/image/upload/v1774338827/sabrinaAI_h6iprh.png" width="160" alt="Sabrina AI Logo" />
</p>

<h1 align="center">Sabrina AI</h1>

<p align="center">
  <em>A fully local, voice-based AI assistant for Linux</em>
</p>

<p align="center">
  <a href="https://github.com/Lovish-Thukral/Sabrina/stargazers">
    <img src="https://img.shields.io/github/stars/Lovish-Thukral/Sabrina?style=for-the-badge&color=63b3ed&labelColor=0d1117" alt="Stars"/>
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-f6e05e?style=for-the-badge&labelColor=0d1117" alt="MIT License"/>
  </a>
  <img src="https://img.shields.io/badge/Platform-Linux-68d391?style=for-the-badge&labelColor=0d1117" alt="Linux"/>
  <img src="https://img.shields.io/badge/Python-3.8+-9f7aea?style=for-the-badge&labelColor=0d1117" alt="Python"/>
</p>

---

## 🧠 Overview

**Sabrina AI** is a fully offline, voice-based assistant for Linux that listens to your voice, processes it with a local LLM, responds with speech, and executes terminal commands — all **on your machine, with zero cloud dependency**.

No API keys. No telemetry. No internet required.

---

## ⚡ Workflow

```
🎙️ Speech  →  👂 Vosk (STT)  →  🧠 LLM  →  🔊 NeuTTS (TTS)  →  ⚙️ Terminal
```

| Step | Component | Role |
|------|-----------|------|
| 1 | **Vosk** | Offline speech-to-text |
| 2 | **LLM** | Local language model processing |
| 3 | **NeuTTS** | Text-to-speech response |
| 4 | **Terminal** | Command execution |

---

## ✨ Features

- 📴 **Offline Speech Recognition** — powered by Vosk, works without internet
- 🧠 **Local LLM Support** — bring your own model from HuggingFace
- 🔊 **Voice Responses** — natural speech output via NeuTTS
- 💻 **Terminal Command Execution** — interact directly with your system
- 🔒 **Fully Private** — your data never leaves your machine

---

## 🚀 Quickstart

### 1. Clone the repo

```bash
git clone https://github.com/Lovish-Thukral/Sabrina.git
cd Sabrina
```

### 2. Set up the environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirement.txt
```

### 3. Download a model

Download your preferred LLM from [HuggingFace](https://huggingface.co) and place it in the `models/` directory:

```
Sabrina/
└── models/
    └── your-model-file-here
```

### 4. Run

```bash
python main.py
```

---

## 🏗️ Architecture

```
User ──► Vosk (STT) ──► LLM ──► NeuTTS (TTS) ──► Terminal
```

---

## 📄 License

This project is licensed under the **MIT License**.

> **What does MIT mean?**
> - ✅ Free to use, copy, modify, distribute, and even sell
> - 📌 Only requirement: keep the original copyright notice in any copy
> - ⚠️ No warranty — software is provided "as is"
>
> In short: *do almost anything you want with it, just give credit.*

See the [LICENSE](LICENSE) file for full details.

---

<p align="center">
  Built with ♥ by <a href="https://github.com/Lovish-Thukral">Lovish Thukral</a>
</p>