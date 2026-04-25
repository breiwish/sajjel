import json
import shutil
from pathlib import Path

from database import RECORDINGS_DIR, get_db
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from models import Lecture, Tag
from sqlalchemy.orm import Session, joinedload

router = APIRouter(prefix="/api/lectures", tags=["lectures"])


@router.post("")
async def create_lecture(
    audio: UploadFile = File(...),
    title: str = Form("Untitled Lecture"),
    notes: str = Form(""),
    tags_json: str = Form("[]"),
    duration: float = Form(0),
    db: Session = Depends(get_db),
):
    lecture = Lecture(title=title, notes=notes, duration=duration)
    db.add(lecture)
    db.flush()

    # Save audio file
    ext = Path(audio.filename).suffix or ".wav"
    audio_filename = f"lecture_{lecture.id}{ext}"
    audio_path = RECORDINGS_DIR / audio_filename
    with open(audio_path, "wb") as f:
        shutil.copyfileobj(audio.file, f)
    lecture.audio_path = audio_filename

    # Save tags
    for t in json.loads(tags_json):
        db.add(
            Tag(
                lecture_id=lecture.id,
                name=t["name"],
                time=t["time"],
                char_index=t.get("charIndex"),
            )
        )

    db.commit()
    db.refresh(lecture)
    return _lecture_dict(lecture)


@router.get("")
def list_lectures(db: Session = Depends(get_db)):
    lectures = db.query(Lecture).order_by(Lecture.date.desc()).all()
    return [_lecture_summary(l) for l in lectures]


@router.get("/{lecture_id}")
def get_lecture(lecture_id: int, db: Session = Depends(get_db)):
    lecture = (
        db.query(Lecture)
        .options(joinedload(Lecture.tags), joinedload(Lecture.transcript))
        .filter(Lecture.id == lecture_id)
        .first()
    )
    if not lecture:
        raise HTTPException(404, "Lecture not found")
    return _lecture_dict(lecture)


@router.delete("/{lecture_id}")
def delete_lecture(lecture_id: int, db: Session = Depends(get_db)):
    lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()
    if not lecture:
        raise HTTPException(404, "Lecture not found")
    # Delete audio file
    if lecture.audio_path:
        audio_path = RECORDINGS_DIR / lecture.audio_path
        audio_path.unlink(missing_ok=True)
    db.delete(lecture)
    db.commit()
    return {"ok": True}


def _lecture_summary(l: Lecture) -> dict:
    return {
        "id": l.id,
        "title": l.title,
        "date": l.date.isoformat() if l.date else None,
        "duration": l.duration,
        "status": l.status,
    }


def _lecture_dict(l: Lecture) -> dict:
    return {
        **_lecture_summary(l),
        "notes": l.notes,
        "audio_path": l.audio_path,
        "tags": [
            {"id": t.id, "name": t.name, "time": t.time, "charIndex": t.char_index}
            for t in (l.tags or [])
        ],
        "transcript": {
            "id": l.transcript.id,
            "content": l.transcript.content,
            "segments": l.transcript.segments,
            "diarize": l.transcript.diarize,
        }
        if l.transcript
        else None,
    }
