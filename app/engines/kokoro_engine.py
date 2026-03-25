import logging

import numpy as np
import torch

from app.core.config import DEFAULT_LANG_CODE, DEFAULT_VOICE, DEVICE, LANGUAGES, VOICES
from app.utils.audio import crossfade_chunks, normalize_audio, trim_silence
from app.utils.text import chunk_text, preprocess_text

logger = logging.getLogger(__name__)


class KokoroEngine:
    """Engine Kokoro-82M com pipelines por idioma."""

    def __init__(self):
        self._pipelines = {}
        self._loaded = False

    def _get_voice_config(self, voice: str) -> dict:
        voice_config = VOICES.get(voice)
        if not voice_config:
            raise ValueError(f"Voz '{voice}' não disponível.")
        return voice_config

    def _load_pipeline(self, lang_code: str):
        if lang_code in self._pipelines:
            return self._pipelines[lang_code]

        from kokoro import KPipeline

        logger.info(f"[Kokoro] Carregando pipeline (lang={lang_code}, device={DEVICE})")
        pipeline = KPipeline(lang_code=lang_code, device=DEVICE)
        self._pipelines[lang_code] = pipeline
        self._loaded = True
        return pipeline

    def load(self) -> None:
        if DEFAULT_LANG_CODE in self._pipelines:
            return
        self._load_pipeline(DEFAULT_LANG_CODE)
        logger.info("[Kokoro] Pipeline padrão carregado com sucesso")

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def get_voices(self) -> list[dict]:
        return list(VOICES.values())

    def get_languages(self) -> list[dict]:
        return list(LANGUAGES.values())

    def get_default_voice(self) -> str:
        return DEFAULT_VOICE

    def validate_voice(self, voice: str) -> bool:
        return voice in VOICES

    def language_supported_for_voice(self, voice: str) -> bool:
        voice_config = self._get_voice_config(voice)
        return LANGUAGES[voice_config["lang"]]["supported"]

    @torch.inference_mode()
    def _synth_chunk(self, text_chunk: str, voice: str, speed: float) -> list[np.ndarray]:
        voice_config = self._get_voice_config(voice)
        pipeline = self._load_pipeline(voice_config["lang_code"])
        voice_source = voice_config.get("source", voice)

        parts = []
        for gs, ps, audio in pipeline(text_chunk, voice=voice_source, speed=speed, split_pattern=r"\n+"):
            if audio is not None:
                parts.append(audio)
        return parts

    def _prepare_text(self, text: str, voice: str) -> list[str]:
        voice_config = self._get_voice_config(voice)
        text = preprocess_text(text, voice_config["lang"])
        return chunk_text(text)

    def synthesize(self, text: str, voice: str, speed: float) -> np.ndarray:
        chunks = self._prepare_text(text, voice)
        logger.debug(f"[Kokoro] Texto dividido em {len(chunks)} chunks")

        audio_segments = []
        for chunk in chunks:
            parts = self._synth_chunk(chunk, voice, speed)
            if parts:
                audio_segments.append(np.concatenate(parts))

        if not audio_segments:
            raise RuntimeError("Nenhum áudio gerado")

        audio = crossfade_chunks(audio_segments)
        audio = trim_silence(audio)
        audio = normalize_audio(audio)
        return audio

    def synthesize_chunks(self, text: str, voice: str, speed: float) -> list[np.ndarray]:
        chunks = self._prepare_text(text, voice)
        result = []

        for chunk in chunks:
            parts = self._synth_chunk(chunk, voice, speed)
            if parts:
                segment = np.concatenate(parts)
                segment = normalize_audio(segment)
                result.append(segment)

        return result

    def synthesize_chunk_generator(self, text: str, voice: str, speed: float):
        """Gera chunks de áudio um a um."""
        chunks = self._prepare_text(text, voice)

        for chunk in chunks:
            parts = self._synth_chunk(chunk, voice, speed)
            if parts:
                segment = np.concatenate(parts)
                segment = normalize_audio(segment)
                yield segment
