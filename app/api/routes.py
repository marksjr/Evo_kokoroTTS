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
    summary="Check API status",
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
    summary="List available languages",
)
async def list_languages():
    return [LanguageInfo(**lang) for lang in tts_service.get_languages()]


@router.get(
    "/voices",
    response_model=list[VoiceInfo],
    summary="List available voices",
)
async def list_voices():
    return [VoiceInfo(**voice) for voice in tts_service.get_voices()]


def _validate_request(voice: str) -> None:
    if not tts_service.validate_voice(voice):
        raise HTTPException(
            status_code=404,
            detail=f"Voice '{voice}' not found. See /voices for the full list.",
        )
    if not tts_service.language_supported_for_voice(voice):
        raise HTTPException(
            status_code=400,
            detail=f"The language of voice '{voice}' is not supported by the current Kokoro installation.",
        )

    available, availability_error = tts_service.get_voice_availability(voice)
    if not available:
        raise HTTPException(
            status_code=400,
            detail=availability_error or f"Voice '{voice}' is not ready for use.",
        )


@router.post(
    "/tts",
    summary="Generate complete audio",
    responses={
        200: {"description": "Audio generated successfully."},
        400: {"description": "Request error or voice unavailable."},
        404: {"description": "Voice not found."},
        500: {"description": "Internal processing error."},
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
        logger.exception("Unexpected error during audio generation (voice: %s)", req.voice)
        raise HTTPException(status_code=500, detail="Internal error while synthesizing audio.")

    media_type = "audio/mpeg" if req.format == "mp3" else "audio/wav"
    return Response(
        content=audio_bytes,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="tts.{req.format}"'},
    )


@router.post(
    "/tts/stream",
    summary="Generate audio via streaming",
    responses={
        200: {"description": "Audio stream started."},
        400: {"description": "Request error."},
        404: {"description": "Voice not found."},
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
            logger.error("Error during audio streaming: %s", exc)

    return StreamingResponse(
        audio_generator(),
        media_type="audio/mpeg",
        headers={"Content-Disposition": 'attachment; filename="tts_stream.mp3"'},
    )
