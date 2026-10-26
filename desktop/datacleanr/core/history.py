"""Linear undo/redo history. Mirrors web/src/core/history.ts.

Immutable: every function returns a new history. `index` points at the current entry;
entries after it can be redone.
"""

from dataclasses import dataclass, replace
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class History(Generic[T]):
    entries: tuple[T, ...]
    index: int = 0

    @property
    def current(self) -> T:
        return self.entries[self.index]

    @property
    def can_undo(self) -> bool:
        return self.index > 0

    @property
    def can_redo(self) -> bool:
        return self.index < len(self.entries) - 1


def create_history(first: T) -> History[T]:
    return History((first,))


def push_entry(history: History[T], entry: T) -> History[T]:
    """Adds an entry after the current one. Anything that could be redone is discarded."""
    return History((*history.entries[: history.index + 1], entry), history.index + 1)


def go_to(history: History[T], index: int) -> History[T]:
    return replace(history, index=min(max(index, 0), len(history.entries) - 1))


def undo(history: History[T]) -> History[T]:
    return go_to(history, history.index - 1)


def redo(history: History[T]) -> History[T]:
    return go_to(history, history.index + 1)
