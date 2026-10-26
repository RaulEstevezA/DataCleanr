from datacleanr.core.history import create_history, go_to, push_entry, redo, undo

ABC = push_entry(push_entry(create_history("a"), "b"), "c")


def test_starts_with_nothing_to_undo_or_redo():
    history = create_history("a")
    assert history.current == "a"
    assert not history.can_undo
    assert not history.can_redo


def test_undo_and_redo():
    back = undo(ABC)
    assert back.current == "b"
    assert back.can_redo
    assert redo(back).current == "c"


def test_does_not_go_past_the_ends():
    assert redo(ABC).current == "c"
    assert undo(undo(undo(ABC))).current == "a"


def test_pushing_discards_redoable_entries():
    branched = push_entry(undo(undo(ABC)), "x")
    assert branched.entries == ("a", "x")
    assert not branched.can_redo


def test_jumps_to_any_entry():
    assert go_to(ABC, 0).current == "a"
    assert go_to(ABC, 99).current == "c"
