from pathlib import Path

from injector import Module, provider

from ..settings import Settings


class ZkModule(Module):
    @provider
    def cwd(self) -> Path:
        settings = Settings()  # type: ignore[call-arg]
        return settings.zk_dir
