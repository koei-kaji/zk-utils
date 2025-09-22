import subprocess
from pathlib import Path
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from zk_utils.infrastructure.zk.zk_client import ZkClient


class TestZkClientInitialization:
    """ZkClientの初期化テスト"""

    def test_create_zk_client_with_valid_path(self) -> None:
        # Given: 有効なパス
        cwd = Path("/test/path")

        # When: ZkClientインスタンスを作成する
        client = ZkClient(cwd=cwd)

        # Then: 正常にインスタンスが作成されること
        assert client._cwd == cwd


class TestZkClientParseNote:
    """ZkClientのnoteパース機能テスト"""

    @pytest.fixture
    def client(self) -> ZkClient:
        return ZkClient(cwd=Path("/test"))

    @pytest.mark.parametrize(
        "input_string,expected_title,expected_path,expected_tags",
        [
            pytest.param(
                "/path/to/note.md|Simple Title|tag1,tag2",
                "Simple Title",
                Path("/path/to/note.md"),
                ["tag1", "tag2"],
                id="simple_note_with_tags_should_parse_correctly",
            ),
            pytest.param(
                "/path/to/note.md|Title with | pipe|tag1",
                "Title with | pipe",
                Path("/path/to/note.md"),
                ["tag1"],
                id="title_with_pipe_character_should_parse_correctly",
            ),
            pytest.param(
                "/path/to/note.md|No Tags Note|",
                "No Tags Note",
                Path("/path/to/note.md"),
                [],
                id="note_without_tags_should_parse_correctly",
            ),
            pytest.param(
                "/path/to/note.md|Single Tag|python",
                "Single Tag",
                Path("/path/to/note.md"),
                ["python"],
                id="note_with_single_tag_should_parse_correctly",
            ),
        ],
    )
    def test_parse_note_with_valid_format(
        self,
        client: ZkClient,
        input_string: str,
        expected_title: str,
        expected_path: Path,
        expected_tags: list[str],
    ) -> None:
        # Given: 有効なフォーマットの文字列

        # When: ノートをパースする
        note = client._parse_note(input_string)

        # Then: 期待される値でNoteオブジェクトが作成されること
        assert note is not None
        assert note.title == expected_title
        assert note.path == expected_path
        assert note.tags == expected_tags

    @pytest.mark.parametrize(
        "invalid_string",
        [
            pytest.param(
                "no_pipe_character", id="no_pipe_character_should_return_none"
            ),
            pytest.param("single|pipe", id="single_pipe_only_should_return_none"),
            pytest.param("", id="empty_string_should_return_none"),
        ],
    )
    def test_parse_note_with_invalid_format_should_return_none(
        self,
        client: ZkClient,
        invalid_string: str,
    ) -> None:
        # Given: 無効なフォーマットの文字列

        # When: ノートをパースする
        note = client._parse_note(invalid_string)

        # Then: Noneが返されること
        assert note is None


class TestZkClientParseTag:
    """ZkClientのタグパース機能テスト"""

    @pytest.fixture
    def client(self) -> ZkClient:
        return ZkClient(cwd=Path("/test"))

    @pytest.mark.parametrize(
        "input_string,expected_name,expected_count",
        [
            pytest.param(
                "python|5",
                "python",
                5,
                id="simple_tag_should_parse_correctly",
            ),
            pytest.param(
                "tag-with-dash|10",
                "tag-with-dash",
                10,
                id="tag_with_dash_should_parse_correctly",
            ),
            pytest.param(
                "日本語タグ|3",
                "日本語タグ",
                3,
                id="japanese_tag_should_parse_correctly",
            ),
            pytest.param(
                "tag_with_underscore|0",
                "tag_with_underscore",
                0,
                id="tag_with_zero_count_should_parse_correctly",
            ),
        ],
    )
    def test_parse_tag_with_valid_format(
        self,
        client: ZkClient,
        input_string: str,
        expected_name: str,
        expected_count: int,
    ) -> None:
        # Given: 有効なフォーマットの文字列

        # When: タグをパースする
        tag = client._parse_tag(input_string)

        # Then: 期待される値でTagオブジェクトが作成されること
        assert tag is not None
        assert tag.name == expected_name
        assert tag.note_count == expected_count

    @pytest.mark.parametrize(
        "invalid_string",
        [
            pytest.param("no_pipe", id="no_pipe_character_should_return_none"),
            pytest.param("", id="empty_string_should_return_none"),
            pytest.param("tag|not_a_number", id="invalid_number_should_raise_error"),
        ],
    )
    def test_parse_tag_with_invalid_format(
        self,
        client: ZkClient,
        invalid_string: str,
    ) -> None:
        # Given: 無効なフォーマットの文字列

        # When & Then: 適切な例外処理が行われること
        if "not_a_number" in invalid_string:
            with pytest.raises(ValueError):
                client._parse_tag(invalid_string)
        else:
            tag = client._parse_tag(invalid_string)
            assert tag is None


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

        # Then: 適切なコマンドが実行され、Noteオブジェクトのリストが返されること
        mock_run.assert_called_once_with(
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

        # Then: 条件がコマンドに追加されること
        mock_run.assert_called_once_with(
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

        # Then: 適切なコマンドが実行され、Tagオブジェクトのリストが返されること
        mock_run.assert_called_once_with(
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

        # Then: 適切なコマンドが実行され、コンテンツが返されること
        mock_run.assert_called_once_with(
            [
                "zk",
                "list",
                "--quiet",
                "--no-pager",
                "--sort",
                "title",
                "--format",
                "{{raw-content}}",
            ],
            capture_output=True,
            text=True,
            cwd=Path("/test"),
            check=True,
        )
        assert content == "# Test Note\n\nThis is test content."


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

        # Then: 適切なコマンドが実行され、Noteオブジェクトが返されること
        mock_run.assert_called_once_with(
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

        mock_run.side_effect = [note_result, content_result]

        # When: 単一ノートを取得する
        note = client.get_note(Path("/test.md"))

        # Then: note情報とコンテンツが設定されたNoteオブジェクトが返されること
        assert note is not None
        assert note.title == "Test Note"
        assert note.path == Path("/test.md")
        assert note.tags == ["python", "testing"]
        assert note.content == "# Test Note\n\nTest content here."
        assert mock_run.call_count == 2

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
