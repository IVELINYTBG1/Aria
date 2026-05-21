"""
characters.py — Character management for Aria's stories.
Handles the player character and all NPC/world characters.
"""

import json
from dataclasses import dataclass, field, asdict
from typing import Optional
from .memory import StoryMemory


@dataclass
class Character:
    name: str
    role: str  # "player", "npc", "antagonist", "mentor", etc.
    description: str
    traits: list[str] = field(default_factory=list)
    emotional_state: str = "neutral"
    backstory: str = ""
    relationships: dict = field(default_factory=dict)  # {name: relationship_desc}
    arc: str = ""  # Character development arc hint


class CharacterManager:
    """Manages all characters within a story."""

    def __init__(self, memory: StoryMemory, story_id: str):
        self.memory = memory
        self.story_id = story_id
        self._cache: dict[str, Character] = {}

    def add_character(self, char: Character) -> Character:
        """Add or update a character in memory."""
        self.memory.upsert_character(
            story_id=self.story_id,
            name=char.name,
            description=char.description,
            traits=char.traits,
            role=char.role,
            emotional_state=char.emotional_state
        )
        self._cache[char.name.lower()] = char
        return char

    def get_character(self, name: str) -> Optional[Character]:
        key = name.lower()
        if key in self._cache:
            return self._cache[key]
        chars = self.memory.get_characters(self.story_id)
        for c in chars:
            if c["name"].lower() == key:
                char = Character(
                    name=c["name"],
                    role=c["role"],
                    description=c["description"],
                    traits=c.get("traits", []),
                    emotional_state=c.get("emotional_state", "neutral")
                )
                self._cache[key] = char
                return char
        return None

    def list_characters(self) -> list[Character]:
        raw = self.memory.get_characters(self.story_id)
        result = []
        for c in raw:
            result.append(Character(
                name=c["name"],
                role=c["role"],
                description=c["description"],
                traits=c.get("traits", []),
                emotional_state=c.get("emotional_state", "neutral")
            ))
        return result

    def update_emotion(self, name: str, state: str):
        self.memory.update_character_state(self.story_id, name, state)
        if name.lower() in self._cache:
            self._cache[name.lower()].emotional_state = state

    def get_character_sheet(self) -> str:
        """Format all characters for prompt injection."""
        chars = self.list_characters()
        if not chars:
            return "No characters introduced yet."
        lines = []
        for c in chars:
            traits = ", ".join(c.traits) if c.traits else "—"
            lines.append(
                f"• {c.name} [{c.role.upper()}] | {c.description} "
                f"| Traits: {traits} | State: {c.emotional_state}"
            )
        return "\n".join(lines)

    def format_for_aria_prompt(self) -> str:
        """Character context Aria uses to voice NPCs."""
        chars = [c for c in self.list_characters() if c.role != "player"]
        if not chars:
            return ""
        lines = ["You play ALL of these characters (never the player):"]
        for c in chars:
            traits_str = ", ".join(c.traits) if c.traits else "no specific traits"
            lines.append(
                f"  [{c.name}] — {c.description}. "
                f"Traits: {traits_str}. Current mood: {c.emotional_state}."
            )
        return "\n".join(lines)
