import subprocess
from pathlib import Path
from unittest.mock import Mock

import pytest
from injector import Injector
from pytest_mock import MockerFixture

from zk_utils.presentation.injector import injector as app_injector


@pytest.fixture
def sample_zk_notes_output() -> str:
    """zkコマンドのget_notes出力例"""
    return (
        "/path/to/note1.md|テストノート1|tag1,tag2\n"
        "/path/to/note2.md|Title with | pipe|tag3\n"
        "/path/to/note3.md|タグなしノート|\n"
        "/path/to/note4.md|Empty Tags Note|\n"
    )


@pytest.fixture
def sample_zk_empty_notes_output() -> str:
    """zkコマンドの空のノート出力例"""
    return ""


@pytest.fixture
def sample_zk_single_note_output() -> str:
    """zkコマンドの単一ノート出力例"""
    return "/path/to/test.md|テストノート|tag1,tag2"


@pytest.fixture
def sample_zk_note_content_output() -> str:
    """zkコマンドのget_content出力例"""
    return (
        "# テストノート\n\nこれはテスト用のノート内容です。\n\n## セクション1\n内容1\n"
    )


@pytest.fixture
def sample_zk_tags_output() -> str:
    """zkコマンドのget_tags出力例"""
    return "tag1|5\ntag2|3\ntag3|1\nprogramming|10\n"


@pytest.fixture
def sample_zk_empty_tags_output() -> str:
    """zkコマンドの空のタグ出力例"""
    return ""


@pytest.fixture
def sample_zk_create_note_output() -> str:
    """zkコマンドのcreate_note出力例"""
    return "/path/to/new/note.md"


@pytest.fixture
def mock_subprocess_run(mocker: MockerFixture) -> Mock:
    """subprocess.runをモック化"""
    mock = mocker.patch("subprocess.run")

    # デフォルトの正常終了設定
    mock.return_value.returncode = 0
    mock.return_value.stderr = ""

    return mock


@pytest.fixture
def mock_failed_subprocess(mock_subprocess_run: Mock) -> Mock:
    """失敗するzkコマンド実行をモック化"""
    mock_subprocess_run.side_effect = subprocess.CalledProcessError(
        returncode=1, cmd=["zk", "list"], stderr="Error: zk command failed"
    )
    return mock_subprocess_run


@pytest.fixture
def test_injector() -> Injector:
    """テスト用DIコンテナ"""
    return app_injector


@pytest.fixture
def sample_note_path() -> Path:
    """テスト用ノートパス"""
    return Path("/path/to/test.md")


@pytest.fixture
def sample_note_title() -> str:
    """テスト用ノートタイトル"""
    return "テストノート"


@pytest.fixture
def large_notes_output() -> str:
    """大量データテスト用のノート出力"""
    notes = []
    for i in range(100):
        notes.append(f"/path/to/note{i}.md|ノート{i}|tag{i % 5}")
    return "\n".join(notes) + "\n"


@pytest.fixture
def special_character_notes_output() -> str:
    """特殊文字を含むノート出力"""
    return (
        "/path/to/special.md|タイトル with 特殊文字 @#$%|tag1\n"
        "/path/emoji.md|📝 Emoji Note 🎯|emoji,special\n"
        "/path/unicode.md|ユニコード文字 αβγ δεζ|unicode\n"
    )
