[README (1).md](https://github.com/user-attachments/files/28124937/README.1.md)
# ✦ Aria — The Eternal Storyteller

An AI-powered interactive narrative engine. Aria tells stories that **never end**, voices every character in the world, and crafts situations that challenge your emotional intelligence, situational awareness, resilience, and social fluency.

---

## 🗂 Folder Structure

```
aria_storyteller/
├── .env                    ← Paste your API keys here
├── .gitignore
├── requirements.txt
├── README.md
├── run.py                  ← Start here: python run.py
│
├── config/
│   └── api_keys.txt        ← Instructions for getting your API keys
│
├── audio/
│   └── output/             ← Auto-created: TTS audio saved here
│
├── chroma_db/              ← Auto-created: persistent story memory
│
└── aria/
    ├── __init__.py
    ├── core.py             ← Main session orchestrator
    ├── story_engine.py     ← LLM story generation & path planning
    ├── memory.py           ← ChromaDB memory layer
    ├── characters.py       ← Character management
    ├── tts.py              ← ElevenLabs TTS
    ├── voice_clone.py      ← Voice validation helpers
    └── tui.py              ← Rich terminal UI
```

---

## ⚡ Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set your API keys
Open `.env` and fill in all three values:

```env
GROQ_API_KEY=your_groq_api_key_here
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_VOICE_ID=your_voice_id_here
```

| Key | Where to get it |
|---|---|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) → API Keys |
| `ELEVENLABS_API_KEY` | [elevenlabs.io/app/settings/api-keys](https://elevenlabs.io/app/settings/api-keys) |
| `ELEVENLABS_VOICE_ID` | ElevenLabs → Voices → click Aria's voice → copy ID from the URL |

### 3. Run
```bash
python run.py
```

Both `chroma_db/` and `audio/output/` are created automatically on first run.

---

## 🎭 How to Interact

There are only two interaction modes:

| What you type | What it means |
|---|---|
| `me:"..."` | Everything inside the quotes is **your character** in the story — speak, act, and gesture freely |
| Anything without `me:"` | You are speaking **directly to Aria**, out of the story |

### Examples

```
me:"I don't know what you mean. *steps back slowly* Who sent you?"
```
→ Your character speaks, steps back, and speaks again — all in one input.

```
What's the mood of this scene?
```
→ You ask Aria directly, out of story. She'll answer as herself.

---

## 📜 Commands

| Command | Description |
|---|---|
| `/new [premise]` | Start a brand new story (optional: add a premise to shape it) |
| `/characters` | List all characters introduced so far |
| `/addchar Name\|description\|role\|traits` | Manually add a character to the story |
| `/paths` | Ask Aria to reveal 3 possible story directions |
| `/stories` | List all saved stories |
| `/tts on\|off` | Toggle voice narration on or off |
| `/help` | Show all commands |
| `/quit` | Exit Aria |

---

## 🧠 What Aria Tests

Every story is designed to challenge you on:

- **Emotional Intelligence** — reading what others feel, responding with empathy
- **Situational Awareness** — noticing what's happening beneath the surface
- **Self-Awareness** — recognising your own biases and blind spots in the moment
- **Resilience** — handling pressure, failure, and conflict without breaking
- **Social Fluency** — reading the room, knowing when to speak and when to stay silent

Stories are morally complex, never easy. Aria never tells you if you did the right thing — you have to figure that out yourself.

---

## 💾 Memory & Persistence

All story data is stored in ChromaDB (`./chroma_db/`):

- Story events and key scenes
- Character descriptions and live emotional states
- World facts and established rules
- Full dialogue history with semantic search

Stories **resume automatically** on next launch — Aria remembers everything.

---

## 🔧 Configuration (`.env`)

```env
# Required
GROQ_API_KEY=your_groq_key
ELEVENLABS_API_KEY=your_elevenlabs_key
ELEVENLABS_VOICE_ID=your_voice_id

# Auto-managed (no need to change)
CHROMA_PATH=./chroma_db
AUDIO_OUTPUT_DIR=./audio/output
AUTOSAVE_INTERVAL=5
```

---

## 🤖 Models Used

| Role | Model |
|---|---|
| Story Generation (LLM) | `moonshotai/kimi-k2-instruct` via Groq |
| Voice (TTS) | ElevenLabs `eleven_multilingual_v2` with your custom Aria voice |

