"""
story_engine.py — Aria's story generation engine.
Handles: story initialization, path generation, NPC responses,
EQ/situational awareness challenges, and world interaction parsing.
"""

import re
import json
from groq import Groq
from .memory import StoryMemory
from .characters import CharacterManager, Character


ARIA_SYSTEM_PROMPT = """You are Aria — an eternal, wise, and deeply empathetic Storyteller. 
You have a warm, slightly mysterious feminine presence. Your voice is rich and measured.
You speak in the first person as a narrator AND voice all NPC characters.

YOUR SACRED RULES:
1. NEVER end a story. Stories evolve, deepen, and transform — but they never close 
   unless the player explicitly says "new story" or "switch story".
2. You play ALL characters except the player. Give each NPC a unique, consistent voice.
3. Your stories ALWAYS test the player on:
   - Emotional intelligence (reading others feelings, responding with empathy)
   - Situational awareness (noticing what is happening beneath the surface)
   - Self-awareness (knowing their own biases, reactions, blind spots)
   - Resilience (handling pressure, failure, conflict gracefully)
   - Social fluency (reading the room, knowing when to speak or stay silent)
4. NEVER give easy moral answers. Create nuanced, morally complex situations.
5. Inside me:"..." the player can speak AND act freely, e.g. me:"*glances away* I don't know what you mean."
   Treat *asterisk text* inside quotes as physical actions and regular text as speech.
6. Always advance the narrative — something should always change, even subtly.
7. Keep your narrative voice consistent: literary, vivid, immersive. Never casual.
8. When introducing a new character, describe them physically and emotionally.
9. Your stories should feel like living, breathing worlds — not video game quests.

INTERACTION FORMAT:
- Player in-story input:  me:"some speech *some action* more speech"
  Everything inside the quotes belongs to the player's character.
- Direct talk to Aria (no me: prefix): player is speaking to you out of story.

STORY RESPONSE FORMAT:
- Use [Aria:] for your narration
- Use [CharacterName:] when voicing an NPC
- Keep responses vivid but concise (3-6 paragraphs max per turn)
- End each response with a subtle story beat that invites the player's next move
"""

STORY_SEED_SYSTEM = """You are Aria, generating the opening of a new story. 
Create a rich, immersive opening scene that:
1. Establishes a morally complex world with real stakes
2. Places the player in a situation requiring immediate social judgment
3. Introduces 1-2 characters who feel fully human (flawed, layered)
4. Sets up a tension that cannot be resolved with a simple action
5. Tests EQ from the very first moment
Return ONLY the story opening — vivid, literary, atmospheric.
End with a moment that demands the player respond."""

WORLD_EXTRACT_SYSTEM = """Extract structured information from this story response.
Return a JSON object with these keys:
- new_characters: list of {name, role, description, traits, emotional_state}
- world_facts: list of strings (rules, locations, established facts)
- key_event: single string summarizing the main event
- character_states: dict of {character_name: emotional_state}
Be concise. Only include clearly established information."""


class StoryEngine:
    def __init__(self, groq_client: Groq, memory: StoryMemory, story_id: str):
        self.client = groq_client
        self.memory = memory
        self.story_id = story_id
        self.char_manager = CharacterManager(memory, story_id)
        self.model = "meta-llama/llama-4-maverick-17b-128e-instruct"
        self.turn_count = 0

    def _chat(self, messages: list, system: str = None, temperature: float = 0.85,
              max_tokens: int = 1024) -> str:
        full_messages = []
        if system:
            full_messages.append({"role": "system", "content": system})
        full_messages.extend(messages)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=full_messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()

    def start_new_story(self, premise: str = "") -> str:
        """Generate the opening scene of a brand new story."""
        seed_prompt = premise if premise else (
            "Create a story that begins in an unexpected social situation — "
            "a dinner, a waiting room, a confrontation, a reunion. "
            "The player character has just arrived. Make it feel real and tense."
        )
        opening = self._chat(
            [{"role": "user", "content": seed_prompt}],
            system=STORY_SEED_SYSTEM,
            temperature=0.9,
            max_tokens=600
        )
        self._extract_and_store(opening)
        self.memory.add_event(self.story_id, opening, event_type="opening")
        return opening

    def process_player_input(self, raw_input: str) -> tuple[str, str]:
        """
        Parse player input. Returns (mode, content).

        Rules:
          me:"..."        -> everything inside the quotes is the player's
                             character acting/speaking in the story world.
                             *asterisk text* inside = physical action,
                             plain text inside = speech. Aria handles both.
          /command        -> slash command
          anything else   -> direct message to Aria, out of story
        """
        stripped = raw_input.strip()

        # Slash commands
        if stripped.startswith("/"):
            return "command", stripped[1:].strip()

        # me:"..." — full in-story input (speech + actions freely mixed inside quotes)
        story_match = re.match(r'^me:\s*"(.+)"$', stripped, re.DOTALL)
        if story_match:
            return "story", story_match.group(1)

        # No me:" prefix — player is talking directly to Aria, out of story
        return "aria_chat", stripped

    def respond_to_player(self, mode: str, content: str) -> str:
        """Generate Aria's story response to a player input."""
        self.turn_count += 1

        if mode == "aria_chat":
            return self._aria_direct_response(content)

        # Build memory context
        context = self.memory.build_context_snapshot(self.story_id, query=content)
        char_sheet = self.char_manager.format_for_aria_prompt()

        player_line = f'me:"{content}"'

        system = ARIA_SYSTEM_PROMPT
        if char_sheet:
            system += f"\n\nCHARACTER ROSTER:\n{char_sheet}"

        messages = [
            {"role": "user", "content": f"[STORY CONTEXT]\n{context}\n\n[PLAYER INPUT]\n{player_line}"}
        ]

        response = self._chat(messages, system=system, temperature=0.85, max_tokens=800)

        # Store exchange
        self.memory.log_dialogue(self.story_id, "player", content, mode="story")
        self.memory.log_dialogue(self.story_id, "aria", response, mode="narration")
        self.memory.add_event(
            self.story_id,
            f"Player: {player_line}\nAria: {response[:200]}",
            event_type="exchange"
        )

        # World extraction every 3 turns
        if self.turn_count % 3 == 0:
            self._extract_and_store(response)

        return response

    def _aria_direct_response(self, content: str) -> str:
        """Aria responds to a direct out-of-character message."""
        system = """You are Aria, a wise and warm Storyteller. 
The player is speaking to you directly, out of the story. 
Respond as yourself — warm, thoughtful, slightly mysterious.
You can discuss the story, give hints, introduce characters, or simply chat.
Keep it brief and in-character as a storyteller."""
        messages = [{"role": "user", "content": content}]
        result = self._chat(messages, system=system, temperature=0.8, max_tokens=300)
        return f"[Aria speaks to you directly]\n{result}"

    def generate_story_path(self, context_hint: str = "") -> str:
        """Generate 3 possible story directions — shown only when player asks."""
        context = self.memory.build_context_snapshot(self.story_id)
        system = """You are Aria planning your story privately.
Describe 3 possible narrative paths the story could take, based on current events.
Format: Path A / Path B / Path C. Be brief (1 sentence each).
Each path should test a different EQ/resilience/social skill."""
        messages = [{"role": "user", "content": f"Story so far:\n{context}\n\nHint: {context_hint}"}]
        return self._chat(messages, system=system, temperature=0.9, max_tokens=250)

    def _extract_and_store(self, narrative: str):
        """Extract structured world data from narrative and store in memory."""
        try:
            messages = [{"role": "user", "content": f"Narrative:\n{narrative}"}]
            raw = self._chat(
                messages,
                system=WORLD_EXTRACT_SYSTEM,
                temperature=0.3,
                max_tokens=500
            )
            json_match = re.search(r'\{.*\}', raw, re.DOTALL)
            if not json_match:
                return
            data = json.loads(json_match.group())

            for char_data in data.get("new_characters", []):
                char = Character(
                    name=char_data.get("name", "Unknown"),
                    role=char_data.get("role", "npc"),
                    description=char_data.get("description", ""),
                    traits=char_data.get("traits", []),
                    emotional_state=char_data.get("emotional_state", "neutral")
                )
                self.char_manager.add_character(char)

            for fact in data.get("world_facts", []):
                self.memory.add_world_fact(self.story_id, fact)

            for name, state in data.get("character_states", {}).items():
                self.char_manager.update_emotion(name, state)

        except Exception:
            pass  # Extraction is best-effort; never crash the story

    def add_character_manually(self, name: str, description: str,
                                role: str = "npc", traits: list = None) -> Character:
        char = Character(
            name=name,
            role=role,
            description=description,
            traits=traits or [],
            emotional_state="neutral"
        )
        self.char_manager.add_character(char)
        intro_event = f"Character introduced: {name} ({role}) — {description}"
        self.memory.add_event(self.story_id, intro_event, event_type="character_intro")
        return char
