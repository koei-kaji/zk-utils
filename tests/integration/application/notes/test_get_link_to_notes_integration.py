from pathlib import Path
from unittest.mock import Mock

import pytest
from injector import Injector

from zk_utils.application.notes.get_link_to_notes import (
    GetLinkToNotesInput,
    GetLinkToNotesService,
)


@pytest.mark.integration
class TestGetLinkToNotesIntegration:
    """GetLinkToNotesServiceとZkNoteQueryServiceの結合テスト"""

    def test_get_link_to_notes_with_valid_path_should_return_linked_notes(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        sample_zk_notes_output: str,
        sample_note_path: Path,
    ) -> None:
        # Given: リンク先ノートを返すzkコマンド
        mock_subprocess_run.return_value.stdout = sample_zk_notes_output
        service = test_injector.get(GetLinkToNotesService)
        input_data = GetLinkToNotesInput(
            page=1,
            per_page=10,
            path=sample_note_path,
        )

        # When: リンク先ノートを取得
        result = service.handle(input_data)

        # Then: 期待する結果が返されること
        assert result.pagination.page == 1
        assert result.pagination.per_page == 10
        assert result.pagination.total == 4
        assert len(result.notes) == 4

        # zkコマンドが正しい引数で呼ばれること
        call_args = mock_subprocess_run.call_args[0][0]
        assert "--link-to" in call_args
        assert str(sample_note_path) in call_args

    def test_get_link_to_notes_with_pagination_should_return_paginated_results(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        large_notes_output: str,
        sample_note_path: Path,
    ) -> None:
        # Given: 大量のリンク先ノートと2ページ目のリクエスト
        mock_subprocess_run.return_value.stdout = large_notes_output
        service = test_injector.get(GetLinkToNotesService)
        input_data = GetLinkToNotesInput(
            page=2,
            per_page=10,
            path=sample_note_path,
        )

        # When: リンク先ノートを取得
        result = service.handle(input_data)

        # Then: 正しくページネーションされること
        assert result.pagination.page == 2
        assert result.pagination.per_page == 10
        assert result.pagination.total == 100
        assert result.pagination.total_pages == 10
        assert result.pagination.has_prev is True
        assert result.pagination.has_next is True
        assert len(result.notes) == 10

    def test_get_link_to_notes_with_no_links_should_return_empty_list(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        sample_zk_empty_notes_output: str,
        sample_note_path: Path,
    ) -> None:
        # Given: リンクがないノート
        mock_subprocess_run.return_value.stdout = sample_zk_empty_notes_output
        service = test_injector.get(GetLinkToNotesService)
        input_data = GetLinkToNotesInput(path=sample_note_path)

        # When: リンク先ノートを取得
        result = service.handle(input_data)

        # Then: 空のリストが返されること
        assert result.pagination.total == 0
        assert len(result.notes) == 0

    def test_get_link_to_notes_with_zk_command_error_should_raise_runtime_error(
        self,
        test_injector: Injector,
        mock_failed_subprocess: Mock,
        sample_note_path: Path,
    ) -> None:
        # Given: zkコマンドがエラーを返す
        service = test_injector.get(GetLinkToNotesService)
        input_data = GetLinkToNotesInput(path=sample_note_path)

        # When & Then: RuntimeErrorが発生すること
        with pytest.raises(RuntimeError, match="Error: zk command failed"):
            service.handle(input_data)


@pytest.mark.integration
class TestGetLinkedByNotesIntegration:
    """GetLinkedByNotesServiceとZkNoteQueryServiceの結合テスト"""

    def test_get_linked_by_notes_with_valid_path_should_return_linking_notes(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        sample_zk_notes_output: str,
        sample_note_path: Path,
    ) -> None:
        # Given: リンク元ノートを返すzkコマンド
        mock_subprocess_run.return_value.stdout = sample_zk_notes_output

        # GetLinkedByNotesServiceをインポート
        from zk_utils.application.notes.get_linked_by_notes import (
            GetLinkedByNotesInput,
            GetLinkedByNotesService,
        )

        service = test_injector.get(GetLinkedByNotesService)
        input_data = GetLinkedByNotesInput(
            page=1,
            per_page=10,
            path=sample_note_path,
        )

        # When: リンク元ノートを取得
        result = service.handle(input_data)

        # Then: 期待する結果が返されること
        assert result.pagination.page == 1
        assert result.pagination.per_page == 10
        assert result.pagination.total == 4
        assert len(result.notes) == 4

        # zkコマンドが正しい引数で呼ばれること
        call_args = mock_subprocess_run.call_args[0][0]
        assert "--linked-by" in call_args
        assert str(sample_note_path) in call_args

    def test_get_linked_by_notes_with_no_backlinks_should_return_empty_list(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        sample_zk_empty_notes_output: str,
        sample_note_path: Path,
    ) -> None:
        # Given: バックリンクがないノート
        mock_subprocess_run.return_value.stdout = sample_zk_empty_notes_output

        from zk_utils.application.notes.get_linked_by_notes import (
            GetLinkedByNotesInput,
            GetLinkedByNotesService,
        )

        service = test_injector.get(GetLinkedByNotesService)
        input_data = GetLinkedByNotesInput(path=sample_note_path)

        # When: リンク元ノートを取得
        result = service.handle(input_data)

        # Then: 空のリストが返されること
        assert result.pagination.total == 0
        assert len(result.notes) == 0


@pytest.mark.integration
class TestGetRelatedNotesIntegration:
    """GetRelatedNotesServiceとZkNoteQueryServiceの結合テスト"""

    def test_get_related_notes_with_valid_path_should_return_related_notes(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        sample_zk_notes_output: str,
        sample_note_path: Path,
    ) -> None:
        # Given: 関連ノートを返すzkコマンド
        mock_subprocess_run.return_value.stdout = sample_zk_notes_output

        from zk_utils.application.notes.get_related_notes import (
            GetRelatedNotesInput,
            GetRelatedNotesService,
        )

        service = test_injector.get(GetRelatedNotesService)
        input_data = GetRelatedNotesInput(
            page=1,
            per_page=10,
            path=sample_note_path,
        )

        # When: 関連ノートを取得
        result = service.handle(input_data)

        # Then: 期待する結果が返されること
        assert result.pagination.page == 1
        assert result.pagination.per_page == 10
        assert result.pagination.total == 4
        assert len(result.notes) == 4

        # zkコマンドが正しい引数で呼ばれること
        call_args = mock_subprocess_run.call_args[0][0]
        assert "--related" in call_args
        assert str(sample_note_path) in call_args

    def test_get_related_notes_with_pagination_should_return_paginated_results(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        large_notes_output: str,
        sample_note_path: Path,
    ) -> None:
        # Given: 大量の関連ノートと3ページ目のリクエスト
        mock_subprocess_run.return_value.stdout = large_notes_output

        from zk_utils.application.notes.get_related_notes import (
            GetRelatedNotesInput,
            GetRelatedNotesService,
        )

        service = test_injector.get(GetRelatedNotesService)
        input_data = GetRelatedNotesInput(
            page=3,
            per_page=15,
            path=sample_note_path,
        )

        # When: 関連ノートを取得
        result = service.handle(input_data)

        # Then: 正しくページネーションされること
        assert result.pagination.page == 3
        assert result.pagination.per_page == 15
        assert result.pagination.total == 100
        assert result.pagination.has_prev is True
        assert result.pagination.has_next is True
        assert len(result.notes) == 15

    def test_get_related_notes_with_no_relations_should_return_empty_list(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        sample_zk_empty_notes_output: str,
        sample_note_path: Path,
    ) -> None:
        # Given: 関連ノートがない場合
        mock_subprocess_run.return_value.stdout = sample_zk_empty_notes_output

        from zk_utils.application.notes.get_related_notes import (
            GetRelatedNotesInput,
            GetRelatedNotesService,
        )

        service = test_injector.get(GetRelatedNotesService)
        input_data = GetRelatedNotesInput(path=sample_note_path)

        # When: 関連ノートを取得
        result = service.handle(input_data)

        # Then: 空のリストが返されること
        assert result.pagination.total == 0
        assert len(result.notes) == 0

    def test_get_related_notes_with_zk_command_error_should_raise_runtime_error(
        self,
        test_injector: Injector,
        mock_failed_subprocess: Mock,
        sample_note_path: Path,
    ) -> None:
        # Given: zkコマンドがエラーを返す
        from zk_utils.application.notes.get_related_notes import (
            GetRelatedNotesInput,
            GetRelatedNotesService,
        )

        service = test_injector.get(GetRelatedNotesService)
        input_data = GetRelatedNotesInput(path=sample_note_path)

        # When & Then: RuntimeErrorが発生すること
        with pytest.raises(RuntimeError, match="Error: zk command failed"):
            service.handle(input_data)
