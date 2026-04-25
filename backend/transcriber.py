"""VibeVoice-ASR wrapper using mlx-audio for Apple Silicon inference."""

import os
import soundfile as sf
import numpy as np
import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Optional


@dataclass
class TranscribeResult:
    segments: list
    text: str
    chunk_idx: int


def _load_model_and_transcribe(args):
    """Load model and transcribe a chunk (for parallel execution)."""
    chunk_data, sr, chunk_start, chunk_idx, model_name, max_tokens = args
    
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
        sf.write(f.name, chunk_data, sr)
        temp_path = f.name
    
    try:
        from mlx_audio.stt import load_model
        model = load_model(model_name)
        result = model.generate(audio=temp_path, max_tokens=max_tokens)
        
        segments = []
        if hasattr(result, "segments") and result.segments:
            for seg in result.segments:
                if isinstance(seg, dict):
                    seg_dict = seg
                else:
                    seg_dict = {
                        "start": getattr(seg, "start", 0),
                        "end": getattr(seg, "end", 0),
                        "text": getattr(seg, "text", ""),
                    }
                segments.append({
                    "start": chunk_start + seg_dict.get("start", 0),
                    "end": chunk_start + seg_dict.get("end", 0),
                    "text": seg_dict.get("text", seg_dict.get("Content", "")),
                })
        
        return TranscribeResult(
            segments=segments,
            text=" ".join(s["text"] for s in segments),
            chunk_idx=chunk_idx
        )
    finally:
        os.unlink(temp_path)


class Transcriber:
    def __init__(self, model_name: str = "mlx-community/VibeVoice-ASR-4bit"):
        from mlx_audio.stt import load_model
        self.model = load_model(model_name)
        self.model_name = model_name
        self.chunk_duration = 30
        self.parallel = True
        self.max_workers = min(os.cpu_count() or 4, 4)

    def transcribe(self, audio_path: str, diarize: bool = False) -> dict:
        """Transcribe an audio file. Returns {text, segments}."""
        data, sr = sf.read(audio_path)
        
        total_duration = len(data) / sr
        
        if total_duration <= self.chunk_duration:
            return self._transcribe_single(audio_path, diarize)
        
        return self._transcribe_chunked(data, sr, diarize)

    def _transcribe_single(self, audio_path: str, diarize: bool) -> dict:
        result = self.model.generate(audio=audio_path, max_tokens=16384)

        segments = []
        full_text_parts = []

        if hasattr(result, "segments") and result.segments:
            for seg in result.segments:
                if isinstance(seg, dict):
                    seg_dict = seg
                else:
                    seg_dict = {
                        "start": getattr(seg, "start", 0),
                        "end": getattr(seg, "end", 0),
                        "text": getattr(seg, "text", ""),
                    }
                segment = {
                    "start": seg_dict.get("start", 0),
                    "end": seg_dict.get("end", 0),
                    "text": seg_dict.get("text", seg_dict.get("Content", "")),
                }
                if diarize:
                    speaker = seg_dict.get("speaker", seg_dict.get("speaker_id"))
                    if speaker is not None:
                        segment["speaker"] = speaker
                segments.append(segment)
                full_text_parts.append(segment["text"])
        elif hasattr(result, "text"):
            full_text_parts.append(result.text)

        return {
            "text": " ".join(full_text_parts).strip() if full_text_parts else str(result),
            "segments": segments,
        }

    def _transcribe_chunked(self, data: np.ndarray, sr: int, diarize: bool) -> dict:
        chunk_samples = int(self.chunk_duration * sr)
        num_chunks = (len(data) + chunk_samples - 1) // chunk_samples
        
        chunks = []
        for i in range(num_chunks):
            start = i * chunk_samples
            end = min(start + chunk_samples, len(data))
            chunk_data = data[start:end]
            chunk_start = start / sr
            chunks.append((chunk_data, sr, chunk_start, i, self.model_name, 8192))
        
        all_results = []
        
        if self.parallel and num_chunks > 1:
            with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [executor.submit(_load_model_and_transcribe, chunk) for chunk in chunks]
                for future in as_completed(futures):
                    all_results.append(future.result())
        else:
            for chunk in chunks:
                all_results.append(_load_model_and_transcribe(chunk))
        
        all_results.sort(key=lambda x: x.chunk_idx)
        
        all_segments = []
        for r in all_results:
            all_segments.extend(r.segments)
        
        full_text = " ".join(r.text for r in all_results)
        
        return {
            "text": full_text.strip(),
            "segments": all_segments,
        }
