import subprocess
from pathlib import Path
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from zk_utils.infrastructure.zk.zk_client import ZkClient


class TestZkClientGetLastModifiedNote:
    """ZkClientの最新変更ノート取得機能テスト"""

    @pytest.fixture
    def client(self) -> ZkClient:
        return ZkClient(cwd=Path("/test"))

    def test_get_last_modified_note_success(
        self, client: ZkClient, mocker: MockerFixture
    ) -> None:
        # Given: モックされたsubprocess実行
        mock_run = mocker.patch("subprocess.run")
        mock_result = Mock()
        mock_result.stdout = "/path/latest.md|Latest Note|recent,updated"
        mock_run.return_value = mock_result

        # When: 最新変更ノートを取得する
        note = client.get_last_modified_note()

        # Then: @with_indexデコレータにより2回の呼び出し
        assert mock_run.call_count == 2

        # 最後の呼び出しで適切なコマンドが実行されること
        mock_run.assert_called_with(
            [
                "zk",
                "list",
                "--quiet",
                "--no-pager",
                "---limit",
                "1",
                "--sort",
                "modified-",
                "--format",
                '{{path}}|{{title}}|{{join tags ","}}',
            ],
            capture_output=True,
            text=True,
            cwd=Path("/test"),
            check=True,
        )
        assert note is not None
        assert note.title == "Latest Note"
        assert note.path == Path("/path/latest.md")
        assert note.tags == ["recent", "updated"]

    def test_get_last_modified_note_no_result_should_return_none(
        self, client: ZkClient, mocker: MockerFixture
    ) -> None:
        # Given: 空の出力
        mock_run = mocker.patch("subprocess.run")
        mock_result = Mock()
        mock_result.stdout = ""
        mock_run.return_value = mock_result

        # When: 最新変更ノートを取得する
        note = client.get_last_modified_note()

        # Then: Noneが返されること
        assert note is None

    def test_get_last_modified_note_command_failure(
        self, client: ZkClient, mocker: MockerFixture
    ) -> None:
        # Given: 失敗するsubprocess実行
        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = subprocess.CalledProcessError(
            1, ["zk", "list"], stderr="List command failed"
        )

        # When & Then: RuntimeErrorが発生すること
        with pytest.raises(RuntimeError, match="Error: List command failed"):
            client.get_last_modified_note()

    def test_get_last_modified_note_parse_failure_should_return_none(
        self, client: ZkClient, mocker: MockerFixture
    ) -> None:
        # Given: パースできない形式の出力
        mock_run = mocker.patch("subprocess.run")
        mock_result = Mock()
        mock_result.stdout = "invalid_format"
        mock_run.return_value = mock_result

        # When: 最新変更ノートを取得する
        note = client.get_last_modified_note()

        # Then: Noneが返されること
        assert note is None
