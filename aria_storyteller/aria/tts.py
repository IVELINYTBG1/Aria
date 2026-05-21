"""
tts.py -- Text-to-Speech for Aria using ElevenLabs.
Uses a voice ID from your ElevenLabs account directly — no cloning needed.
"""

import os
import io
import threading
import queue
import re
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

try:
    import sounddevice as sd
    import soundfile as sf
    import numpy as np
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

_CLEAN_PATTERNS = [
    (r'\[Aria[^\]]*\]', ''),
    (r'\[[A-Z][^\]]*\]:', ''),
    (r'\[.*?\]', ''),
    (r'=+[^=]*=+', ''),
    (r'\*\*(.+?)\*\*', r'\1'),
    (r'\*(.+?)\*', r'\1'),
    (r'#+\s', ''),
]

def clean_for_tts(text: str) -> str:
    for pattern, replacement in _CLEAN_PATTERNS:
        text = re.sub(pattern, replacement, text, flags=re.MULTILINE)
    return re.sub(r'\s+', ' ', text).strip()


class AriaVoice:
    """ElevenLabs TTS using a pre-made voice from your ElevenLabs account."""

    MODEL = "eleven_multilingual_v2"

    def __init__(self, api_key: str, voice_id: str,
                 output_dir: str = "./audio/output", enabled: bool = True):
        self.client = ElevenLabs(api_key=api_key)
        self.voice_id = voice_id
        self.output_dir = output_dir
        self.enabled = enabled and AUDIO_AVAILABLE
        self._speech_queue: queue.Queue = queue.Queue()
        self._running = False

        if self.enabled:
            os.makedirs(output_dir, exist_ok=True)
            self._start_playback_worker()

    def _start_playback_worker(self):
        self._running = True
        threading.Thread(target=self._playback_loop, daemon=True).start()

    def _playback_loop(self):
        while self._running:
            try:
                audio_np, sr = self._speech_queue.get(timeout=0.5)
                sd.play(audio_np, sr)
                sd.wait()
                self._speech_queue.task_done()
            except queue.Empty:
                continue
            except Exception:
                continue

    def synthesize(self, text: str) -> bytes:
        clean = clean_for_tts(text)
        if not clean:
            return b""
        audio = self.client.text_to_speech.convert(
            voice_id=self.voice_id,
            text=clean[:5000],
            model_id=self.MODEL,
            voice_settings=VoiceSettings(
                stability=0.45,
                similarity_boost=0.82,
                style=0.35,
                use_speaker_boost=True
            ),
            output_format="pcm_22050"
        )
        return b"".join(audio)

    def speak(self, text: str, blocking: bool = False):
        if not self.enabled or not text.strip():
            return

        def _do():
            try:
                pcm = self.synthesize(text)
                if not pcm:
                    return
                audio_np = np.frombuffer(pcm, dtype=np.int16).astype(np.float32) / 32768.0
                if blocking:
                    sd.play(audio_np, 22050)
                    sd.wait()
                else:
                    self._speech_queue.put((audio_np, 22050))
            except Exception:
                pass

        if blocking:
            _do()
        else:
            threading.Thread(target=_do, daemon=True).start()

    def speak_blocking(self, text: str):
        self.speak(text, blocking=True)

    def stop(self):
        self._running = False
        if AUDIO_AVAILABLE:
            try:
                sd.stop()
            except Exception:
                pass

    def set_enabled(self, val: bool):
        self.enabled = val and AUDIO_AVAILABLE
        if self.enabled and not self._running:
            self._start_playback_worker()

    @staticmethod
    def is_available() -> bool:
        return AUDIO_AVAILABLE
