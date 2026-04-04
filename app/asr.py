import os
import sys
from pathlib import Path

# Load model once at startup
_model = None

def get_model():
    """Load and return Whisper model."""
    global _model
    if _model is None:
        from faster_whisper import WhisperModel
        # Use base model for speed, can change to 'small', 'medium', 'large'
        # compute_type="int8" is faster and uses less memory
        _model = WhisperModel("base", device="cpu", compute_type="int8")
    return _model

def transcribe_audio(audio_path: str, language: str = "en") -> list[dict]:
    """
    Transcribe audio file to text with timestamps.
    Returns list of segments with 'start', 'end', 'text'.
    """
    model = get_model()

    # Transcribe
    segments, info = model.transcribe(audio_path, language=language, beam_size=5)

    result = []
    for segment in segments:
        result.append({
            'start': segment.start,
            'end': segment.end,
            'text': segment.text.strip()
        })

    return result

def segments_to_srt(segments: list[dict], output_path: str):
    """Convert Whisper segments to SRT format."""
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, seg in enumerate(segments, 1):
            start = format_timestamp(seg['start'])
            end = format_timestamp(seg['end'])
            text = seg['text']

            f.write(f"{i}\n")
            f.write(f"{start} --> {end}\n")
            f.write(f"{text}\n\n")

def format_timestamp(seconds: float) -> str:
    """Convert seconds to SRT timestamp format HH:MM:SS,mmm"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def extract_audio_from_video(video_path: str, output_path: str = None) -> str:
    """Extract audio from video file to WAV format."""
    import subprocess
    from .config import FFMPEG_PATH

    if output_path is None:
        output_path = video_path.rsplit('.', 1)[0] + '.wav'

    ffmpeg_bin_name = 'ffmpeg.exe' if sys.platform == 'win32' else 'ffmpeg'
    ffmpeg_bin = os.path.join(FFMPEG_PATH, ffmpeg_bin_name)

    cmd = [
        ffmpeg_bin,
        '-i', video_path,
        '-vn',
        '-acodec', 'pcm_s16le',
        '-ar', '16000',
        '-ac', '1',
        '-y',
        output_path
    ]

    subprocess.run(cmd, capture_output=True, text=True)
    return output_path