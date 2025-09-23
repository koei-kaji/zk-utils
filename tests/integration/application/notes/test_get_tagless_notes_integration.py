from pathlib import Path
from unittest.mock import Mock

import pytest
from injector import Injector

from zk_utils.application.notes.get_tagless_notes import (
    GetTaglessNotesInput,
    GetTaglessNotesService,
)


@pytest.mark.integration
class TestGetTaglessNotesIntegration:
    """GetTaglessNotesServiceとZkClientの結合テスト"""

    def test_get_tagless_notes_should_return_tagless_notes_list(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
    ) -> None:
        # Given: タグなしノートの出力をモック
        mock_subprocess_run.return_value.stdout = (
            "/path/to/note1.md|タグなしノート1|\n"
            "/path/to/note2.md|Note without tags|\n"
            "/path/to/note3.md|無タグノート|\n"
        )
        service = test_injector.get(GetTaglessNotesService)
        input_data = GetTaglessNotesInput()

        # When: タグなしノートを取得
        result = service.handle(input_data)

        # Then: 期待する結果が返されること
        assert len(result.notes) == 3
        assert result.notes[0].title == "タグなしノート1"
        assert result.notes[0].path == Path("/path/to/note1.md")
        assert result.notes[0].tags == []
        assert result.notes[1].title == "Note without tags"
        assert result.notes[1].path == Path("/path/to/note2.md")
        assert result.notes[1].tags == []
        assert result.notes[2].title == "無タグノート"
        assert result.notes[2].path == Path("/path/to/note3.md")
        assert result.notes[2].tags == []

    def test_get_tagless_notes_with_empty_result_should_return_empty_list(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
    ) -> None:
        # Given: 空の結果を返すzkコマンド
        mock_subprocess_run.return_value.stdout = ""
        service = test_injector.get(GetTaglessNotesService)
        input_data = GetTaglessNotesInput()

        # When: タグなしノートを取得
        result = service.handle(input_data)

        # Then: 空のリストが返されること
        assert len(result.notes) == 0

    def test_get_tagless_notes_with_single_note_should_return_single_note(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
    ) -> None:
        # Given: 単一のタグなしノート出力
        mock_subprocess_run.return_value.stdout = "/single.md|単一のタグなしノート|"
        service = test_injector.get(GetTaglessNotesService)
        input_data = GetTaglessNotesInput()

        # When: タグなしノートを取得
        result = service.handle(input_data)

        # Then: 単一のノートが返されること
        assert len(result.notes) == 1
        assert result.notes[0].title == "単一のタグなしノート"
        assert result.notes[0].path == Path("/single.md")
        assert result.notes[0].tags == []

    def test_get_tagless_notes_with_special_characters_should_handle_correctly(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
    ) -> None:
        # Given: 特殊文字を含むタグなしノート出力
        mock_subprocess_run.return_value.stdout = (
            "/special.md|特殊文字 @#$% を含むノート|\n"
            "/emoji.md|📝 Emoji Note 🎯|\n"
            "/unicode.md|ユニコード文字 αβγ δεζ|\n"
        )
        service = test_injector.get(GetTaglessNotesService)
        input_data = GetTaglessNotesInput()

        # When: タグなしノートを取得
        result = service.handle(input_data)

        # Then: 特殊文字が正しく処理されること
        assert len(result.notes) == 3
        assert result.notes[0].title == "特殊文字 @#$% を含むノート"
        assert result.notes[1].title == "📝 Emoji Note 🎯"
        assert result.notes[2].title == "ユニコード文字 αβγ δεζ"

    def test_get_tagless_notes_with_zk_command_error_should_raise_runtime_error(
        self,
        test_injector: Injector,
        mock_failed_subprocess: Mock,
    ) -> None:
        # Given: zkコマンドがエラーを返す
        service = test_injector.get(GetTaglessNotesService)
        input_data = GetTaglessNotesInput()

        # When & Then: RuntimeErrorが発生すること
        with pytest.raises(RuntimeError, match="Error: zk command failed"):
            service.handle(input_data)

    def test_get_tagless_notes_with_malformed_output_should_skip_invalid_lines(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
    ) -> None:
        # Given: 不正な形式の行を含む出力
        malformed_output = (
            "/path/to/note1.md|有効なタグなしノート1|\n"
            "invalid_line_without_pipes\n"
            "/path/to/note2.md|有効なタグなしノート2|\n"
            "another|invalid|format|line|with|too|many|pipes\n"
            "/path/to/note3.md|有効なタグなしノート3|\n"
        )
        mock_subprocess_run.return_value.stdout = malformed_output
        service = test_injector.get(GetTaglessNotesService)
        input_data = GetTaglessNotesInput()

        # When: タグなしノートを取得
        result = service.handle(input_data)

        # Then: 有効な行のみが処理されること
        assert len(result.notes) == 4
        assert result.notes[0].title == "有効なタグなしノート1"
        assert result.notes[1].title == "有効なタグなしノート2"
        assert result.notes[2].title == "invalid|format|line|with|too|many"
        assert result.notes[3].title == "有効なタグなしノート3"
