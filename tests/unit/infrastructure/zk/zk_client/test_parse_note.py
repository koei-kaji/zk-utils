from pathlib import Path

import pytest

from zk_utils.infrastructure.zk.zk_client import ZkClient


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
