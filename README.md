# 🤖 SABRINA

**SABRINA** is a local, wake-word–activated AI assistant that understands user commands and performs real system-level actions.

It runs **Qwen2.5-Coder-Instruct 7B** locally using **llama.cpp**, with **Python** handling decision logic and system automation.

No cloud. No telemetry. Just compute.

---

## 🧠 What It Does

- Listens for a **wake word** before activating
- Understands **natural language commands**
- Decides whether to:
  - Answer a query, or
  - Execute a system function
- Performs controlled OS-level operations via Python

---

## ⚙️ Tech Stack

- **LLM**: Qwen2.5-Coder-Instruct 7B  
- **Inference**: llama.cpp  
- **Language**: Python  
- **Mode**: Local, offline, system-aware agent

---

## 🖥 System Requirements

- **GPU**: Minimum **4 GB VRAM** (recommended for usable inference speed)
- **CPU**: Modern x86_64 processor
- **RAM**: 8 GB or more
- **OS**: Linux (primary target)

> CPU-only execution is technically possible but not practical.

---

## 🚀 Current Features

- Wake-word activation  
- Natural language query handling  
- System operations:
  - Open applications
  - Install and update packages
  - Manage apps
  - Shutdown system

All actions are executed through predefined Python functions, not raw LLM shell access.

---

## 🛣 Planned Features

- Web and local search
- Weather fetching
- Information and news summaries
- Persistent memory and context
- File and directory management
- Plugin-based skill system

(Planned, not implemented yet.)

---

## 🧪 Status

Active development. Built for experimentation with local AI agents.

---

## ⚠️ Disclaimer

SABRINA can control parts of your system.  
Use it only on machines you’re comfortable breaking and fixing.

---

## 📄 License

Add one when ready.
