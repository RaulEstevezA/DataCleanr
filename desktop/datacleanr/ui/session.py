"""What each history step did, stored as data so it can be shown in any language and saved in a profile."""

from dataclasses import dataclass
from typing import Literal

from ..core.dataset import Dataset

# Everything that can be applied to the cells of one column (same ids as the web version)
CellAction = Literal[
    "trim", "collapseSpaces", "lowercase", "uppercase", "titleCase", "custom", "phone", "date", "amount", "similar"
]


@dataclass(frozen=True)
class ImportOperation:
    kind: Literal["import"] = "import"


@dataclass(frozen=True)
class CellsOperation:
    column: int
    action: CellAction
    count: int
    kind: Literal["cells"] = "cells"


@dataclass(frozen=True)
class RemoveRowsOperation:
    mode: Literal["exact", "similar"]
    count: int
    filled: int
    kind: Literal["removeRows"] = "removeRows"


Operation = ImportOperation | CellsOperation | RemoveRowsOperation


@dataclass(frozen=True)
class HistoryStep:
    dataset: Dataset
    operation: Operation
    # How to replay this step in a cleaning profile; None when it cannot be replayed
    profile_step: dict | None = None
