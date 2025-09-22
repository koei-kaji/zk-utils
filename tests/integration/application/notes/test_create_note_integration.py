import subprocess
from pathlib import Path
from unittest.mock import Mock

import pytest
from injector import Injector

from zk_utils.application.notes.create_note import CreateNoteInput, CreateNoteService


@pytest.mark.integration
class TestCreateNoteIntegration:
    """CreateNoteServiceとZkNoteRepositoryの結合テスト"""

    def test_create_note_with_valid_parameters_should_return_created_note(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        sample_zk_create_note_output: str,
        sample_note_title: str,
        sample_note_path: Path,
    ) -> None:
        # Given: 正常なzk new出力をモック
        mock_subprocess_run.return_value.stdout = sample_zk_create_note_output
        service = test_injector.get(CreateNoteService)
        input_data = CreateNoteInput(
            title=sample_note_title,
            path=sample_note_path,
        )

        # When: ノートを作成
        result = service.handle(input_data)

        # Then: 作成されたノート情報が返されること
        assert result.note.title == sample_note_title
        assert result.note.path == Path(sample_zk_create_note_output)
        assert result.note.tags == []

        # zkコマンドが正しい引数で呼ばれること
        call_args = mock_subprocess_run.call_args[0][0]
        assert "zk" in call_args
        assert "new" in call_args
        assert "--print-path" in call_args
        assert "--title" in call_args
        assert sample_note_title in call_args
        assert str(sample_note_path) in call_args

    def test_create_note_with_japanese_title_should_handle_correctly(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        sample_zk_create_note_output: str,
        sample_note_path: Path,
    ) -> None:
        # Given: 日本語タイトルのノート作成リクエスト
        japanese_title = "日本語のタイトル 📝"
        mock_subprocess_run.return_value.stdout = sample_zk_create_note_output
        service = test_injector.get(CreateNoteService)
        input_data = CreateNoteInput(
            title=japanese_title,
            path=sample_note_path,
        )

        # When: ノートを作成
        result = service.handle(input_data)

        # Then: 日本語タイトルが正しく処理されること
        assert result.note.title == japanese_title
        assert "日本語のタイトル" in result.note.title
        assert "📝" in result.note.title

        # zkコマンドに日本語タイトルが渡されること
        call_args = mock_subprocess_run.call_args[0][0]
        assert japanese_title in call_args

    def test_create_note_with_special_characters_in_title_should_handle_correctly(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        sample_zk_create_note_output: str,
        sample_note_path: Path,
    ) -> None:
        # Given: 特殊文字を含むタイトル
        special_title = "Title with @#$%^&*()_+-=[]{}|;:,.<>?"
        mock_subprocess_run.return_value.stdout = sample_zk_create_note_output
        service = test_injector.get(CreateNoteService)
        input_data = CreateNoteInput(
            title=special_title,
            path=sample_note_path,
        )

        # When: ノートを作成
        result = service.handle(input_data)

        # Then: 特殊文字が正しく処理されること
        assert result.note.title == special_title

    def test_create_note_with_empty_title_should_handle_correctly(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        sample_zk_create_note_output: str,
        sample_note_path: Path,
    ) -> None:
        # Given: 空のタイトル
        empty_title = ""
        mock_subprocess_run.return_value.stdout = sample_zk_create_note_output
        service = test_injector.get(CreateNoteService)
        input_data = CreateNoteInput(
            title=empty_title,
            path=sample_note_path,
        )

        # When: ノートを作成
        result = service.handle(input_data)

        # Then: 空のタイトルが処理されること
        assert result.note.title == empty_title

    def test_create_note_with_long_title_should_handle_correctly(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        sample_zk_create_note_output: str,
        sample_note_path: Path,
    ) -> None:
        # Given: 長いタイトル
        long_title = "This is a very long title " * 10
        mock_subprocess_run.return_value.stdout = sample_zk_create_note_output
        service = test_injector.get(CreateNoteService)
        input_data = CreateNoteInput(
            title=long_title,
            path=sample_note_path,
        )

        # When: ノートを作成
        result = service.handle(input_data)

        # Then: 長いタイトルが正しく処理されること
        assert result.note.title == long_title
        assert len(result.note.title) > 200

    def test_create_note_with_complex_path_should_handle_correctly(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        sample_zk_create_note_output: str,
        sample_note_title: str,
    ) -> None:
        # Given: 複雑なパス構造
        complex_path = Path("folder1/subfolder/deep/nested/note.md")
        mock_subprocess_run.return_value.stdout = sample_zk_create_note_output
        service = test_injector.get(CreateNoteService)
        input_data = CreateNoteInput(
            title=sample_note_title,
            path=complex_path,
        )

        # When: ノートを作成
        result = service.handle(input_data)

        # Then: 複雑なパスが正しく処理されること
        assert result.note.path == Path(sample_zk_create_note_output)

        # zkコマンドに複雑なパスが渡されること
        call_args = mock_subprocess_run.call_args[0][0]
        assert str(complex_path) in call_args

    def test_create_note_with_zk_command_error_should_raise_runtime_error(
        self,
        test_injector: Injector,
        mock_failed_subprocess: Mock,
        sample_note_title: str,
        sample_note_path: Path,
    ) -> None:
        # Given: zkコマンドがエラーを返す
        service = test_injector.get(CreateNoteService)
        input_data = CreateNoteInput(
            title=sample_note_title,
            path=sample_note_path,
        )

        # When & Then: RuntimeErrorが発生すること
        with pytest.raises(RuntimeError, match="Error: zk command failed"):
            service.handle(input_data)

    def test_create_note_with_permission_error_should_raise_runtime_error(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        sample_note_title: str,
        sample_note_path: Path,
    ) -> None:
        # Given: 権限エラーでzkコマンドが失敗
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=["zk", "new"], stderr="Error: permission denied"
        )
        service = test_injector.get(CreateNoteService)
        input_data = CreateNoteInput(
            title=sample_note_title,
            path=sample_note_path,
        )

        # When & Then: RuntimeErrorが発生すること
        with pytest.raises(RuntimeError, match="Error: permission denied"):
            service.handle(input_data)

    def test_create_note_with_invalid_zk_directory_should_raise_runtime_error(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        sample_note_title: str,
        sample_note_path: Path,
    ) -> None:
        # Given: 無効なzkディレクトリでエラー
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(
            returncode=1, cmd=["zk", "new"], stderr="Error: not a zk directory"
        )
        service = test_injector.get(CreateNoteService)
        input_data = CreateNoteInput(
            title=sample_note_title,
            path=sample_note_path,
        )

        # When & Then: RuntimeErrorが発生すること
        with pytest.raises(RuntimeError, match="Error: not a zk directory"):
            service.handle(input_data)


@pytest.mark.integration
class TestCreateNoteCommandGeneration:
    """CreateNoteServiceのzkコマンド生成テスト"""

    def test_create_note_should_generate_correct_zk_command(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        sample_zk_create_note_output: str,
    ) -> None:
        # Given: ノート作成パラメータ
        title = "Test Note"
        path = Path("test/note.md")
        mock_subprocess_run.return_value.stdout = sample_zk_create_note_output
        service = test_injector.get(CreateNoteService)
        input_data = CreateNoteInput(title=title, path=path)

        # When: ノートを作成
        service.handle(input_data)

        # Then: 正しいzkコマンドが生成されること
        call_args = mock_subprocess_run.call_args[0][0]
        expected_command = ["zk", "new", "--print-path", "--title", title, str(path)]
        assert call_args == expected_command

    def test_create_note_with_spaces_in_title_should_quote_correctly(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        sample_zk_create_note_output: str,
    ) -> None:
        # Given: スペースを含むタイトル
        title_with_spaces = "Note with spaces in title"
        path = Path("note.md")
        mock_subprocess_run.return_value.stdout = sample_zk_create_note_output
        service = test_injector.get(CreateNoteService)
        input_data = CreateNoteInput(title=title_with_spaces, path=path)

        # When: ノートを作成
        service.handle(input_data)

        # Then: タイトルが正しく渡されること
        call_args = mock_subprocess_run.call_args[0][0]
        assert title_with_spaces in call_args
