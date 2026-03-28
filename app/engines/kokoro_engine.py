import logging
import numpy as np
import torch
from kokoro import KPipeline

from app.core.config import DEFAULT_LANG_CODE, DEVICE, LANGUAGES, VOICES
from app.utils.audio import crossfade_chunks, normalize_audio, trim_silence
from app.utils.text import chunk_text, preprocess_text

logger = logging.getLogger(__name__)


class KokoroEngine:
    """Engine Kokoro-82M com pipelines gerenciados por idioma."""

    def __init__(self):
        self._pipelines = {}
        self._loaded = False

    def _get_voice_config(self, voice: str) -> dict:
        voice_config = VOICES.get(voice)
        if not voice_config:
            raise ValueError(f"Voz '{voice}' não encontrada.")
        return voice_config

    def _load_pipeline(self, lang_code: str) -> KPipeline:
        if lang_code in self._pipelines:
            return self._pipelines[lang_code]

        logger.info(f"[Kokoro] Carregando pipeline para idioma '{lang_code}' no dispositivo {DEVICE}...")
        try:
            pipeline = KPipeline(lang_code=lang_code, device=DEVICE)
            self._pipelines[lang_code] = pipeline
            self._loaded = True
            return pipeline
        except Exception as e:
            logger.error(f"[Kokoro] Erro ao carregar pipeline {lang_code}: {e}")
            raise

    def load(self) -> None:
        """Carrega o pipeline padrão definido nas configurações."""
        self._load_pipeline(DEFAULT_LANG_CODE)
        logger.info(f"[Kokoro] Engine inicializada com sucesso ({DEVICE})")

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def get_voices(self) -> list[dict]:
        return list(VOICES.values())

    def get_languages(self) -> list[dict]:
        return list(LANGUAGES.values())

    def language_supported_for_voice(self, voice: str) -> bool:
        voice_config = self._get_voice_config(voice)
        lang_id = voice_config.get("lang")
        return LANGUAGES.get(lang_id, {}).get("supported", False)

    @torch.inference_mode()
    def _synth_chunk(self, text_chunk: str, voice: str, speed: float) -> list[np.ndarray]:
        """Sintetiza um único chunk de texto."""
        voice_config = self._get_voice_config(voice)
        pipeline = self._load_pipeline(voice_config["lang_code"])
        voice_source = voice_config.get("source", voice)

        parts = []
        # O pipeline Kokoro já faz uma divisão interna por nova linha se solicitado
        for _, _, audio in pipeline(text_chunk, voice=voice_source, speed=speed, split_pattern=r"\n+"):
            if audio is not None:
                parts.append(audio)
        return parts

    def _prepare_text(self, text: str, voice: str) -> list[str]:
        voice_config = self._get_voice_config(voice)
        text = preprocess_text(text, voice_config["lang"])
        return chunk_text(text)

    def synthesize(self, text: str, voice: str, speed: float) -> np.ndarray:
        """Sintetiza o texto completo concatenando chunks com crossfade."""
        chunks = self._prepare_text(text, voice)
        logger.debug(f"[Kokoro] Sintetizando {len(chunks)} chunks para a voz {voice}")

        audio_segments = []
        for chunk in chunks:
            parts = self._synth_chunk(chunk, voice, speed)
            if parts:
                audio_segments.append(np.concatenate(parts))

        if not audio_segments:
            raise RuntimeError(f"A engine Kokoro não gerou áudio para o texto fornecido.")

        audio = crossfade_chunks(audio_segments)
        audio = trim_silence(audio)
        return normalize_audio(audio)

    def synthesize_chunk_generator(self, text: str, voice: str, speed: float):
        """Gerador para streaming de áudio chunk por chunk."""
        chunks = self._prepare_text(text, voice)

        for chunk in chunks:
            parts = self._synth_chunk(chunk, voice, speed)
            if parts:
                segment = np.concatenate(parts)
                yield normalize_audio(segment)
