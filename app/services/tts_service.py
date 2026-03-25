import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import AsyncGenerator

from app.core.config import DEVICE, VOICES
from app.engines.edge_engine import EdgeTTSEngine
from app.engines.kokoro_engine import KokoroEngine
from app.utils.audio import numpy_to_mp3_chunk

logger = logging.getLogger(__name__)

_executor = ThreadPoolExecutor(max_workers=4)


class TTSService:
    """Serviço central que roteia por engine de voz."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._kokoro_engine = KokoroEngine()
        self._edge_engine = EdgeTTSEngine()
        self._initialized = True

    def _get_voice_config(self, voice: str) -> dict:
        voice_config = VOICES.get(voice)
        if not voice_config:
            raise ValueError(f"Voz '{voice}' não disponível.")
        return voice_config

    def load_model(self):
        self._kokoro_engine.load()

    @property
    def model_loaded(self) -> bool:
        return self._kokoro_engine.is_loaded

    @property
    def device(self) -> str:
        return DEVICE

    def get_voices(self) -> list[dict]:
        return self._kokoro_engine.get_voices()

    def get_languages(self) -> list[dict]:
        return self._kokoro_engine.get_languages()

    def get_default_voice(self) -> str:
        return self._kokoro_engine.get_default_voice()

    def validate_voice(self, voice: str) -> bool:
        return voice in VOICES

    def language_supported_for_voice(self, voice: str) -> bool:
        return self._kokoro_engine.language_supported_for_voice(voice)

    def _resolve_pitch(self, voice_config: dict, pitch: int) -> int:
        if pitch != 0:
            return pitch
        return int(voice_config.get("default_pitch", 0) or 0)

    def _resolve_speed(self, voice_config: dict, speed: float) -> float:
        if abs(speed - 1.0) > 1e-9:
            return speed
        return float(voice_config.get("default_speed", 1.0) or 1.0)

    async def generate(self, text: str, voice: str, speed: float, pitch: int, fmt: str) -> bytes:
        voice_config = self._get_voice_config(voice)
        engine_name = voice_config.get("engine", "kokoro")

        if engine_name == "edge":
            return await self._edge_engine.synthesize(
                text,
                voice_config["source"],
                self._resolve_speed(voice_config, speed),
                self._resolve_pitch(voice_config, pitch),
                fmt,
            )

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_executor, self._generate_kokoro_bytes, text, voice, speed, fmt)

    def _generate_kokoro_bytes(self, text: str, voice: str, speed: float, fmt: str) -> bytes:
        from app.utils.audio import numpy_to_mp3_bytes, numpy_to_wav_bytes

        audio = self._kokoro_engine.synthesize(text, voice, speed)
        if fmt == "wav":
            return numpy_to_wav_bytes(audio)
        return numpy_to_mp3_bytes(audio)

    async def generate_stream(self, text: str, voice: str, speed: float, pitch: int) -> AsyncGenerator[bytes, None]:
        voice_config = self._get_voice_config(voice)
        engine_name = voice_config.get("engine", "kokoro")

        if engine_name == "edge":
            async for chunk in self._edge_engine.synthesize_stream(
                text,
                voice_config["source"],
                self._resolve_speed(voice_config, speed),
                self._resolve_pitch(voice_config, pitch),
            ):
                yield chunk
            return

        loop = asyncio.get_event_loop()
        generator = self._kokoro_engine.synthesize_chunk_generator(text, voice, speed)
        while True:
            chunk = await loop.run_in_executor(_executor, lambda: next(generator, None))
            if chunk is None:
                break
            yield numpy_to_mp3_chunk(chunk)


tts_service = TTSService()
