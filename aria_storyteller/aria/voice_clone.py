"""
voice_clone.py — Voice reference analysis and voice style transfer.
Groq's playai-tts uses a reference voice file to match speaking style.
Note: Groq TTS voice cloning works via the "voice" parameter with reference
audio when supported. This module handles that integration.
"""

import os
from pathlib import Path


def validate_reference_voice(path: str) -> tuple[bool, str]:
    """
    Validate that the reference voice file is suitable.
    Returns (is_valid, message).
    """
    if not path or not os.path.exists(path):
        return False, f"Voice file not found: {path}"

    p = Path(path)
    if p.suffix.lower() not in [".wav", ".mp3", ".ogg", ".flac", ".m4a"]:
        return False, f"Unsupported format: {p.suffix}. Use .wav, .mp3, .ogg, .flac, or .m4a"

    size_mb = os.path.getsize(path) / (1024 * 1024)
    if size_mb > 25:
        return False, f"File too large ({size_mb:.1f} MB). Keep under 25 MB for best results."
    if size_mb < 0.001:
        return False, "File appears empty."

    return True, f"Voice file OK — {p.name} ({size_mb:.2f} MB)"


def get_voice_instructions() -> str:
    return """
╔══════════════════════════════════════════════════════════════════╗
║              ARIA — VOICE REFERENCE SETUP                        ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  To give Aria a custom voice, provide a reference audio file.   ║
║                                                                  ║
║  HOW IT WORKS:                                                   ║
║  ─────────────                                                   ║
║  Groq's Orpheus TTS (playai-tts) can match the style, tone,     ║
║  and cadence of a reference voice you provide.                   ║
║                                                                  ║
║  SETUP STEPS:                                                    ║
║  ─────────────                                                   ║
║  1. Find or record an audio clip of the voice you want.         ║
║     • Best results: 10-60 seconds of clear speech               ║
║     • Format: .wav or .mp3                                       ║
║     • No background music or noise                               ║
║                                                                  ║
║  2. Place the file in: ./audio/reference_voice.wav              ║
║     (or update VOICE_REFERENCE_PATH in .env)                     ║
║                                                                  ║
║  3. Run Aria — the voice will be used automatically.            ║
║                                                                  ║
║  NOTE: If no reference file is provided, Aria uses the          ║
║  default Fritz-PlayAI Orpheus voice.                             ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""
