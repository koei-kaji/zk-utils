import subprocess
from functools import wraps
from pathlib import Path
from typing import Callable, Final, TypeVar

from injector import inject, singleton

from ..._base_models import BaseFrozenModel
from .dao.note import Note
from .dao.tag import Tag

F = TypeVar("F", bound=Callable[..., object])


def with_index(func: F) -> F:
    @wraps(func)
    def wrapper(self: "ZkClient", *args: object, **kwargs: object) -> object:
        self._execute_index()
        return func(self, *args, **kwargs)

    return wrapper  # type: ignore[return-value]


FORMAT_NOTE: Final[str] = '{{path}}|{{title}}|{{join tags ","}}'
FORMAT_CONTENT: Final[str] = "{{raw-content}}"
FORMAT_TAG: Final[str] = "{{name}}|{{note-count}}"


@singleton
class ZkClient(BaseFrozenModel):
    _cwd: Path

    @inject
    def __init__(self, cwd: Path) -> None:
        super().__init__()
        self._cwd = cwd

    def _execute_index(self) -> None:
        command = ["zk", "index", "--quiet"]

        try:
            subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=self._cwd,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error: {e.stderr}") from e

    @with_index
    def _execute_zk_list_single(
        self,
        fmt: str = "",
        conditions: list[str] = [],
    ) -> str:
        command = [
            "zk",
            "list",
            "--quiet",
            "--no-pager",
            "--sort",
            "title",
            "--format",
            fmt,
        ]

        try:
            stdout = subprocess.run(
                command + conditions,
                capture_output=True,
                text=True,
                cwd=self._cwd,
                check=True,
            )

            return stdout.stdout.strip()

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error: {e.stderr}") from e

    @with_index
    def _execute_zk_list_multilines(
        self,
        fmt: str = "",
        conditions: list[str] = [],
    ) -> list[str]:
        command = [
            "zk",
            "list",
            "--quiet",
            "--no-pager",
            "--sort",
            "title",
            "--format",
            fmt,
        ]

        try:
            stdout = subprocess.run(
                command + conditions,
                capture_output=True,
                text=True,
                cwd=self._cwd,
                check=True,
            )
            return stdout.stdout.strip().splitlines()

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error: {e.stderr}") from e

    @with_index
    def _execute_zk_tag_list_multilines(
        self,
        fmt: str = "",
    ) -> list[str]:
        command = [
            "zk",
            "tag",
            "list",
            "--quiet",
            "--no-pager",
            "--format",
            fmt,
        ]

        try:
            stdout = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=self._cwd,
                check=True,
            )
            return stdout.stdout.strip().splitlines()

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error: {e.stderr}") from e

    def _parse_note(self, target: str) -> Note | None:
        # パイプ文字を含むタイトルに対応するため、逆方向から分割
        # 最後のパイプでtagsを、最初のパイプでpathを分離
        last_pipe_idx = target.rfind("|")
        if last_pipe_idx == -1:
            return None

        tags_part = target[last_pipe_idx + 1 :]
        remaining = target[:last_pipe_idx]

        first_pipe_idx = remaining.find("|")
        if first_pipe_idx == -1:
            return None

        path = remaining[:first_pipe_idx]
        title = remaining[first_pipe_idx + 1 :]

        if tags_part == "":
            tags = []
        else:
            tags = tags_part.split(",")

        return Note(title=title, path=Path(path), tags=tags)

    def _parse_tag(self, target: str) -> Tag | None:
        pipe_idx = target.rfind("|")
        if pipe_idx == -1:
            return None

        name = target[:pipe_idx]
        note_count_str = target[pipe_idx + 1 :]

        return Tag(name=name, note_count=int(note_count_str))

    def get_notes(self, conditions: list[str] = []) -> list[Note]:
        results = self._execute_zk_list_multilines(FORMAT_NOTE, conditions)

        notes: list[Note] = []
        for result in results:
            note = self._parse_note(result)
            if note is None:
                continue
            notes.append(note)

        return notes

    def get_tagless_notes(self) -> list[Note]:
        results = self._execute_zk_list_multilines(FORMAT_NOTE, ["--tagless"])

        notes: list[Note] = []
        for result in results:
            note = self._parse_note(result)
            if note is None:
                continue
            notes.append(note)

        return notes

    def get_note(self, path: Path) -> Note | None:
        result = self._execute_zk_list_single(FORMAT_NOTE, [str(path)])
        note = self._parse_note(result)

        if note is None:
            return None

        content = self.get_content(path)
        note.content = content

        return note

    def get_content(self, path: Path) -> str:
        return self._execute_zk_list_single(FORMAT_CONTENT, [str(path)])

    def get_tags(self) -> list[Tag]:
        results = self._execute_zk_tag_list_multilines(FORMAT_TAG)

        tags: list[Tag] = []
        for result in results:
            tag = self._parse_tag(result)
            if tag is None:
                continue
            tags.append(tag)

        return tags

    @with_index
    def create_note(self, title: str, path: Path) -> Note:
        command = ["zk", "new", "--print-path", "--title", title, str(path)]

        try:
            stdout = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=self._cwd,
                check=True,
            )

            path = Path(stdout.stdout)

            return Note(title=title, path=path, tags=[])

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error: {e.stderr}") from e

    @with_index
    def get_last_modified_note(self) -> Note | None:
        command = [
            "zk",
            "list",
            "--quiet",
            "--no-pager",
            "--limit",
            "1",
            "--sort",
            "modified-",
            "--format",
            FORMAT_NOTE,
        ]

        try:
            stdout = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=self._cwd,
                check=True,
            )

            return self._parse_note(stdout.stdout.strip())

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error: {e.stderr}") from e

    @with_index
    def get_random_note(self) -> Note | None:
        command = [
            "zk",
            "list",
            "--quiet",
            "--no-pager",
            "--limit",
            "1",
            "--sort",
            "random",
            "--format",
            FORMAT_NOTE,
        ]

        try:
            stdout = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=self._cwd,
                check=True,
            )

            return self._parse_note(stdout.stdout.strip())

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error: {e.stderr}") from e
