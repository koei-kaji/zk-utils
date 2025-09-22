from pathlib import Path

import pytest

from zk_utils.infrastructure.zk.zk_client import ZkClient


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
