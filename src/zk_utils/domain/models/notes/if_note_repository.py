import abc
from pathlib import Path

from .._abc import IFRepository
from .note import Note


class IFNoteRepository(IFRepository):
    @abc.abstractmethod
    def find_note_content(self, path: Path) -> Note: ...

    @abc.abstractmethod
    def create_note(self, title: str, path: Path) -> Note: ...

    @abc.abstractmethod
    def find_last_modified_note(self) -> Note: ...
