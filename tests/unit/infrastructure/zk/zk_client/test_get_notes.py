import subprocess
from pathlib import Path
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from zk_utils.infrastructure.zk.zk_client import ZkClient


class TestZkClientGetNotes:
    """ZkClientのnote取得機能テスト"""

    @pytest.fixture
    def client(self) -> ZkClient:
        return ZkClient(cwd=Path("/test"))

    def test_get_notes_success(self, client: ZkClient, mocker: MockerFixture) -> None:
        # Given: モックされたsubprocess実行
        mock_run = mocker.patch("subprocess.run")
        mock_result = Mock()
        mock_result.stdout = "/path1.md|Note 1|tag1\n/path2.md|Note 2|tag2,tag3"
        mock_run.return_value = mock_result

        # When: ノート一覧を取得する
        notes = client.get_notes()

        # Then: @with_indexデコレータにより_execute_index()とget_notesで計2回の呼び出し
        assert mock_run.call_count == 2

        # 最後の呼び出し（get_notes）が適切なコマンドで実行されること
        mock_run.assert_called_with(
            [
                "zk",
                "list",
                "--quiet",
                "--no-pager",
                "--sort",
                "title",
                "--format",
                '{{path}}|{{title}}|{{join tags ","}}',
            ],
            capture_output=True,
            text=True,
            cwd=Path("/test"),
            check=True,
        )
        assert len(notes) == 2
        assert notes[0].title == "Note 1"
        assert notes[0].path == Path("/path1.md")
        assert notes[0].tags == ["tag1"]
        assert notes[1].title == "Note 2"
        assert notes[1].path == Path("/path2.md")
        assert notes[1].tags == ["tag2", "tag3"]

    def test_get_notes_with_conditions(
        self, client: ZkClient, mocker: MockerFixture
    ) -> None:
        # Given: 検索条件とモックされたsubprocess実行
        conditions = ["--tag", "python"]
        mock_run = mocker.patch("subprocess.run")
        mock_result = Mock()
        mock_result.stdout = "/python.md|Python Note|python"
        mock_run.return_value = mock_result

        # When: 条件付きでノート一覧を取得する
        notes = client.get_notes(conditions)

        # Then: @with_indexデコレータにより2回の呼び出し
        assert mock_run.call_count == 2

        # 最後の呼び出しで条件がコマンドに追加されること
        mock_run.assert_called_with(
            [
                "zk",
                "list",
                "--quiet",
                "--no-pager",
                "--sort",
                "title",
                "--format",
                '{{path}}|{{title}}|{{join tags ","}}',
                "--tag",
                "python",
            ],
            capture_output=True,
            text=True,
            cwd=Path("/test"),
            check=True,
        )
        assert len(notes) == 1
        assert notes[0].title == "Python Note"

    def test_get_notes_command_failure(
        self, client: ZkClient, mocker: MockerFixture
    ) -> None:
        # Given: 失敗するsubprocess実行
        mock_run = mocker.patch("subprocess.run")
        mock_run.side_effect = subprocess.CalledProcessError(
            1, ["zk", "list"], stderr="Command failed"
        )

        # When & Then: RuntimeErrorが発生すること
        with pytest.raises(RuntimeError, match="Error: Command failed"):
            client.get_notes()

    def test_get_notes_with_unparseable_lines(
        self, client: ZkClient, mocker: MockerFixture
    ) -> None:
        # Given: パースできない行を含む出力
        mock_run = mocker.patch("subprocess.run")
        mock_result = Mock()
        mock_result.stdout = (
            "/valid.md|Valid Note|tag\ninvalid_line\n/valid2.md|Valid Note 2|"
        )
        mock_run.return_value = mock_result

        # When: ノート一覧を取得する
        notes = client.get_notes()

        # Then: パースできる行のみが返されること
        assert len(notes) == 2
        assert notes[0].title == "Valid Note"
        assert notes[1].title == "Valid Note 2"
