import yt_dlp
import os
from pathlib import Path
from typing import Optional
from .config import FFMPEG_PATH, OUTPUT_DIR
from .download_manager import TaskStage

def create_yt_dlp_opts(task_id: str, translate_subtitles: bool = False, progress_callback=None):
    """Create yt-dlp options for best quality download.

    Args:
        task_id: Download task ID
        translate_subtitles: If True, will embed translated subtitles later.
                            If False, download original video with original subtitles.
    """

    output_path = str(OUTPUT_DIR / task_id)

    # Build subtitle languages
    sub_langs = 'zh-CN,zh-Hans,zh-Hant,en'  # Download all available subtitles

    opts = {
        'format': 'bv*+ba/b',  # Best video + best audio, fallback
        'merge_output_format': 'mkv',
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'writesubtitles': True,
        'writeautomaticsub': True,
        'sub_langs': sub_langs,
        'subtitle_format': 'srt',
        'progress_hooks': [],
        'ffmpeg_location': FFMPEG_PATH,
        'quiet': True,
        'no_warnings': True,
    }

    # Only embed subtitles when translating - this keeps original video intact
    if translate_subtitles:
        opts['postprocessors'] = [{
            'key': 'FFmpegEmbedSubtitle',
            'already_have_subtitle': False,
        }]

    if progress_callback:
        opts['progress_hooks'].append(progress_callback)

    return opts

def download_video(url: str, task_id: str, translate_subtitles: bool = False,
                  progress_callback=None) -> tuple[Optional[str], Optional[str]]:
    """
    Download video with best quality and subtitles.

    Returns: (file_path, subtitle_path) or (None, error_message)
    """

    output_path = str(OUTPUT_DIR / task_id)
    Path(output_path).mkdir(parents=True, exist_ok=True)

    opts = create_yt_dlp_opts(task_id, translate_subtitles, progress_callback)

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)

            if info is None:
                return None, "Failed to extract video info"

            filename = ydl.prepare_filename(info)

            # Find the actual downloaded file (may have different extension after merge)
            base_name = os.path.splitext(filename)[0]
            possible_extensions = ['.mkv', '.mp4', '.webm', '.avi']

            file_path = None
            for ext in possible_extensions:
                test_path = os.path.join(output_path, os.path.basename(base_name + ext))
                if os.path.exists(test_path):
                    file_path = test_path
                    break

            if file_path is None and os.path.exists(os.path.join(output_path, os.path.basename(filename))):
                file_path = os.path.join(output_path, os.path.basename(filename))

            # Find subtitle files
            subtitle_path = None
            for ext in ['.srt', '.ass', '.vtt']:
                sub_name = base_name + ext
                if os.path.exists(sub_name):
                    subtitle_path = sub_name
                    break

            if file_path:
                return file_path, subtitle_path
            else:
                return None, "Failed to find downloaded file"

    except yt_dlp.utils.DownloadError as e:
        return None, f"Download error: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"

def get_video_info(url: str) -> Optional[dict]:
    """Get video information without downloading."""
    opts = {
        'quiet': True,
        'no_warnings': True,
        'skip_download': True,
    }

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info
    except Exception:
        return None
