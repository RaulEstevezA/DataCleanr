"""Human descriptions of history steps and profile steps. Mirrors web/src/components/profileLabels.ts."""

from ..core.dataset import column_label
from .i18n import Messages
from .session import HistoryStep


def action_name(t: Messages, action: str) -> str:
    return t.transform_names[action]


def describe_step(t: Messages, step: HistoryStep) -> str:
    operation, dataset = step.operation, step.dataset
    if operation.kind == "import":
        return t.history_import(dataset.file_name)
    if operation.kind == "cells":
        return t.history_cells(
            action_name(t, operation.action), column_label(dataset, operation.column), operation.count
        )
    if operation.mode == "exact":
        return t.history_remove_exact(operation.count, operation.filled)
    return t.history_remove_similar(operation.count, operation.filled)


def describe_profile_step(t: Messages, step: dict) -> str:
    kind = step["type"]
    if kind == "removeDuplicates":
        return t.profile_step_duplicates(", ".join(step["columns"]))
    if kind == "map":
        return t.profile_step_map(step["column"], len(step["mapping"]))
    action = step["transform"] if kind == "transform" else "custom" if kind == "replace" else kind
    return t.profile_step_cells(action_name(t, action), step["column"])
