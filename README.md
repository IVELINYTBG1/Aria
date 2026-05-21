[README.md](https://github.com/user-attachments/files/28124411/README.md)
# Aria# ✦ Aria — The Eternal Storyteller

An AI-powered interactive narrative engine. Aria tells stories that **never end**, 
voices every character in the world, and crafts situations that challenge your 
emotional intelligence, situational awareness, resilience, and social fluency.

---

## 🗂 Folder Structure

```
aria_storyteller/
├── .env                    ← Paste your API key here
├── .gitignore
├── requirements.txt
├── README.md
├── run.py                  ← Start here: python run.py
│
├── config/
│   └── api_keys.txt        ← Instructions for getting your Groq API key
│
├── audio/
│   ├── reference_voice.wav ← Put your voice reference file here
│   └── output/             ← Generated TTS audio saved here
│
├── chroma_db/              ← Auto-created: persistent story memory
│
└── aria/
    ├── __init__.py
    ├── core.py             ← Main session orchestrator
    ├── story_engine.py     ← LLM story generation & path planning
    ├── memory.py           ← ChromaDB memory layer
    ├── characters.py       ← Character management
    ├── tts.py              ← Orpheus TTS via Groq
    ├── voice_clone.py      ← Voice reference validation
    └── tui.py              ← Rich terminal UI
```

---

## ⚡ Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set your API key
Open `.env` and paste your Groq API key:
```
GROQ_API_KEY=gsk_your_key_here
```
Get a free key at [console.groq.com](https://console.groq.com)

### 3. (Optional) Add a reference voice
Drop an audio file into `audio/reference_voice.wav` to give Aria your chosen voice.  
See `config/api_keys.txt` for more details.

### 4. Run
```bash
python run.py
```

---

## 🎭 How to Interact

| Input Format | Meaning |
|---|---|
| `me:"Hello, who are you?"` | Your character **speaks** in the story world |
| `me:*looks around the room slowly*` | Your character **acts** in the story world |
| `What's happening in this story?` | You speak **directly to Aria** (out of story) |

---

## 📜 Commands

| Command | Description |
|---|---|
| `/new [premise]` | Start a brand new story (optional: add a premise) |
| `/characters` | List all characters introduced so far |
| `/addchar Name\|description\|role\|traits` | Add a new character to the story |
| `/paths` | Ask Aria to reveal 3 possible story directions |
| `/stories` | List all saved stories |
| `/tts on\|off` | Toggle voice narration |
| `/help` | Show all commands |
| `/quit` | Exit Aria |

---

## 🧠 What Aria Tests

Every story is designed to challenge:
- **Emotional Intelligence** — reading what others feel, responding with care
- **Situational Awareness** — noticing what's happening beneath the surface
- **Self-Awareness** — recognizing your own biases and reactions
- **Resilience** — handling pressure, failure, and conflict gracefully
- **Social Fluency** — reading the room, knowing when to speak or stay silent

---

## 🔧 Configuration (`.env`)

```env
GROQ_API_KEY=your_key_here
CHROMA_PATH=./chroma_db
AUDIO_OUTPUT_DIR=./audio/output
VOICE_REFERENCE_PATH=./audio/reference_voice.wav
AUTOSAVE_INTERVAL=5
```

---

## 🎙 TTS Voice

Aria uses **Orpheus (playai-tts)** via Groq's TTS API with the `Fritz-PlayAI` voice — 
a warm, narrative-quality English voice. Stories are narrated automatically.

Toggle TTS anytime with `/tts off`.

---

## 💾 Memory & Persistence

All story data is stored in ChromaDB (`./chroma_db/`):
- Story events and key scenes
- Character descriptions and emotional states  
- World facts and rules
- Full dialogue history

Stories **resume automatically** on next launch.

---

## Models Used

| Role | Model |
|---|---|
| Story Generation (LLM) | `meta-llama/llama-4-maverick-17b-128e-instruct` |
| Voice (TTS) | `playai-tts` — `Fritz-PlayAI` (Orpheus English) |
