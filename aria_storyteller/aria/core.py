"""
core.py -- Aria's central orchestrator.
"""

import os
import uuid
from dotenv import load_dotenv
from groq import Groq

from .memory import StoryMemory
from .story_engine import StoryEngine
from .tts import AriaVoice

load_dotenv()


class AriaSession:

    def __init__(self):
        groq_key = os.getenv("GROQ_API_KEY", "")
        if not groq_key or groq_key == "your_groq_api_key_here":
            raise ValueError("GROQ_API_KEY not set. Open .env and paste your Groq API key.")

        eleven_key = os.getenv("ELEVENLABS_API_KEY", "")
        if not eleven_key or eleven_key == "your_elevenlabs_api_key_here":
            raise ValueError("ELEVENLABS_API_KEY not set. Open .env and paste your ElevenLabs API key.")

        voice_id = os.getenv("ELEVENLABS_VOICE_ID", "")
        if not voice_id or voice_id == "your_voice_id_here":
            raise ValueError("ELEVENLABS_VOICE_ID not set. Open .env and paste Aria's voice ID from ElevenLabs.")

        self.groq_client = Groq(api_key=groq_key)
        self.memory = StoryMemory(persist_path=os.getenv("CHROMA_PATH", "./chroma_db"))

        self.tts = AriaVoice(
            api_key=eleven_key,
            voice_id=voice_id,
            output_dir=os.getenv("AUDIO_OUTPUT_DIR", "./audio/output"),
            enabled=True
        )
        self.voice_ref_valid = True
        self.voice_ref_msg = f"Using ElevenLabs voice ID: {voice_id[:8]}..."

        self.current_story_id: str = None
        self.engine: StoryEngine = None
        self._resume_or_create_story()

    def _resume_or_create_story(self):
        active = self.memory.get_active_story()
        if active:
            self.current_story_id = active["story_id"]
            self.engine = StoryEngine(self.groq_client, self.memory, self.current_story_id)
            return True, active.get("title", "Untitled")
        return False, None

    def new_story(self, title: str = "", premise: str = "") -> str:
        if self.current_story_id:
            self.memory.deactivate_story(self.current_story_id)
        story_id = str(uuid.uuid4())[:8]
        self.current_story_id = story_id
        self.memory.save_story_meta(story_id, title or f"Story {story_id}")
        self.engine = StoryEngine(self.groq_client, self.memory, story_id)
        return self.engine.start_new_story(premise=premise)

    def send(self, raw_input: str) -> tuple[str, str]:
        if not self.engine:
            return "aria", "No story active. Type /new to start a new story."
        mode, content = self.engine.process_player_input(raw_input)
        if mode == "command":
            return "command", self._handle_command(content)
        return "story", self.engine.respond_to_player(mode, content)

    def _handle_command(self, cmd: str) -> str:
        parts = cmd.strip().split(None, 1)
        verb = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if verb in ("new", "new_story"):
            return f"__NEW_STORY__\n{self.new_story(premise=arg)}"

        elif verb == "characters":
            chars = self.engine.char_manager.list_characters() if self.engine else []
            if not chars:
                return "No characters introduced yet."
            return "\n".join(["Characters:"] + [
                f"  • {c.name} [{c.role}] — {c.description[:60]} | {c.emotional_state}"
                for c in chars
            ])

        elif verb == "addchar":
            if not arg:
                return "Usage: /addchar Name | description | role | trait1, trait2"
            p = [x.strip() for x in arg.split("|")]
            traits = [t.strip() for t in p[3].split(",")] if len(p) > 3 else []
            char = self.engine.add_character_manually(
                p[0], p[1] if len(p)>1 else "",
                p[2] if len(p)>2 else "npc", traits
            )
            return f"Character added: {char.name} ({char.role})"

        elif verb in ("paths", "whatnext"):
            return f"Possible story paths:\n{self.engine.generate_story_path()}"

        elif verb == "stories":
            stories = self.memory.list_stories()
            if not stories:
                return "No stories saved yet."
            return "\n".join(["Saved stories:"] + [
                f"  [{'●' if s.get('active')=='true' else '○'}] {s.get('title','?')}"
                for s in stories
            ])

        elif verb in ("tts", "voice"):
            if arg.lower() in ("on", "enable"):
                self.tts.set_enabled(True); return "Voice enabled."
            elif arg.lower() in ("off", "disable"):
                self.tts.set_enabled(False); return "Voice disabled."
            return f"TTS: {'enabled' if self.tts.enabled else 'disabled'}. Use /tts on|off"

        elif verb in ("help", "?"):
            return HELP_TEXT

        else:
            return f"Unknown command: /{verb}. Type /help for commands."

    def speak(self, text: str):
        if self.tts.enabled:
            self.tts.speak(text)

    def get_story_title(self) -> str:
        active = self.memory.get_active_story()
        return active.get("title", "Untitled Story") if active else "No Active Story"

    def cleanup(self):
        self.tts.stop()


HELP_TEXT = """
+-------------------------------------------------------+
|                   ARIA -- COMMANDS                    |
+-------------------------------------------------------+
|  me:"Hello *waves* who are you?"  -> in the story    |
|  (no me: prefix)                  -> talk to Aria     |
|                                                       |
|  /new [premise]        -> start a new story          |
|  /characters           -> list characters            |
|  /addchar Name|desc|role|traits -> add character     |
|  /paths                -> see 3 story directions     |
|  /stories              -> list saved stories         |
|  /tts on|off           -> toggle voice               |
|  /help                 -> show this help             |
|  /quit                 -> exit                       |
+-------------------------------------------------------+
"""
