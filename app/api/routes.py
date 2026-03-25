import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response, StreamingResponse

from app.models.schemas import HealthResponse, LanguageInfo, TTSRequest, TTSStreamRequest, VoiceInfo
from app.services.tts_service import tts_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Verificar status da API",
    description="Retorna o status atual da API, o dispositivo em uso e se o pipeline padrão do Kokoro já foi carregado.",
)
async def health():
    return HealthResponse(
        status="ok" if tts_service.model_loaded else "loading",
        device=tts_service.device,
        model_loaded=tts_service.model_loaded,
    )


@router.get(
    "/languages",
    response_model=list[LanguageInfo],
    summary="Listar idiomas disponíveis",
    description="Retorna todos os idiomas disponíveis na instalação atual, incluindo idiomas atendidos por Kokoro e Edge TTS.",
)
async def list_languages():
    return [LanguageInfo(**lang) for lang in tts_service.get_languages()]


@router.get(
    "/voices",
    response_model=list[VoiceInfo],
    summary="Listar vozes disponíveis",
    description="Retorna o catálogo completo de vozes, incluindo engine, idioma e presets sugeridos de speed e pitch.",
)
async def list_voices():
    return [VoiceInfo(**voice) for voice in tts_service.get_voices()]


def _validate_voice_or_raise(voice: str) -> None:
    if not tts_service.validate_voice(voice):
        raise HTTPException(400, f"Voz '{voice}' não disponível. Use GET /voices.")
    if not tts_service.language_supported_for_voice(voice):
        raise HTTPException(400, "Idioma selecionado não é suportado pela versão instalada do Kokoro.")


@router.post(
    "/tts",
    summary="Gerar áudio completo",
    description="Sintetiza o texto inteiro e retorna um arquivo MP3 ou WAV. Para vozes Edge, speed=1.0 e pitch=0 aplicam os presets default da voz quando definidos.",
    responses={
        200: {"description": "Áudio gerado com sucesso."},
        400: {"description": "Parâmetros inválidos ou voz indisponível."},
        500: {"description": "Falha interna durante a geração."},
    },
)
async def text_to_speech(req: TTSRequest):
    _validate_voice_or_raise(req.voice)

    try:
        audio_bytes = await tts_service.generate(
            text=req.text,
            voice=req.voice,
            speed=req.speed,
            pitch=req.pitch,
            fmt=req.format,
        )
    except Exception as e:
        logger.exception("Erro na geração de áudio")
        raise HTTPException(500, f"Erro na geração: {str(e)}")

    media_type = "audio/mpeg" if req.format == "mp3" else "audio/wav"
    return Response(
        content=audio_bytes,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="tts.{req.format}"'},
    )


@router.post(
    "/tts/stream",
    summary="Gerar áudio por streaming",
    description="Sintetiza e retorna o áudio em fluxo MP3. Para vozes Edge, speed=1.0 e pitch=0 aplicam os presets default da voz quando definidos.",
    responses={
        200: {"description": "Stream de áudio iniciado com sucesso."},
        400: {"description": "Parâmetros inválidos ou voz indisponível."},
        500: {"description": "Falha interna durante a geração."},
    },
)
async def text_to_speech_stream(req: TTSStreamRequest):
    _validate_voice_or_raise(req.voice)

    async def audio_generator():
        async for chunk in tts_service.generate_stream(
            text=req.text,
            voice=req.voice,
            speed=req.speed,
            pitch=req.pitch,
        ):
            yield chunk

    return StreamingResponse(
        audio_generator(),
        media_type="audio/mpeg",
        headers={"Content-Disposition": 'attachment; filename="tts_stream.mp3"'},
    )
