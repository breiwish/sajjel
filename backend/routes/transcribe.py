from database import RECORDINGS_DIR, get_db
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from models import Lecture, Transcript
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/lectures", tags=["transcription"])

# Lazy-loaded transcriber
_transcriber = None


def get_transcriber():
    global _transcriber
    if _transcriber is None:
        from transcriber import Transcriber

        _transcriber = Transcriber()
    return _transcriber


def _run_transcription(lecture_id: int, audio_path: str, diarize: bool):
    from database import SessionLocal

    db = SessionLocal()
    try:
        transcriber = get_transcriber()
        result = transcriber.transcribe(str(RECORDINGS_DIR / audio_path), diarize=diarize)

        # Remove old transcript if exists
        db.query(Transcript).filter(Transcript.lecture_id == lecture_id).delete()

        transcript = Transcript(
            lecture_id=lecture_id,
            content=result["text"],
            segments=result["segments"],
            diarize=diarize,
        )
        db.add(transcript)
        db.query(Lecture).filter(Lecture.id == lecture_id).update({"status": "transcribed"})
        db.commit()
    except Exception as e:
        db.query(Lecture).filter(Lecture.id == lecture_id).update({"status": "recorded"})
        db.commit()
        raise e
    finally:
        db.close()


@router.post("/{lecture_id}/transcribe")
def transcribe_lecture(
    lecture_id: int,
    diarize: bool = False,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
):
    lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()
    if not lecture:
        raise HTTPException(404, "Lecture not found")
    if not lecture.audio_path:
        raise HTTPException(400, "No audio file")
    if lecture.status == "transcribing":
        raise HTTPException(409, "Already transcribing")

    lecture.status = "transcribing"
    db.commit()

    background_tasks.add_task(_run_transcription, lecture_id, lecture.audio_path, diarize)
    return {"status": "transcribing"}


@router.get("/{lecture_id}/transcript")
def get_transcript(lecture_id: int, db: Session = Depends(get_db)):
    lecture = db.query(Lecture).filter(Lecture.id == lecture_id).first()
    if not lecture:
        raise HTTPException(404, "Lecture not found")

    transcript = db.query(Transcript).filter(Transcript.lecture_id == lecture_id).first()
    return {
        "status": lecture.status,
        "transcript": {
            "id": transcript.id,
            "content": transcript.content,
            "segments": transcript.segments,
            "diarize": transcript.diarize,
        }
        if transcript
        else None,
    }
