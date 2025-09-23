import subprocess
from pathlib import Path
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from zk_utils.infrastructure.zk.zk_client import ZkClient


class TestZkClientGetRandomNote:
    """ZkClientのランダムノート取得機能テスト"""

    @pytest.fixture
    def client(self) -> ZkClient:
        return ZkClient(cwd=Path("/test"))

    def test_get_random_note_success(
        self, client: ZkClient, mocker: MockerFixture
    ) -> None:
        # Given: モックされたsubprocess実行
        mock_run = mocker.patch("subprocess.run")
        mock_result = Mock()
        mock_result.stdout = "/path/random.md|Random Note|random,test"
        mock_run.return_value = mock_result

        # When: ランダムノートを取得する
        note = client.get_random_note()

        # Then: @with_indexデコレータにより2回の呼び出し
        assert mock_run.call_count == 2

        # 最後の呼び出しで適切なコマンドが実行されること
        mock_run.assert_called_with(
            [
                "zk",
                "list",
                "--quiet",
                "--no-pager",
                "--limit",
                "1",
                "--sort",
                "random",
                "--format",
                '{{path}}|{{title}}|{{join tags ","}}',
            ],
            capture_output=True,
            text=True,
            cwd=Path("/test"),
            check=True,
        )
        assert note is not None
        assert note.title == "Random Note"
        assert note.path == Path("/path/random.md")
        assert note.tags == ["random", "test"]

    def test_get_random_note_no_result_should_return_none(
        self, client: ZkClient, mocker: MockerFixture
    ) -> None:
        # Given: 空の出力
        mock_run = mocker.patch("subprocess.run")
        mock_result = Mock()
        mock_result.stdout = ""
        mock_run.return_value = mock_result

        # When: ランダムノートを取得する
        note = client.get_random_note()

        # Then: Noneが返されること
        assert note is None

    def test_get_random_note_command_failure(
        self, client: ZkClient, mocker: MockerFixture
    ) -> None:
        # Given: 失敗するsubprocess実行
        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = subprocess.CalledProcessError(
            1, ["zk", "list"], stderr="List command failed"
        )

        # When & Then: RuntimeErrorが発生すること
        with pytest.raises(RuntimeError, match="Error: List command failed"):
            client.get_random_note()

    def test_get_random_note_parse_failure_should_return_none(
        self, client: ZkClient, mocker: MockerFixture
    ) -> None:
        # Given: パースできない形式の出力
        mock_run = mocker.patch("subprocess.run")
        mock_result = Mock()
        mock_result.stdout = "invalid_format"
        mock_run.return_value = mock_result

        # When: ランダムノートを取得する
        note = client.get_random_note()

        # Then: Noneが返されること
        assert note is None

    def test_get_random_note_with_japanese_content(
        self, client: ZkClient, mocker: MockerFixture
    ) -> None:
        # Given: 日本語を含む出力
        mock_run = mocker.patch("subprocess.run")
        mock_result = Mock()
        mock_result.stdout = "/日本語/パス.md|日本語タイトル|日本語タグ,テスト"
        mock_run.return_value = mock_result

        # When: ランダムノートを取得する
        note = client.get_random_note()

        # Then: 日本語が正しく処理されること
        assert note is not None
        assert note.title == "日本語タイトル"
        assert note.path == Path("/日本語/パス.md")
        assert note.tags == ["日本語タグ", "テスト"]

    def test_get_random_note_with_empty_tags(
        self, client: ZkClient, mocker: MockerFixture
    ) -> None:
        # Given: タグなしの出力
        mock_run = mocker.patch("subprocess.run")
        mock_result = Mock()
        mock_result.stdout = "/path/notags.md|No Tags Note|"
        mock_run.return_value = mock_result

        # When: ランダムノートを取得する
        note = client.get_random_note()

        # Then: 空のタグリストが返されること
        assert note is not None
        assert note.title == "No Tags Note"
        assert note.path == Path("/path/notags.md")
        assert note.tags == []

    def test_get_random_note_with_special_characters(
        self, client: ZkClient, mocker: MockerFixture
    ) -> None:
        # Given: 特殊文字を含む出力
        mock_run = mocker.patch("subprocess.run")
        mock_result = Mock()
        mock_result.stdout = "/path/special.md|Special @#$% Note|special,chars@#"
        mock_run.return_value = mock_result

        # When: ランダムノートを取得する
        note = client.get_random_note()

        # Then: 特殊文字が正しく処理されること
        assert note is not None
        assert note.title == "Special @#$% Note"
        assert note.path == Path("/path/special.md")
        assert note.tags == ["special", "chars@#"]

    def test_get_random_note_with_pipe_in_title(
        self, client: ZkClient, mocker: MockerFixture
    ) -> None:
        # Given: タイトルにパイプを含む出力
        mock_run = mocker.patch("subprocess.run")
        mock_result = Mock()
        mock_result.stdout = "/path/pipe.md|Title with | pipe|tag1,tag2"
        mock_run.return_value = mock_result

        # When: ランダムノートを取得する
        note = client.get_random_note()

        # Then: パイプが正しく処理されること
        assert note is not None
        assert note.title == "Title with | pipe"
        assert note.path == Path("/path/pipe.md")
        assert note.tags == ["tag1", "tag2"]

    def test_get_random_note_with_trailing_newline_in_tags(
        self, client: ZkClient, mocker: MockerFixture
    ) -> None:
        # Given: 最後のタグに改行が含まれる出力（修正前の問題ケース）
        mock_run = mocker.patch("subprocess.run")
        mock_result = Mock()
        mock_result.stdout = "/path/note.md|Note Title|terminal,zsh,git\n"
        mock_run.return_value = mock_result

        # When: ランダムノートを取得する
        note = client.get_random_note()

        # Then: 改行が除去されて正しく処理されること
        assert note is not None
        assert note.title == "Note Title"
        assert note.path == Path("/path/note.md")
        assert note.tags == ["terminal", "zsh", "git"]  # 改行除去済み
