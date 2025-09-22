from pathlib import Path
from unittest.mock import Mock

import pytest
from injector import Injector

from zk_utils.application.notes.get_notes import GetNotesInput, GetNotesService


@pytest.mark.integration
class TestGetNotesIntegration:
    """GetNotesServiceとZkClientの結合テスト"""

    def test_get_notes_with_basic_parameters_should_return_notes_list(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        sample_zk_notes_output: str,
    ) -> None:
        # Given: 正常なzk出力をモック
        mock_subprocess_run.return_value.stdout = sample_zk_notes_output
        service = test_injector.get(GetNotesService)
        input_data = GetNotesInput(
            page=1,
            per_page=10,
            title_patterns=[],
            search_patterns=[],
            tags=[],
        )

        # When: ノート一覧を取得
        result = service.handle(input_data)

        # Then: 期待する結果が返されること
        assert result.pagination.page == 1
        assert result.pagination.per_page == 10
        assert result.pagination.total == 4
        assert result.pagination.total_pages == 1
        assert len(result.notes) == 4
        assert result.notes[0].title == "テストノート1"
        assert result.notes[0].path == Path("/path/to/note1.md")
        assert result.notes[0].tags == ["tag1", "tag2"]
        # @with_indexデコレータにより_execute_index()が先に呼ばれるため、計2回の呼び出し
        assert mock_subprocess_run.call_count == 2

    def test_get_notes_with_title_filter_should_apply_title_search(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        sample_zk_notes_output: str,
    ) -> None:
        # Given: タイトルフィルタ付きのリクエスト
        mock_subprocess_run.return_value.stdout = sample_zk_notes_output
        service = test_injector.get(GetNotesService)
        input_data = GetNotesInput(
            title_patterns=["テスト", "Note"],
            title_match_mode="AND",
            search_patterns=[],
            tags=[],
        )

        # When: ノート一覧を取得
        result = service.handle(input_data)

        # Then: zkコマンドが正しい引数で呼ばれること
        call_args = mock_subprocess_run.call_args[0][0]
        assert "--match" in call_args
        assert "title: テスト AND title: Note" in call_args
        assert len(result.notes) == 4

    def test_get_notes_with_search_patterns_should_apply_full_text_search(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        sample_zk_notes_output: str,
    ) -> None:
        # Given: 検索パターン付きのリクエスト
        mock_subprocess_run.return_value.stdout = sample_zk_notes_output
        service = test_injector.get(GetNotesService)
        input_data = GetNotesInput(
            title_patterns=[],
            search_patterns=["テスト", "内容"],
            search_match_mode="OR",
            tags=[],
        )

        # When: ノート一覧を取得
        result = service.handle(input_data)

        # Then: zkコマンドが正しい引数で呼ばれること
        call_args = mock_subprocess_run.call_args[0][0]
        assert "--match" in call_args
        assert "テスト OR 内容" in call_args
        assert len(result.notes) == 4

    def test_get_notes_with_tags_filter_should_apply_tag_search(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        sample_zk_notes_output: str,
    ) -> None:
        # Given: タグフィルタ付きのリクエスト
        mock_subprocess_run.return_value.stdout = sample_zk_notes_output
        service = test_injector.get(GetNotesService)
        input_data = GetNotesInput(
            title_patterns=[],
            search_patterns=[],
            tags=["tag1", "tag2"],
            tags_match_mode="AND",
        )

        # When: ノート一覧を取得
        result = service.handle(input_data)

        # Then: zkコマンドが正しい引数で呼ばれること
        call_args = mock_subprocess_run.call_args[0][0]
        assert "--tag" in call_args
        assert "tag1, tag2" in call_args
        assert len(result.notes) == 4

    def test_get_notes_with_pagination_should_return_paginated_results(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        large_notes_output: str,
    ) -> None:
        # Given: 大量のノート出力と2ページ目のリクエスト
        mock_subprocess_run.return_value.stdout = large_notes_output
        service = test_injector.get(GetNotesService)
        input_data = GetNotesInput(
            page=2,
            per_page=5,
            title_patterns=[],
            search_patterns=[],
            tags=[],
        )

        # When: ノート一覧を取得
        result = service.handle(input_data)

        # Then: 正しくページネーションされること
        assert result.pagination.page == 2
        assert result.pagination.per_page == 5
        assert result.pagination.total == 100
        assert result.pagination.total_pages == 20
        assert result.pagination.has_prev is True
        assert result.pagination.has_next is True
        assert len(result.notes) == 5
        assert result.notes[0].title == "ノート5"

    def test_get_notes_with_empty_results_should_return_empty_list(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        sample_zk_empty_notes_output: str,
    ) -> None:
        # Given: 空の結果を返すzkコマンド
        mock_subprocess_run.return_value.stdout = sample_zk_empty_notes_output
        service = test_injector.get(GetNotesService)
        input_data = GetNotesInput(title_patterns=[], search_patterns=[], tags=[])

        # When: ノート一覧を取得
        result = service.handle(input_data)

        # Then: 空のリストが返されること
        assert result.pagination.total == 0
        assert result.pagination.total_pages == 0
        assert len(result.notes) == 0

    def test_get_notes_with_special_characters_should_handle_correctly(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        special_character_notes_output: str,
    ) -> None:
        # Given: 特殊文字を含むノート出力
        mock_subprocess_run.return_value.stdout = special_character_notes_output
        service = test_injector.get(GetNotesService)
        input_data = GetNotesInput(title_patterns=[], search_patterns=[], tags=[])

        # When: ノート一覧を取得
        result = service.handle(input_data)

        # Then: 特殊文字が正しく処理されること
        assert len(result.notes) == 3
        assert result.notes[0].title == "タイトル with 特殊文字 @#$%"
        assert result.notes[1].title == "📝 Emoji Note 🎯"
        assert result.notes[2].title == "ユニコード文字 αβγ δεζ"

    def test_get_notes_with_zk_command_error_should_raise_runtime_error(
        self,
        test_injector: Injector,
        mock_failed_subprocess: Mock,
    ) -> None:
        # Given: zkコマンドがエラーを返す
        service = test_injector.get(GetNotesService)
        input_data = GetNotesInput(title_patterns=[], search_patterns=[], tags=[])

        # When & Then: RuntimeErrorが発生すること
        with pytest.raises(RuntimeError, match="Error: zk command failed"):
            service.handle(input_data)

    def test_get_notes_with_malformed_output_should_skip_invalid_lines(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
    ) -> None:
        # Given: 不正な形式の行を含む出力
        malformed_output = (
            "/path/to/note1.md|テストノート1|tag1,tag2\n"
            "invalid_line_without_pipes\n"
            "/path/to/note2.md|テストノート2|tag3\n"
            "path|this|is|part|of|title|tag\n"
        )
        mock_subprocess_run.return_value.stdout = malformed_output
        service = test_injector.get(GetNotesService)
        input_data = GetNotesInput(title_patterns=[], search_patterns=[], tags=[])

        # When: ノート一覧を取得
        result = service.handle(input_data)

        # Then: 有効な行のみが処理されること
        assert len(result.notes) == 3
        assert result.notes[0].title == "テストノート1"
        assert result.notes[1].title == "テストノート2"
        assert result.notes[2].title == "this|is|part|of|title"


@pytest.mark.integration
class TestGetNotesWithMultipleFilters:
    """複数フィルタの組み合わせテスト"""

    def test_get_notes_with_all_filters_should_combine_conditions(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        sample_zk_notes_output: str,
    ) -> None:
        # Given: 全種類のフィルタを含むリクエスト
        mock_subprocess_run.return_value.stdout = sample_zk_notes_output
        service = test_injector.get(GetNotesService)
        input_data = GetNotesInput(
            title_patterns=["テスト"],
            search_patterns=["内容"],
            tags=["tag1"],
        )

        # When: ノート一覧を取得
        result = service.handle(input_data)

        # Then: 全ての条件がzkコマンドに渡されること
        call_args = mock_subprocess_run.call_args[0][0]
        assert "--match" in call_args
        assert "--tag" in call_args
        assert len(result.notes) == 4
