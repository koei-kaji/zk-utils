from pathlib import Path
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from zk_utils.infrastructure.zk.zk_client import ZkClient


class TestZkClientGetNote:
    """ZkClientの単一note取得機能テスト"""

    @pytest.fixture
    def client(self) -> ZkClient:
        return ZkClient(cwd=Path("/test"))

    def test_get_note_success(self, client: ZkClient, mocker: MockerFixture) -> None:
        # Given: モックされたsubprocess実行(note情報とコンテンツ)
        mock_run = mocker.patch("subprocess.run")

        # ノート情報の取得
        note_result = Mock()
        note_result.stdout = "/test.md|Test Note|python,testing"

        # コンテンツの取得
        content_result = Mock()
        content_result.stdout = "# Test Note\n\nTest content here."

        # @with_indexデコレータにより4回の呼び出しが発生
        # 1. _execute_index (get_note用)
        # 2. _execute_zk_list_single (note情報取得)
        # 3. _execute_index (get_content用)
        # 4. _execute_zk_list_single (content取得)
        index_result = Mock()
        index_result.stdout = ""
        mock_run.side_effect = [index_result, note_result, index_result, content_result]

        # When: 単一ノートを取得する
        note = client.get_note(Path("/test.md"))

        # Then: note情報とコンテンツが設定されたNoteオブジェクトが返されること
        assert note is not None
        assert note.title == "Test Note"
        assert note.path == Path("/test.md")
        assert note.tags == ["python", "testing"]
        assert note.content == "# Test Note\n\nTest content here."
        assert mock_run.call_count == 4

    def test_get_note_parse_failure_should_return_none(
        self, client: ZkClient, mocker: MockerFixture
    ) -> None:
        # Given: パースできない形式の出力
        mock_run = mocker.patch("subprocess.run")
        mock_result = Mock()
        mock_result.stdout = "invalid_format"
        mock_run.return_value = mock_result

        # When: 単一ノートを取得する
        note = client.get_note(Path("/test.md"))

        # Then: Noneが返されること
        assert note is None
