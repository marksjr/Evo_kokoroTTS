import logging
import numpy as np
import torch
from kokoro import KPipeline

from app.core.config import DEFAULT_LANG_CODE, DEVICE, LANGUAGES, VOICES
from app.utils.audio import crossfade_chunks, normalize_audio, trim_silence
from app.utils.text import chunk_text, preprocess_text

logger = logging.getLogger(__name__)


class KokoroEngine:
    """Kokoro-82M engine with language-managed pipelines."""

    def __init__(self):
        self._pipelines = {}
        self._loaded = False

    def _get_voice_config(self, voice: str) -> dict:
        voice_config = VOICES.get(voice)
        if not voice_config:
            raise ValueError(f"Voice '{voice}' not found.")
        return voice_config

    def _load_pipeline(self, lang_code: str) -> KPipeline:
        if lang_code in self._pipelines:
            return self._pipelines[lang_code]

        logger.info(f"[Kokoro] Loading pipeline for language '{lang_code}' on device {DEVICE}...")
        try:
            pipeline = KPipeline(lang_code=lang_code, device=DEVICE)
            self._pipelines[lang_code] = pipeline
            self._loaded = True
            return pipeline
        except Exception as e:
            logger.error(f"[Kokoro] Error loading pipeline {lang_code}: {e}")
            raise

    def load(self) -> None:
        """Loads the default pipeline defined in the configuration."""
        self._load_pipeline(DEFAULT_LANG_CODE)
        logger.info(f"[Kokoro] Engine initialized successfully ({DEVICE})")

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
        """Synthesizes a single text chunk."""
        voice_config = self._get_voice_config(voice)
        pipeline = self._load_pipeline(voice_config["lang_code"])
        voice_source = voice_config.get("source", voice)

        parts = []
        # The Kokoro pipeline already performs an internal split by newline if requested
        for _, _, audio in pipeline(text_chunk, voice=voice_source, speed=speed, split_pattern=r"\n+"):
            if audio is not None:
                parts.append(audio)
        return parts

    def _prepare_text(self, text: str, voice: str) -> list[str]:
        voice_config = self._get_voice_config(voice)
        text = preprocess_text(text, voice_config["lang"])
        return chunk_text(text)

    def synthesize(self, text: str, voice: str, speed: float) -> np.ndarray:
        """Synthesizes the full text by concatenating chunks with crossfade."""
        chunks = self._prepare_text(text, voice)
        logger.debug(f"[Kokoro] Synthesizing {len(chunks)} chunks for voice {voice}")

        audio_segments = []
        for chunk in chunks:
            parts = self._synth_chunk(chunk, voice, speed)
            if parts:
                audio_segments.append(np.concatenate(parts))

        if not audio_segments:
            raise RuntimeError(f"The Kokoro engine did not generate audio for the provided text.")

        audio = crossfade_chunks(audio_segments)
        audio = trim_silence(audio)
        return normalize_audio(audio)

    def synthesize_chunk_generator(self, text: str, voice: str, speed: float):
        """Generator for streaming audio chunk by chunk."""
        chunks = self._prepare_text(text, voice)

        for chunk in chunks:
            parts = self._synth_chunk(chunk, voice, speed)
            if parts:
                segment = np.concatenate(parts)
                yield normalize_audio(segment)
