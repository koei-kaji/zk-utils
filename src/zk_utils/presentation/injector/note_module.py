from injector import Binder, Module

from ...application.notes import IFNoteQueryService
from ...domain.models.notes import IFNoteRepository
from ...infrastructure.zk.notes import ZkNoteQueryService, ZkNoteRepository


class NoteModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(IFNoteQueryService, ZkNoteQueryService)
        binder.bind(IFNoteRepository, ZkNoteRepository)
