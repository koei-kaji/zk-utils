from injector import Binder, Module

from ...application.tags import IFTagQueryService
from ...infrastructure.zk.tags import ZkTagQueryService


class TagModule(Module):
    def configure(self, binder: Binder) -> None:
        binder.bind(IFTagQueryService, ZkTagQueryService)  # type: ignore[type-abstract]
