from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.schemas.speech import (
    SpeechSynthesisRequest,
    SpeechSynthesisResponse,
    SpeechTranscriptionResponse,
)
from app.services.speech_service import SpeechServiceError, synthesize_text, transcribe_audio


router = APIRouter(prefix="/api/speech", tags=["speech"])


@router.post("/transcribe", response_model=SpeechTranscriptionResponse)
async def transcribe_speech(
    file: UploadFile = File(...),
    language: str = Form(...),
) -> SpeechTranscriptionResponse:
    audio_bytes = await file.read()
    try:
        return await transcribe_audio(audio_bytes, file.content_type or "", language)
    except SpeechServiceError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@router.post("/synthesize", response_model=SpeechSynthesisResponse)
async def synthesize_speech(payload: SpeechSynthesisRequest) -> SpeechSynthesisResponse:
    try:
        return await synthesize_text(payload.text, payload.language)
    except SpeechServiceError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
