import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import AsyncGenerator

from app.core.config import DEVICE, VOICES
from app.engines.edge_engine import EdgeTTSEngine
from app.engines.kokoro_engine import KokoroEngine
from app.utils.audio import numpy_to_mp3_bytes, numpy_to_mp3_chunk, numpy_to_wav_bytes

logger = logging.getLogger(__name__)
ROOT_DIR = Path(__file__).resolve().parents[2]

# Executor global para tarefas intensivas de CPU (Kokoro)
_executor = ThreadPoolExecutor(max_workers=4)


class TTSService:
    """Serviço central que roteia requisições entre as engines Kokoro e Edge TTS."""

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
            raise ValueError(f"Voz '{voice}' não encontrada no catálogo.")
        return voice_config

    def load_model(self):
        """Carrega o modelo Kokoro na memória/GPU."""
        self._kokoro_engine.load()

    @property
    def model_loaded(self) -> bool:
        return self._kokoro_engine.is_loaded

    @property
    def device(self) -> str:
        return DEVICE

    def get_voices(self) -> list[dict]:
        voices = []
        for voice in self._kokoro_engine.get_voices():
            available, availability_error = self.get_voice_availability(voice["id"])
            voices.append({
                **voice,
                "available": available,
                "availability_error": availability_error,
            })
        return voices

    def get_languages(self) -> list[dict]:
        return self._kokoro_engine.get_languages()

    def validate_voice(self, voice: str) -> bool:
        return voice in VOICES

    def language_supported_for_voice(self, voice: str) -> bool:
        return self._kokoro_engine.language_supported_for_voice(voice)

    def get_voice_availability(self, voice: str) -> tuple[bool, str | None]:
        voice_config = self._get_voice_config(voice)
        if voice_config.get("engine") != "kokoro":
            return True, None

        source = voice_config.get("source")
        if not source:
            return False, "Voz Kokoro sem arquivo de origem configurado."

        source_path = Path(source)
        if source_path.suffix.lower() != ".pt":
            return True, None

        resolved_path = source_path if source_path.is_absolute() else ROOT_DIR / source_path
        if resolved_path.is_file():
            return True, None

        return False, f"Arquivo de voz ausente: {source}"

    def _resolve_params(self, voice_config: dict, speed: float, pitch: int) -> tuple[float, int]:
        """Resolve speed e pitch usando defaults da voz se os fornecidos forem neutros (1.0 e 0)."""
        final_speed = speed if abs(speed - 1.0) > 1e-9 else float(voice_config.get("default_speed", 1.0))
        final_pitch = pitch if pitch != 0 else int(voice_config.get("default_pitch", 0))
        return final_speed, final_pitch

    async def generate(self, text: str, voice: str, speed: float, pitch: int, fmt: str) -> bytes:
        """Gera áudio completo (WAV ou MP3) de forma assíncrona."""
        voice_config = self._get_voice_config(voice)
        engine_name = voice_config.get("engine", "kokoro")
        speed, pitch = self._resolve_params(voice_config, speed, pitch)

        if engine_name == "edge":
            return await self._edge_engine.synthesize(text, voice_config["source"], speed, pitch, fmt)

        # Kokoro synthesis (CPU/GPU bound) executada em thread separada
        loop = asyncio.get_running_loop()
        audio = await loop.run_in_executor(_executor, self._kokoro_engine.synthesize, text, voice, speed)

        if fmt == "wav":
            return numpy_to_wav_bytes(audio)
        return numpy_to_mp3_bytes(audio)

    async def generate_stream(self, text: str, voice: str, speed: float, pitch: int) -> AsyncGenerator[bytes, None]:
        """Gera stream de áudio em chunks MP3."""
        voice_config = self._get_voice_config(voice)
        engine_name = voice_config.get("engine", "kokoro")
        speed, pitch = self._resolve_params(voice_config, speed, pitch)

        if engine_name == "edge":
            async for chunk in self._edge_engine.synthesize_stream(text, voice_config["source"], speed, pitch):
                yield chunk
            return

        # Para Kokoro, consumimos o gerador síncrono chunk a chunk via executor
        loop = asyncio.get_running_loop()
        generator = self._kokoro_engine.synthesize_chunk_generator(text, voice, speed)

        while True:
            try:
                chunk = await loop.run_in_executor(_executor, next, generator)
                yield numpy_to_mp3_chunk(chunk)
            except StopIteration:
                break
            except Exception as e:
                logger.error(f"Erro no streaming Kokoro: {e}")
                break


# Instância única global
tts_service = TTSService()
