import os
from pathlib import Path

# FFmpeg binary location - configurable via environment variable
# On Linux/Render (default): /usr/bin
# On Windows: set FFMPEG_PATH env var to the bin directory containing ffmpeg.exe
_ffmpeg_path_env = os.environ.get("FFMPEG_PATH", None)
if _ffmpeg_path_env:
    FFMPEG_PATH = _ffmpeg_path_env
else:
    # Default Windows path - for local development on Windows
    _local_app_data = os.environ.get("LOCALAPPDATA", None)
    if _local_app_data:
        FFMPEG_PATH = str(Path(_local_app_data) / "Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.1-full_build/bin")
    else:
        # Default Linux path for Render/docker deployment
        FFMPEG_PATH = "/usr/bin"

# Base output directory - configurable via environment variable
# On Linux/Render (default): /tmp/downloads
# On Windows: set OUTPUT_DIR env var or use ~/Videos/YouTube-Downloads
_output_dir_env = os.environ.get("OUTPUT_DIR", None)
if _output_dir_env:
    OUTPUT_DIR = Path(_output_dir_env)
else:
    OUTPUT_DIR = Path(os.path.expanduser("~/Videos/YouTube-Downloads"))

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Temp directory for partial downloads
TEMP_DIR = OUTPUT_DIR / "temp"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# yt-dlp location hint
YT_DLP_PATH = None  # Will use system yt-dlp if None

# CORS settings for frontend
CORS_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]