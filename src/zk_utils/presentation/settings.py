from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    zk_dir: Path
