from typing import Literal

from pydantic import BaseModel, Field


class TTSRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Text to synthesize.",
        examples=["Hello! This is a child voice synthesis test in Portuguese."],
    )
    voice: str = Field(
        default="pf_dora",
        description="Voice ID. Use GET /voices to list all options.",
        examples=["pt_f_menina"],
    )
    speed: float = Field(
        default=1.0,
        ge=0.5,
        le=2.0,
        description="Speech speed. For Edge voices, 1.0 uses the voice's default preset when available.",
        examples=[1.0],
    )
    pitch: int = Field(
        default=0,
        ge=-80,
        le=80,
        description="Pitch adjustment in Hz. For Edge voices, 0 uses the voice's default preset when available.",
        examples=[46],
    )
    format: Literal["mp3", "wav"] = Field(
        default="mp3",
        description="Output format.",
        examples=["mp3"],
    )


class TTSStreamRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Text to synthesize via streaming.",
        examples=["Long text for progressive real-time playback."],
    )
    voice: str = Field(
        default="pf_dora",
        description="Voice ID. Use GET /voices to list all options.",
        examples=["pt_m_menino"],
    )
    speed: float = Field(
        default=1.0,
        ge=0.5,
        le=2.0,
        description="Speech speed. For Edge voices, 1.0 uses the voice's default preset when available.",
        examples=[1.05],
    )
    pitch: int = Field(
        default=0,
        ge=-80,
        le=80,
        description="Pitch adjustment in Hz. For Edge voices, 0 uses the voice's default preset when available.",
        examples=[28],
    )


class HealthResponse(BaseModel):
    status: str = Field(description="API status: ok or loading.")
    device: str = Field(description="Current inference device: cuda or cpu.")
    model_loaded: bool = Field(description="Indicates whether the default Kokoro pipeline has been loaded.")


class LanguageInfo(BaseModel):
    id: str = Field(description="Normalized language ID.")
    name: str = Field(description="Native language name.")
    label: str = Field(description="User-friendly label for UI.")
    kokoro_code: str | None = Field(default=None, description="Language code used by Kokoro, when applicable.")
    supported: bool = Field(description="Indicates whether the language is available in this installation.")
    sample_text: str = Field(description="Sample text for quick testing.")


class VoiceInfo(BaseModel):
    id: str = Field(description="Voice ID.")
    name: str = Field(description="Short name displayed in UI.")
    gender: str = Field(description="Voice gender.")
    lang: str = Field(description="Voice language.")
    lang_code: str | None = Field(default=None, description="Language code used by Kokoro, when applicable.")
    engine: str = Field(description="Engine responsible for synthesis: kokoro or edge.")
    default_speed: float | None = Field(default=None, description="Suggested speed preset for the voice.")
    default_pitch: int | None = Field(default=None, description="Suggested pitch preset in Hz for the voice.")
    available: bool = Field(default=True, description="Indicates whether the voice is ready for local use.")
    availability_error: str | None = Field(default=None, description="Reason for local unavailability, when applicable.")
    description: str = Field(description="Short voice description.")
