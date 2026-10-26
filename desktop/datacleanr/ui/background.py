"""Runs slow work (reading big files, fuzzy matching) off the interface thread."""

from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal


class _Signals(QObject):
    done = Signal(object)
    failed = Signal(object)


class _Task(QRunnable):
    def __init__(self, work: Callable[[], Any]):
        super().__init__()
        self.work = work
        self.signals = _Signals()

    def run(self) -> None:
        try:
            result = self.work()
        except Exception as error:  # noqa: BLE001 (reported to the interface, never swallowed)
            self.signals.failed.emit(error)
        else:
            self.signals.done.emit(result)


# Tasks are kept referenced until they finish, or Python could collect their signals early
_running: set[_Task] = set()


def run_in_background(
    work: Callable[[], Any], on_done: Callable[[Any], None], on_error: Callable[[Exception], None]
) -> None:
    """Calls `work` in a worker thread; `on_done` / `on_error` run back on the interface thread."""
    task = _Task(work)
    _running.add(task)

    def finish(callback: Callable[[Any], None], value: Any) -> None:
        _running.discard(task)
        callback(value)

    task.signals.done.connect(lambda result: finish(on_done, result))
    task.signals.failed.connect(lambda error: finish(on_error, error))
    QThreadPool.globalInstance().start(task)
