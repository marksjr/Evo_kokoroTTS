from typing import Literal

from pydantic import BaseModel, Field


class TTSRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Texto para sintetizar.",
        examples=["Ola! Este e um teste de sintese de voz infantil em portugues."],
    )
    voice: str = Field(
        default="pf_dora",
        description="ID da voz. Use GET /voices para listar todas as opcoes.",
        examples=["pt_f_menina"],
    )
    speed: float = Field(
        default=1.0,
        ge=0.5,
        le=2.0,
        description="Velocidade da fala. Para vozes Edge, 1.0 usa o preset default da voz quando existir.",
        examples=[1.0],
    )
    pitch: int = Field(
        default=0,
        ge=-80,
        le=80,
        description="Ajuste de pitch em Hz. Para vozes Edge, 0 usa o preset default da voz quando existir.",
        examples=[46],
    )
    format: Literal["mp3", "wav"] = Field(
        default="mp3",
        description="Formato de saida.",
        examples=["mp3"],
    )


class TTSStreamRequest(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Texto para sintetizar em streaming.",
        examples=["Texto longo para playback progressivo em tempo real."],
    )
    voice: str = Field(
        default="pf_dora",
        description="ID da voz. Use GET /voices para listar todas as opcoes.",
        examples=["pt_m_menino"],
    )
    speed: float = Field(
        default=1.0,
        ge=0.5,
        le=2.0,
        description="Velocidade da fala. Para vozes Edge, 1.0 usa o preset default da voz quando existir.",
        examples=[1.05],
    )
    pitch: int = Field(
        default=0,
        ge=-80,
        le=80,
        description="Ajuste de pitch em Hz. Para vozes Edge, 0 usa o preset default da voz quando existir.",
        examples=[28],
    )


class HealthResponse(BaseModel):
    status: str = Field(description="Estado da API: ok ou loading.")
    device: str = Field(description="Dispositivo atual de inferencia: cuda ou cpu.")
    model_loaded: bool = Field(description="Indica se o pipeline padrao do Kokoro ja foi carregado.")


class LanguageInfo(BaseModel):
    id: str = Field(description="ID normalizado do idioma.")
    name: str = Field(description="Nome nativo do idioma.")
    label: str = Field(description="Rotulo amigavel para UI.")
    kokoro_code: str | None = Field(default=None, description="Codigo de idioma usado pelo Kokoro, quando aplicavel.")
    supported: bool = Field(description="Indica se o idioma esta disponivel nesta instalacao.")
    sample_text: str = Field(description="Texto de exemplo para teste rapido.")


class VoiceInfo(BaseModel):
    id: str = Field(description="ID da voz.")
    name: str = Field(description="Nome curto exibido na UI.")
    gender: str = Field(description="Genero da voz.")
    lang: str = Field(description="Idioma da voz.")
    lang_code: str | None = Field(default=None, description="Codigo de idioma usado pelo Kokoro, quando aplicavel.")
    engine: str = Field(description="Engine responsavel pela sintese: kokoro ou edge.")
    default_speed: float | None = Field(default=None, description="Preset sugerido de velocidade para a voz.")
    default_pitch: int | None = Field(default=None, description="Preset sugerido de pitch em Hz para a voz.")
    available: bool = Field(default=True, description="Indica se a voz esta pronta para uso local.")
    availability_error: str | None = Field(default=None, description="Motivo da indisponibilidade local, quando houver.")
    description: str = Field(description="Descricao curta da voz.")
