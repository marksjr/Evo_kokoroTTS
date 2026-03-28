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
    summary="Listar idiomas disponiveis",
)
async def list_languages():
    return [LanguageInfo(**lang) for lang in tts_service.get_languages()]


@router.get(
    "/voices",
    response_model=list[VoiceInfo],
    summary="Listar vozes disponiveis",
)
async def list_voices():
    return [VoiceInfo(**voice) for voice in tts_service.get_voices()]


def _validate_request(voice: str) -> None:
    if not tts_service.validate_voice(voice):
        raise HTTPException(
            status_code=404,
            detail=f"Voz '{voice}' nao encontrada. Consulte /voices para a lista completa.",
        )
    if not tts_service.language_supported_for_voice(voice):
        raise HTTPException(
            status_code=400,
            detail=f"O idioma da voz '{voice}' nao e suportado pela instalacao atual do Kokoro.",
        )

    available, availability_error = tts_service.get_voice_availability(voice)
    if not available:
        raise HTTPException(
            status_code=400,
            detail=availability_error or f"A voz '{voice}' nao esta pronta para uso.",
        )


@router.post(
    "/tts",
    summary="Gerar audio completo",
    responses={
        200: {"description": "Audio gerado com sucesso."},
        400: {"description": "Erro na requisicao ou voz indisponivel."},
        404: {"description": "Voz nao encontrada."},
        500: {"description": "Erro interno no processamento."},
    },
)
async def text_to_speech(req: TTSRequest):
    _validate_request(req.voice)

    try:
        audio_bytes = await tts_service.generate(
            text=req.text,
            voice=req.voice,
            speed=req.speed,
            pitch=req.pitch,
            fmt=req.format,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception:
        logger.exception("Erro inesperado na geracao de audio (voz: %s)", req.voice)
        raise HTTPException(status_code=500, detail="Erro interno ao sintetizar o audio.")

    media_type = "audio/mpeg" if req.format == "mp3" else "audio/wav"
    return Response(
        content=audio_bytes,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="tts.{req.format}"'},
    )


@router.post(
    "/tts/stream",
    summary="Gerar audio por streaming",
    responses={
        200: {"description": "Stream de audio iniciado."},
        400: {"description": "Erro na requisicao."},
        404: {"description": "Voz nao encontrada."},
    },
)
async def text_to_speech_stream(req: TTSStreamRequest):
    _validate_request(req.voice)

    async def audio_generator():
        try:
            async for chunk in tts_service.generate_stream(
                text=req.text,
                voice=req.voice,
                speed=req.speed,
                pitch=req.pitch,
            ):
                yield chunk
        except Exception as exc:
            logger.error("Erro durante o streaming de audio: %s", exc)

    return StreamingResponse(
        audio_generator(),
        media_type="audio/mpeg",
        headers={"Content-Disposition": 'attachment; filename="tts_stream.mp3"'},
    )
