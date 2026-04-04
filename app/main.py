import asyncio
import json
import os
import sys
import threading
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
import sse_starlette.sse as sse

from .config import CORS_ORIGINS, OUTPUT_DIR
from .models import DownloadRequest, DownloadResponse, ProgressEvent, TaskStatus
from .download_manager import manager, DownloadTask, TaskStage
from .yt_dlp_wrapper import download_video
from .translator import translate_srt

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown - cleanup if needed
    pass

app = FastAPI(title="YouTube Downloader API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

def run_download(task: DownloadTask):
    """Run download in thread pool."""

    def progress_hook(d: dict):
        if d['status'] == 'downloading':
            total = d.get('total', 0) or 1
            downloaded = d.get('downloaded', 0) or 0
            speed = d.get('speed', 0)
            eta = d.get('eta', 0)

            progress = (downloaded / total) * 100 if total > 0 else 0
            speed_str = f"{speed / 1024 / 1024:.1f}MB/s" if speed else ""
            eta_str = f"{int(eta)}s" if eta else ""

            task.update(
                stage=TaskStage.DOWNLOADING,
                progress=progress,
                speed=speed_str,
                eta=eta_str
            )
        elif d['status'] == 'finished':
            task.update(stage=TaskStage.EXTRACTING_SUBS, progress=95)

    try:
        # Download video
        task.update(stage=TaskStage.DOWNLOADING, progress=0)
        file_path, subtitle_path = download_video(
            task.url,
            task.task_id,
            task.translate_subtitles,
            progress_hook
        )

        if file_path is None:
            task.update(stage=TaskStage.ERROR, error=subtitle_path)
            task.set_complete()
            return

        print(f"[DEBUG] download_video returned: file_path={file_path}, subtitle_path={subtitle_path}")
        task.update(filename=os.path.basename(file_path), file_path=file_path)

        # If translation is NOT requested, keep original video with original subtitles
        if not task.translate_subtitles:
            # Original video mode - just keep the downloaded file as-is
            task.update(stage=TaskStage.COMPLETE, progress=100)
            task.set_complete()
            return

        # Translation requested - use ASR + translation + embedding
        task.update(stage=TaskStage.EXTRACTING_SUBS, progress=80)

        # If no original subtitles, use Whisper ASR
        if subtitle_path is None:
            try:
                from .asr import extract_audio_from_video, transcribe_audio, segments_to_srt

                # Extract audio from video
                audio_path = extract_audio_from_video(file_path)
                if audio_path and os.path.exists(audio_path):
                    # Transcribe audio to SRT
                    segments = transcribe_audio(audio_path, language="en")
                    if segments:
                        base_name = os.path.splitext(file_path)[0]
                        subtitle_path = base_name + '.srt'
                        segments_to_srt(segments, subtitle_path)
                        # Remove temp audio file
                        try:
                            os.remove(audio_path)
                        except:
                            pass
            except Exception as e:
                # ASR failed, continue without subtitles
                pass

        # Translate subtitles
        if subtitle_path:
            task.update(stage=TaskStage.TRANSLATING, progress=85)
            try:
                translated_path = translate_srt(subtitle_path, 'zh-CN')
                if translated_path:
                    subtitle_path = translated_path
            except Exception as e:
                # Continue without translation if it fails
                pass

        # Embed subtitles into video using FFmpeg with styled background
        task.update(stage=TaskStage.EMBEDDING, progress=97)
        if subtitle_path and os.path.exists(subtitle_path):
            try:
                from .config import FFMPEG_PATH
                import subprocess

                ffmpeg_bin_name = 'ffmpeg.exe' if sys.platform == 'win32' else 'ffmpeg'
                ffmpeg_bin = os.path.join(FFMPEG_PATH, ffmpeg_bin_name)
                output_file = file_path.rsplit('.', 1)[0] + '_with_subs.mkv'

                # Convert SRT to ASS with background style
                ass_subtitle = subtitle_path.rsplit('.', 1)[0] + '.ass'
                srt_to_ass_cmd = [
                    ffmpeg_bin,
                    '-i', subtitle_path,
                    '-y',
                    ass_subtitle
                ]
                subprocess.run(srt_to_ass_cmd, capture_output=True)

                # Embed with styled subtitles using ASS format
                cmd = [
                    ffmpeg_bin,
                    '-i', file_path,
                    '-vf', f"subtitles='{ass_subtitle.replace(chr(92), chr(92)+chr(92))}':force_style='FontSize=24,PrimaryColour=&H00FFFFFF&,OutlineColour=&H00000000&,BackColour=&H80000000&,Outline=2,MarginV=30'",
                    '-c:a', 'copy',
                    '-y',
                    output_file
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode != 0 or not os.path.exists(output_file):
                    # Fallback: try simple embed
                    cmd = [
                        ffmpeg_bin,
                        '-i', file_path,
                        '-i', ass_subtitle,
                        '-c', 'copy',
                        '-c:s', 'ass',
                        '-map', '0',
                        '-map', '1',
                        '-y',
                        output_file
                    ]
                    result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0 and os.path.exists(output_file):
                    os.remove(file_path)
                    os.rename(output_file, file_path)
                    # Clean up temp ASS file
                    try:
                        os.remove(ass_subtitle)
                    except:
                        pass
            except Exception as e:
                pass

        task.update(stage=TaskStage.COMPLETE, progress=100)
        task.set_complete()

    except Exception as e:
        task.update(stage=TaskStage.ERROR, error=str(e))
        task.set_complete()

@app.post("/api/download", response_model=DownloadResponse)
async def start_download(request: DownloadRequest, background_tasks: BackgroundTasks):
    """Start a new download task."""
    if not request.url or not ('youtube.com' in request.url or 'youtu.be' in request.url):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    task_id = manager.create_task(request.url, request.translate_subtitles)
    task = manager.get_task(task_id)

    background_tasks.add_task(run_download, task)

    return DownloadResponse(task_id=task_id, status="started")

@app.get("/api/progress/{task_id}")
async def progress_stream(task_id: str):
    """SSE stream for download progress."""
    task = manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    async def event_generator():
        while True:
            progress_data = {
                "task_id": task.task_id,
                "stage": task.stage.value,
                "progress": task.progress,
                "speed": task.speed,
                "eta": task.eta,
                "filename": task.filename,
                "error": task.error,
            }
            yield {"event": "progress", "data": json.dumps(progress_data)}

            if task.stage in (TaskStage.COMPLETE, TaskStage.ERROR):
                break

            await asyncio.sleep(0.3)

    return sse.EventSourceResponse(event_generator())

@app.get("/api/status/{task_id}", response_model=TaskStatus)
async def get_status(task_id: str):
    """Get current task status."""
    task = manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskStatus(
        task_id=task.task_id,
        status=task.stage.value,
        progress=task.progress,
        filename=task.filename,
        error=task.error
    )

@app.delete("/api/cancel/{task_id}")
async def cancel_download(task_id: str):
    """Cancel a download task."""
    if not manager.cancel_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return {"cancelled": True}

@app.get("/api/download/{task_id}")
async def download_file(task_id: str):
    """Stream the downloaded file."""
    task = manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.stage != TaskStage.COMPLETE or not task.file_path:
        raise HTTPException(status_code=400, detail="Download not complete")

    if not os.path.exists(task.file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # Sanitize filename - remove special characters that cause issues
    import re
    safe_filename = re.sub(r'[^\w\s\-\.]', '_', task.filename or 'video.mkv')

    return FileResponse(
        path=task.file_path,
        filename=safe_filename,
        media_type='video/x-matroska',
    )

@app.get("/api/output_dir")
async def get_output_dir():
    """Get the output directory path."""
    return {"output_dir": str(OUTPUT_DIR)}
