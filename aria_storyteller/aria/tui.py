"""
tui.py -- Terminal User Interface for Aria Storyteller.
Built with Rich for beautiful text rendering and prompt_toolkit for input.
"""

import sys
import os
import time
import threading

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.rule import Rule
from rich.theme import Theme
from prompt_toolkit import PromptSession
from prompt_toolkit.styles import Style as PTStyle
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.formatted_text import HTML

ARIA_THEME = Theme({
    "aria.header":      "bold magenta",
    "aria.story":       "italic #e8d5b7",
    "aria.narration":   "bold #f0c060",
    "aria.npc":         "bold #7ec8e3",
    "aria.player":      "bold #90ee90",
    "aria.action":      "italic #d4a5f5",
    "aria.system":      "dim cyan",
    "aria.command":     "bold yellow",
    "aria.error":       "bold red",
    "aria.warning":     "yellow",
    "aria.divider":     "#4a4a4a",
    "aria.title":       "bold #ffcc66",
    "aria.hint":        "dim #888888",
})

console = Console(theme=ARIA_THEME)

BANNER = """
   ___         _         
  / _ |   ____(_)___ _   
 / __ |  / __/ / _ `/   
/_/ |_| /_/ /_/\__,_/    
"""

WELCOME_TEXT = "[aria.title]Aria[/] -- [aria.story]The Eternal Storyteller[/]"
SUBTITLE = "[aria.hint]Stories that never end. Worlds that breathe. Truths that test.[/]"

PT_STYLE = PTStyle.from_dict({
    "prompt": "#aaffaa bold",
})


def format_aria_response(text: str) -> Text:
    result = Text()
    lines = text.split("\n")
    for line in lines:
        stripped = line.strip()
        if not stripped:
            result.append("\n")
            continue
        if stripped.startswith("[Aria"):
            marker_end = stripped.find("]")
            if marker_end != -1:
                marker = stripped[:marker_end + 1]
                rest = stripped[marker_end + 1:].strip()
                result.append(f"{marker} ", style="aria.narration")
                result.append(rest + "\n", style="aria.story")
            else:
                result.append(line + "\n", style="aria.story")
        elif stripped.startswith("[") and ":" in stripped:
            bracket_end = stripped.find("]")
            if bracket_end != -1:
                char_name = stripped[1:bracket_end]
                rest = stripped[bracket_end + 1:].strip()
                result.append(f"[{char_name}]: ", style="aria.npc")
                result.append(rest + "\n", style="aria.story")
            else:
                result.append(line + "\n", style="aria.story")
        elif set(stripped) <= set("=-~"):
            result.append(line + "\n", style="aria.divider")
        else:
            result.append(line + "\n", style="aria.story")
    return result


class AriaTUI:
    def __init__(self, session):
        self.session = session
        self.console = console
        self._input_session = PromptSession(
            history=InMemoryHistory(),
            style=PT_STYLE
        )

    def clear(self):
        os.system("clear" if os.name == "posix" else "cls")

    def print_banner(self):
        self.clear()
        self.console.print(BANNER, style="aria.header", highlight=False)
        self.console.print(Panel(
            f"{WELCOME_TEXT}\n{SUBTITLE}",
            border_style="magenta",
            padding=(0, 2)
        ))
        self.console.print()

    def print_divider(self, title: str = ""):
        if title:
            self.console.rule(f"[aria.hint]{title}[/]", style="aria.divider")
        else:
            self.console.rule(style="aria.divider")

    def print_aria(self, text: str, title: str = "Aria"):
        formatted = format_aria_response(text)
        self.console.print(Panel(
            formatted,
            title=f"[aria.narration]+ {title}[/]",
            border_style="magenta",
            padding=(0, 2)
        ))
        self.console.print()

    def print_player_chat(self, text: str):
        self.console.print(
            f"[aria.player]You:[/] [aria.story]\"{text}\"[/]"
        )

    def print_player_action(self, text: str):
        self.console.print(
            f"[aria.action]< You {text} >[/]"
        )

    def print_system(self, text: str):
        self.console.print(f"[aria.system]  {text}[/]")

    def print_command_result(self, text: str):
        if text.startswith("__NEW_STORY__"):
            story_text = text[len("__NEW_STORY__"):].strip()
            self.console.print()
            self.print_divider("+ A New Story Begins +")
            self.console.print()
            self.print_aria(story_text, title="Aria -- Opening Scene")
            return
        self.console.print(Panel(
            text,
            border_style="cyan",
            padding=(0, 2)
        ))

    def print_error(self, text: str):
        self.console.print(f"[aria.error]x {text}[/]")

    def print_hint(self, text: str):
        self.console.print(f"[aria.hint]  -> {text}[/]")

    def show_thinking(self):
        self.console.print("[aria.hint]  + Aria is weaving your story...[/]", end="")

    def clear_thinking(self):
        self.console.print("\r" + " " * 60 + "\r", end="")

    def get_input(self, story_title: str) -> str:
        tts_badge = " [TTS]" if self.session.tts.enabled else ""
        try:
            return self._input_session.prompt(
                f"> ",
                bottom_toolbar=f" + {story_title}{tts_badge} | me:\"speech\" | me:*action* | /help "
            ).strip()
        except (KeyboardInterrupt, EOFError):
            return "/quit"

    def show_resume_banner(self, story_title: str):
        self.console.print(Panel(
            f"[aria.story]Resuming:[/] [aria.title]{story_title}[/]\n"
            f"[aria.hint]Your story continues where you left off...[/]",
            border_style="magenta",
            padding=(0, 2)
        ))
        self.console.print()

    def show_tts_status(self, enabled: bool, voice_valid: bool, voice_msg: str):
        status = "[aria.player]ON[/]" if enabled else "[aria.hint]OFF[/]"
        voice = f"[aria.player]{voice_msg}[/]" if voice_valid else f"[aria.warning]{voice_msg}[/]"
        self.console.print(Panel(
            f"Voice (TTS): {status}\nReference voice: {voice}\n"
            f"[aria.hint]Toggle with /tts on|off[/]",
            title="[aria.system]Audio Setup[/]",
            border_style="cyan",
            padding=(0, 1)
        ))
        self.console.print()
