from unittest.mock import Mock

import pytest
from injector import Injector

from zk_utils.application.tags.get_tags import GetTagsInput, GetTagsService


@pytest.mark.integration
class TestGetTagsIntegration:
    """GetTagsServiceとZkTagQueryServiceの結合テスト"""

    def test_get_tags_with_valid_request_should_return_tags_list(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        sample_zk_tags_output: str,
    ) -> None:
        # Given: 正常なzk tag list出力をモック
        mock_subprocess_run.return_value.stdout = sample_zk_tags_output
        service = test_injector.get(GetTagsService)
        input_data = GetTagsInput()

        # When: タグ一覧を取得
        result = service.handle(input_data)

        # Then: 期待する結果が返されること
        assert len(result.tags) == 4
        assert result.tags[0].name == "tag1"
        assert result.tags[0].note_count == 5
        assert result.tags[1].name == "tag2"
        assert result.tags[1].note_count == 3
        assert result.tags[2].name == "tag3"
        assert result.tags[2].note_count == 1
        assert result.tags[3].name == "programming"
        assert result.tags[3].note_count == 10

    def test_get_tags_with_empty_result_should_return_empty_list(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        sample_zk_empty_tags_output: str,
    ) -> None:
        # Given: 空のタグ結果を返すzkコマンド
        mock_subprocess_run.return_value.stdout = sample_zk_empty_tags_output
        service = test_injector.get(GetTagsService)
        input_data = GetTagsInput()

        # When: タグ一覧を取得
        result = service.handle(input_data)

        # Then: 空のリストが返されること
        assert len(result.tags) == 0

    def test_get_tags_with_special_character_tags_should_handle_correctly(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
    ) -> None:
        # Given: 特殊文字を含むタグ出力
        special_tags_output = (
            "tag-with-dash|2\n"
            "tag_with_underscore|1\n"
            "tag.with.dots|3\n"
            "日本語タグ|5\n"
            "emoji🎯tag|1\n"
            "space tag|2\n"
        )
        mock_subprocess_run.return_value.stdout = special_tags_output
        service = test_injector.get(GetTagsService)
        input_data = GetTagsInput()

        # When: タグ一覧を取得
        result = service.handle(input_data)

        # Then: 特殊文字が正しく処理されること
        assert len(result.tags) == 6
        assert result.tags[0].name == "tag-with-dash"
        assert result.tags[1].name == "tag_with_underscore"
        assert result.tags[2].name == "tag.with.dots"
        assert result.tags[3].name == "日本語タグ"
        assert result.tags[4].name == "emoji🎯tag"
        assert result.tags[5].name == "space tag"

    def test_get_tags_with_large_note_counts_should_handle_correctly(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
    ) -> None:
        # Given: 大きなノート数を持つタグ
        large_count_output = (
            "popular_tag|1000\nmedium_tag|100\nsmall_tag|1\nzero_tag|0\n"
        )
        mock_subprocess_run.return_value.stdout = large_count_output
        service = test_injector.get(GetTagsService)
        input_data = GetTagsInput()

        # When: タグ一覧を取得
        result = service.handle(input_data)

        # Then: 大きなノート数が正しく処理されること
        assert len(result.tags) == 4
        assert result.tags[0].note_count == 1000
        assert result.tags[1].note_count == 100
        assert result.tags[2].note_count == 1
        assert result.tags[3].note_count == 0

    def test_get_tags_with_zk_command_error_should_raise_runtime_error(
        self,
        test_injector: Injector,
        mock_failed_subprocess: Mock,
    ) -> None:
        # Given: zkコマンドがエラーを返す
        service = test_injector.get(GetTagsService)
        input_data = GetTagsInput()

        # When & Then: RuntimeErrorが発生すること
        with pytest.raises(RuntimeError, match="Error: zk command failed"):
            service.handle(input_data)

    def test_get_tags_with_unicode_tags_should_handle_correctly(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
    ) -> None:
        # Given: Unicode文字を含むタグ
        unicode_output = "αβγδεζ|2\n中文标签|3\n한국어태그|1\nالعربية|4\n🏷️📋📝|1\n"
        mock_subprocess_run.return_value.stdout = unicode_output
        service = test_injector.get(GetTagsService)
        input_data = GetTagsInput()

        # When: タグ一覧を取得
        result = service.handle(input_data)

        # Then: Unicode文字が正しく処理されること
        assert len(result.tags) == 5
        assert result.tags[0].name == "αβγδεζ"
        assert result.tags[1].name == "中文标签"
        assert result.tags[2].name == "한국어태그"
        assert result.tags[3].name == "العربية"
        assert result.tags[4].name == "🏷️📋📝"
