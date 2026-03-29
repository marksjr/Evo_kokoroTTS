import logging
from typing import AsyncGenerator

import edge_tts

from app.utils.audio import mp3_bytes_to_wav_bytes

logger = logging.getLogger(__name__)


class EdgeTTSEngine:
    """Isolated engine for Edge TTS voices."""

    @staticmethod
    def _speed_to_rate(speed: float) -> str:
        percent = round((speed - 1.0) * 100)
        if percent >= 0:
            return f"+{percent}%"
        return f"{percent}%"

    @staticmethod
    def _pitch_to_value(pitch: int) -> str:
        if pitch >= 0:
            return f"+{pitch}Hz"
        return f"{pitch}Hz"

    async def synthesize(self, text: str, voice: str, speed: float, pitch: int, fmt: str) -> bytes:
        chunks = []
        async for chunk in self.synthesize_stream(text, voice, speed, pitch):
            chunks.append(chunk)
        mp3_bytes = b"".join(chunks)
        if fmt == "wav":
            return mp3_bytes_to_wav_bytes(mp3_bytes)
        return mp3_bytes

    async def synthesize_stream(self, text: str, voice: str, speed: float, pitch: int) -> AsyncGenerator[bytes, None]:
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=self._speed_to_rate(speed),
            pitch=self._pitch_to_value(pitch),
        )
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]
