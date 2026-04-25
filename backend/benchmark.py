"""Benchmark different STT models on the same audio file."""

import os
import sys
import time

import soundfile as sf

sys.path.insert(0, os.path.dirname(__file__))


def benchmark_model(model_name: str, audio_path: str, chunk_duration: int = 300):
    """Transcribe audio with a given model and return metrics."""
    from mlx_audio.stt import load_model

    print(f"\n{'=' * 50}")
    print(f"Model: {model_name}")
    print(f"{'=' * 50}")

    try:
        # Load model
        load_start = time.time()
        model = load_model(model_name)
        load_time = time.time() - load_start
        print(f"Load time: {load_time:.2f}s")

        # Get audio duration
        data, sr = sf.read(audio_path)
        duration = len(data) / sr
        print(f"Audio duration: {duration:.2f}s")

        # Transcribe
        transcribe_start = time.time()
        result = model.generate(audio=audio_path, max_tokens=16384)
        transcribe_time = time.time() - transcribe_start

        realtime_factor = transcribe_time / duration
        print(f"Transcription time: {transcribe_time:.2f}s")
        print(f"Realtime factor: {realtime_factor:.2f}x")

        # Extract text
        if hasattr(result, "text"):
            text = result.text
        else:
            text = str(result)

        print(f"Text length: {len(text)} chars")
        print(f"Text preview: {text[:200]}...")

        # Extract segments if available
        segments = []
        if hasattr(result, "segments") and result.segments:
            for seg in result.segments:
                if isinstance(seg, dict):
                    segments.append(seg)
                else:
                    segments.append(
                        {
                            "start": getattr(seg, "start", 0),
                            "end": getattr(seg, "end", 0),
                            "text": getattr(seg, "text", ""),
                        }
                    )
            print(f"Segments: {len(segments)}")

        return {
            "model": model_name,
            "load_time": load_time,
            "transcribe_time": transcribe_time,
            "realtime_factor": realtime_factor,
            "text": text,
            "segments": segments,
            "duration": duration,
        }

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return None


def compare_transcriptions(results: list):
    """Compare transcriptions from different models."""
    print(f"\n{'=' * 60}")
    print("COMPARISON")
    print(f"{'=' * 60}")

    for i, r in enumerate(results):
        if r:
            print(f"\n{i + 1}. {r['model']}")
            print(f"   Time: {r['transcribe_time']:.2f}s ({r['realtime_factor']:.2f}x)")
            print(f"   Chars: {len(r['text'])}")

    # Check text similarity (simple word-based)
    if len(results) >= 2:
        texts = [r["text"] for r in results if r]
        wordsets = [set(t.lower().split()) for t in texts]

        print("\nWord overlap analysis:")
        for i in range(len(textsets)):
            for j in range(i + 1, len(textsets)):
                overlap = wordsets[i] & wordsets[j]
                union = wordsets[i] | wordsets[j]
                jaccard = len(overlap) / len(union) if union else 0
                print(
                    f"   {results[i]['model']} vs {results[j]['model']}: {jaccard:.2%} word overlap"
                )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python benchmark.py <audio_file> [model1] [model2] ...")
        print("\nAvailable models:")
        print("  - mlx-community/VibeVoice-ASR-6bit (default)")
        print("  - mlx-community/VibeVoice-ASR-4bit")
        print("\nUsing default model on lecture_7.wav...")
        audio_path = "/Users/irb/.udhkur/recordings/lecture_7.wav"
        models = ["mlx-community/VibeVoice-ASR-6bit"]
    else:
        audio_path = sys.argv[1]
        models = sys.argv[2:] if len(sys.argv) > 2 else ["mlx-community/VibeVoice-ASR-6bit"]

    if not os.path.exists(audio_path):
        print(f"File not found: {audio_path}")
        sys.exit(1)

    print(f"Audio file: {audio_path}")
    print(f"Models: {models}")

    results = []
    for model in models:
        result = benchmark_model(model, audio_path)
        results.append(result)

    compare_transcriptions(results)
