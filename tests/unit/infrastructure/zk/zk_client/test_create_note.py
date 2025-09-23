import subprocess
from pathlib import Path
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from zk_utils.infrastructure.zk.zk_client import ZkClient


class TestZkClientCreateNote:
    """ZkClientのnote作成機能テスト"""

    @pytest.fixture
    def client(self) -> ZkClient:
        return ZkClient(cwd=Path("/test"))

    def test_create_note_success(self, client: ZkClient, mocker: MockerFixture) -> None:
        # Given: モックされたsubprocess実行
        mock_run = mocker.patch("subprocess.run")
        mock_result = Mock()
        mock_result.stdout = "/created/note.md"
        mock_run.return_value = mock_result

        # When: ノートを作成する
        note = client.create_note("New Note", Path("notes/"))

        # Then: @with_indexデコレータにより2回の呼び出し
        assert mock_run.call_count == 2

        # 最後の呼び出しで適切なコマンドが実行されること
        mock_run.assert_called_with(
            ["zk", "new", "--print-path", "--title", "New Note", "notes"],
            capture_output=True,
            text=True,
            cwd=Path("/test"),
            check=True,
        )
        assert note.title == "New Note"
        assert note.path == Path("/created/note.md")
        assert note.tags == []

    def test_create_note_command_failure(
        self, client: ZkClient, mocker: MockerFixture
    ) -> None:
        # Given: 失敗するsubprocess実行
        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = subprocess.CalledProcessError(
            1, ["zk", "new"], stderr="Create command failed"
        )

        # When & Then: RuntimeErrorが発生すること
        with pytest.raises(RuntimeError, match="Error: Create command failed"):
            client.create_note("Failed Note", Path("notes/"))
