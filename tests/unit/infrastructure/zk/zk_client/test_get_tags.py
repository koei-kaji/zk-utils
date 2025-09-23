import subprocess
from pathlib import Path
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from zk_utils.infrastructure.zk.zk_client import ZkClient


class TestZkClientGetTags:
    """ZkClientのタグ取得機能テスト"""

    @pytest.fixture
    def client(self) -> ZkClient:
        return ZkClient(cwd=Path("/test"))

    def test_get_tags_success(self, client: ZkClient, mocker: MockerFixture) -> None:
        # Given: モックされたsubprocess実行
        mock_run = mocker.patch("subprocess.run")
        mock_result = Mock()
        mock_result.stdout = "python|5\njava|3\ntest|1"
        mock_run.return_value = mock_result

        # When: タグ一覧を取得する
        tags = client.get_tags()

        # Then: @with_indexデコレータにより2回の呼び出し
        assert mock_run.call_count == 2

        # 最後の呼び出しで適切なコマンドが実行されること
        mock_run.assert_called_with(
            [
                "zk",
                "tag",
                "list",
                "--quiet",
                "--no-pager",
                "--format",
                "{{name}}|{{note-count}}",
            ],
            capture_output=True,
            text=True,
            cwd=Path("/test"),
            check=True,
        )
        assert len(tags) == 3
        assert tags[0].name == "python"
        assert tags[0].note_count == 5
        assert tags[1].name == "java"
        assert tags[1].note_count == 3
        assert tags[2].name == "test"
        assert tags[2].note_count == 1

    def test_get_tags_command_failure(
        self, client: ZkClient, mocker: MockerFixture
    ) -> None:
        # Given: 失敗するsubprocess実行
        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = subprocess.CalledProcessError(
            1, ["zk", "tag", "list"], stderr="Tag command failed"
        )

        # When & Then: RuntimeErrorが発生すること
        with pytest.raises(RuntimeError, match="Error: Tag command failed"):
            client.get_tags()
