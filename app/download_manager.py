import asyncio
import uuid
import threading
from typing import Dict, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

class TaskStage(str, Enum):
    DOWNLOADING = "downloading"
    EXTRACTING_SUBS = "extracting_subs"
    TRANSLATING = "translating"
    MERGING = "merging"
    EMBEDDING = "embedding"
    COMPLETE = "complete"
    ERROR = "error"

@dataclass
class DownloadTask:
    task_id: str
    url: str
    translate_subtitles: bool = False
    stage: TaskStage = TaskStage.DOWNLOADING
    progress: float = 0.0
    speed: Optional[str] = None
    eta: Optional[str] = None
    filename: Optional[str] = None
    error: Optional[str] = None
    file_path: Optional[str] = None
    _event: threading.Event = field(default_factory=threading.Event)
    _callbacks: list = field(default_factory=list)

    def update(self, stage: TaskStage = None, progress: float = None,
               speed: str = None, eta: str = None, filename: str = None,
               error: str = None, file_path: str = None):
        if stage is not None:
            self.stage = stage
        if progress is not None:
            self.progress = progress
        if speed is not None:
            self.speed = speed
        if eta is not None:
            self.eta = eta
        if filename is not None:
            self.filename = filename
        if error is not None:
            self.error = error
        if file_path is not None:
            self.file_path = file_path
        self._notify()

    def _notify(self):
        for cb in self._callbacks:
            try:
                cb(self)
            except Exception:
                pass

    def add_callback(self, cb: Callable):
        self._callbacks.append(cb)

    def wait(self):
        self._event.wait()

    def set_complete(self):
        self._event.set()


class DownloadManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._tasks = {}
                    cls._instance._task_lock = threading.Lock()
        return cls._instance

    def create_task(self, url: str, translate_subtitles: bool = False) -> str:
        task_id = str(uuid.uuid4())[:8]
        task = DownloadTask(task_id=task_id, url=url, translate_subtitles=translate_subtitles)
        with self._task_lock:
            self._tasks[task_id] = task
        return task_id

    def get_task(self, task_id: str) -> Optional[DownloadTask]:
        with self._task_lock:
            return self._tasks.get(task_id)

    def cancel_task(self, task_id: str) -> bool:
        with self._task_lock:
            task = self._tasks.get(task_id)
            if task:
                task.update(stage=TaskStage.ERROR, error="Cancelled by user")
                task.set_complete()
                return True
            return False

    def remove_task(self, task_id: str):
        with self._task_lock:
            self._tasks.pop(task_id, None)


manager = DownloadManager()
