from injector import Injector

from .note_module import NoteModule
from .tag_module import TagModule
from .zk_module import ZkModule

injector = Injector(
    [
        NoteModule,
        TagModule,
        ZkModule,
    ]
)
