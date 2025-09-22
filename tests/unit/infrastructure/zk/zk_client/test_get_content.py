from pathlib import Path
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from zk_utils.infrastructure.zk.zk_client import ZkClient


class TestZkClientGetContent:
    """ZkClientのコンテンツ取得機能テスト"""

    @pytest.fixture
    def client(self) -> ZkClient:
        return ZkClient(cwd=Path("/test"))

    def test_get_content_success(self, client: ZkClient, mocker: MockerFixture) -> None:
        # Given: モックされたsubprocess実行
        mock_run = mocker.patch("subprocess.run")
        mock_result = Mock()
        mock_result.stdout = "# Test Note\n\nThis is test content."
        mock_run.return_value = mock_result

        # When: コンテンツを取得する
        content = client.get_content(Path("/test.md"))

        # Then: @with_indexデコレータにより2回の呼び出し
        assert mock_run.call_count == 2

        # 最後の呼び出しで適切なコマンドが実行されること
        mock_run.assert_called_with(
            [
                "zk",
                "list",
                "--quiet",
                "--no-pager",
                "--sort",
                "title",
                "--format",
                "{{raw-content}}",
                "/test.md",
            ],
            capture_output=True,
            text=True,
            cwd=Path("/test"),
            check=True,
        )
        assert content == "# Test Note\n\nThis is test content."
