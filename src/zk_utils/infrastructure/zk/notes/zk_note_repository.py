from pathlib import Path

from injector import inject, singleton

from ....domain.models.notes.if_note_repository import IFNoteRepository
from ....domain.models.notes.note import Note
from ..zk_client import ZkClient


@singleton
class ZkNoteRepository(IFNoteRepository):
    _client: ZkClient

    @inject
    def __init__(self, client: ZkClient) -> None:
        super().__init__()
        self._client = client

    def find_note_content(self, path: Path) -> Note:
        result = self._client.get_note(path)

        if result is None:
            raise ValueError(f"Note not found at path: {path}")

        return Note(
            title=result.title,
            path=result.path,
            tags=result.tags,
            content=result.content,
        )

    def create_note(self, title: str, path: Path) -> Note:
        result = self._client.create_note(title, path)

        return Note(title=result.title, path=result.path, tags=[])

    def find_last_modified_note(self) -> Note:
        result = self._client.get_last_modified_note()

        if result is None:
            raise ValueError("Last modified note not found")

        return Note(
            title=result.title,
            path=result.path,
            tags=result.tags,
        )

    def find_tagless_notes(self) -> list[Note]:
        results = self._client.get_tagless_notes()

        return [
            Note(
                title=result.title,
                path=result.path,
                tags=result.tags,
            )
            for result in results
        ]

    def find_random_note(self) -> Note:
        result = self._client.get_random_note()

        if result is None:
            raise ValueError("Last modified note not found")

        return Note(
            title=result.title,
            path=result.path,
            tags=result.tags,
        )
