from fastapi import APIRouter, HTTPException

from schemas import ExtractUrlRequest, ExtractTextRequest, ExtractedFields
from services.scraper import fetch_and_clean
from services.extractor import extract_fields

router = APIRouter(prefix="/api/extract", tags=["extract"])


@router.post("/url", response_model=ExtractedFields)
def extract_from_url(payload: ExtractUrlRequest):
    try:
        text = fetch_and_clean(payload.url)
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Could not fetch URL: {exc}. Try pasting the job spec instead.",
        )
    try:
        return extract_fields(text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {exc}")


@router.post("/text", response_model=ExtractedFields)
def extract_from_text(payload: ExtractTextRequest):
    if not payload.text.strip():
        raise HTTPException(status_code=422, detail="Text must not be empty")
    try:
        return extract_fields(payload.text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {exc}")
