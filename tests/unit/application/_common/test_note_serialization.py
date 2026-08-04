from pathlib import Path

from zk_utils.application._common.note import Note


def test_path_should_be_serialized_as_string_in_json_mode() -> None:
    path = Path("/path/to/note.md")
    note = Note(title="Note", path=path, tags=[])

    assert note.path == path
    assert note.model_dump()["path"] == path
    assert note.model_dump(mode="json")["path"] == str(path)
