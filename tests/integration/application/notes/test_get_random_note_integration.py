from pathlib import Path
from unittest.mock import Mock

import pytest
from injector import Injector

from zk_utils.application.notes.get_random_note import (
    GetRandomNoteInput,
    GetRandomNoteService,
)


@pytest.mark.integration
class TestGetRandomNoteIntegration:
    """GetRandomNoteServiceとZkClientの結合テスト"""

    def test_get_random_note_success_should_return_note(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
    ) -> None:
        # Given: ランダムノートのzk出力をモック
        mock_subprocess_run.return_value.stdout = (
            "/path/to/random.md|ランダムノート|random,test"
        )
        mock_subprocess_run.return_value.returncode = 0
        service = test_injector.get(GetRandomNoteService)
        input_data = GetRandomNoteInput()

        # When: ランダムノートを取得
        result = service.handle(input_data)

        # Then: 期待する結果が返されること
        assert result.note.title == "ランダムノート"
        assert result.note.path == Path("/path/to/random.md")
        assert result.note.tags == ["random", "test"]

    def test_get_random_note_no_results_should_raise_error(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
    ) -> None:
        # Given: 空の結果を返すzkコマンド
        mock_subprocess_run.return_value.stdout = ""
        mock_subprocess_run.return_value.returncode = 0
        service = test_injector.get(GetRandomNoteService)
        input_data = GetRandomNoteInput()

        # When & Then: ValueErrorが発生すること
        with pytest.raises(ValueError, match="Last modified note not found"):
            service.handle(input_data)

    def test_get_random_note_with_japanese_title_should_handle_correctly(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
    ) -> None:
        # Given: 日本語タイトルのノート出力
        mock_subprocess_run.return_value.stdout = (
            "/日本語/パス.md|日本語タイトルのノート|日本語タグ,テスト"
        )
        mock_subprocess_run.return_value.returncode = 0
        service = test_injector.get(GetRandomNoteService)
        input_data = GetRandomNoteInput()

        # When: ランダムノートを取得
        result = service.handle(input_data)

        # Then: 日本語が正しく処理されること
        assert result.note.title == "日本語タイトルのノート"
        assert result.note.path == Path("/日本語/パス.md")
        assert result.note.tags == ["日本語タグ", "テスト"]

    def test_get_random_note_with_empty_tags_should_return_empty_list(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
    ) -> None:
        # Given: タグなしのノート出力
        mock_subprocess_run.return_value.stdout = "/path/note.md|タグなしノート|"
        mock_subprocess_run.return_value.returncode = 0
        service = test_injector.get(GetRandomNoteService)
        input_data = GetRandomNoteInput()

        # When: ランダムノートを取得
        result = service.handle(input_data)

        # Then: 空のタグリストが返されること
        assert result.note.title == "タグなしノート"
        assert result.note.path == Path("/path/note.md")
        assert result.note.tags == []

    def test_get_random_note_with_special_characters_should_handle_correctly(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
    ) -> None:
        # Given: 特殊文字を含むノート出力
        mock_subprocess_run.return_value.stdout = (
            "/path/special.md|タイトル with 特殊文字 @#$%|特殊,文字"
        )
        mock_subprocess_run.return_value.returncode = 0
        service = test_injector.get(GetRandomNoteService)
        input_data = GetRandomNoteInput()

        # When: ランダムノートを取得
        result = service.handle(input_data)

        # Then: 特殊文字が正しく処理されること
        assert result.note.title == "タイトル with 特殊文字 @#$%"
        assert result.note.path == Path("/path/special.md")
        assert result.note.tags == ["特殊", "文字"]

    def test_get_random_note_with_pipe_in_title_should_parse_correctly(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
    ) -> None:
        # Given: タイトルにパイプ文字を含むノート出力
        mock_subprocess_run.return_value.stdout = (
            "/path/pipe.md|Title with | pipe character|tag1,tag2"
        )
        mock_subprocess_run.return_value.returncode = 0
        service = test_injector.get(GetRandomNoteService)
        input_data = GetRandomNoteInput()

        # When: ランダムノートを取得
        result = service.handle(input_data)

        # Then: パイプ文字が正しく処理されること
        assert result.note.title == "Title with | pipe character"
        assert result.note.path == Path("/path/pipe.md")
        assert result.note.tags == ["tag1", "tag2"]

    def test_get_random_note_with_zk_command_error_should_raise_runtime_error(
        self,
        test_injector: Injector,
        mock_failed_subprocess: Mock,
    ) -> None:
        # Given: zkコマンドがエラーを返す
        service = test_injector.get(GetRandomNoteService)
        input_data = GetRandomNoteInput()

        # When & Then: RuntimeErrorが発生すること
        with pytest.raises(RuntimeError, match="Error: zk command failed"):
            service.handle(input_data)

    def test_get_random_note_with_malformed_output_should_raise_error(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
    ) -> None:
        # Given: 不正な形式の出力
        mock_subprocess_run.return_value.stdout = "invalid_format_without_pipes"
        mock_subprocess_run.return_value.returncode = 0
        service = test_injector.get(GetRandomNoteService)
        input_data = GetRandomNoteInput()

        # When & Then: ValueErrorが発生すること
        with pytest.raises(ValueError, match="Last modified note not found"):
            service.handle(input_data)
