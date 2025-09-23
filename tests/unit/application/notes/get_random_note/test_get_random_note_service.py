from pathlib import Path
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from zk_utils.application._common.note import Note as AppNote
from zk_utils.application.notes.get_random_note import (
    GetRandomNoteInput,
    GetRandomNoteOutput,
    GetRandomNoteService,
)
from zk_utils.domain.models.notes.if_note_repository import IFNoteRepository
from zk_utils.domain.models.notes.note import Note as DomainNote


class TestGetRandomNoteService:
    """GetRandomNoteServiceの単体テスト"""

    @pytest.fixture
    def mock_repository(self, mocker: MockerFixture) -> Mock:
        return mocker.create_autospec(IFNoteRepository)

    @pytest.fixture
    def service(self, mock_repository: Mock) -> GetRandomNoteService:
        return GetRandomNoteService(repository=mock_repository)

    def test_handle_success(
        self, service: GetRandomNoteService, mock_repository: Mock
    ) -> None:
        # Given: リポジトリからランダムノートが取得できる
        domain_note = DomainNote(
            title="Random Note",
            path=Path("/path/random.md"),
            tags=["random", "test"],
        )
        mock_repository.find_random_note.return_value = domain_note
        input_data = GetRandomNoteInput()

        # When: サービスを実行する
        result = service.handle(input_data)

        # Then: リポジトリメソッドが呼ばれ、適切な出力が返されること
        mock_repository.find_random_note.assert_called_once()
        assert isinstance(result, GetRandomNoteOutput)
        assert result.note.title == domain_note.title
        assert result.note.path == domain_note.path
        assert result.note.tags == domain_note.tags

    def test_handle_repository_exception_should_propagate(
        self, service: GetRandomNoteService, mock_repository: Mock
    ) -> None:
        # Given: リポジトリで例外が発生する
        mock_repository.find_random_note.side_effect = ValueError(
            "Last modified note not found"
        )
        input_data = GetRandomNoteInput()

        # When & Then: ValueErrorが伝播すること
        with pytest.raises(ValueError, match="Last modified note not found"):
            service.handle(input_data)

        mock_repository.find_random_note.assert_called_once()

    def test_handle_with_empty_input(
        self, service: GetRandomNoteService, mock_repository: Mock
    ) -> None:
        # Given: 空の入力データとリポジトリからの正常なレスポンス
        domain_note = DomainNote(
            title="Default Random Note",
            path=Path("/default.md"),
            tags=[],
        )
        mock_repository.find_random_note.return_value = domain_note
        input_data = GetRandomNoteInput()

        # When: サービスを実行する
        result = service.handle(input_data)

        # Then: 正常に処理されること
        assert isinstance(result, GetRandomNoteOutput)
        assert result.note.title == "Default Random Note"
        assert result.note.path == Path("/default.md")
        assert result.note.tags == []

    def test_handle_with_japanese_title(
        self, service: GetRandomNoteService, mock_repository: Mock
    ) -> None:
        # Given: 日本語タイトルのノートが返される
        domain_note = DomainNote(
            title="ランダムノート",
            path=Path("/日本語/ノート.md"),
            tags=["日本語", "テスト"],
        )
        mock_repository.find_random_note.return_value = domain_note
        input_data = GetRandomNoteInput()

        # When: サービスを実行する
        result = service.handle(input_data)

        # Then: 日本語が正しく処理されること
        assert result.note.title == "ランダムノート"
        assert result.note.path == Path("/日本語/ノート.md")
        assert result.note.tags == ["日本語", "テスト"]

    def test_handle_with_special_characters(
        self, service: GetRandomNoteService, mock_repository: Mock
    ) -> None:
        # Given: 特殊文字を含むノートが返される
        domain_note = DomainNote(
            title="Special @#$% Note",
            path=Path("/special/note.md"),
            tags=["special", "chars@#$%"],
        )
        mock_repository.find_random_note.return_value = domain_note
        input_data = GetRandomNoteInput()

        # When: サービスを実行する
        result = service.handle(input_data)

        # Then: 特殊文字が正しく処理されること
        assert result.note.title == "Special @#$% Note"
        assert result.note.path == Path("/special/note.md")
        assert result.note.tags == ["special", "chars@#$%"]


class TestGetRandomNoteInput:
    """GetRandomNoteInputの単体テスト"""

    def test_create_empty_input(self) -> None:
        # Given: パラメータなし

        # When: インスタンスを作成する
        input_data = GetRandomNoteInput()

        # Then: 正常にインスタンスが作成されること
        assert isinstance(input_data, GetRandomNoteInput)


class TestGetRandomNoteOutput:
    """GetRandomNoteOutputの単体テスト"""

    def test_create_output_with_note(self) -> None:
        # Given: ノート情報
        note = AppNote(
            title="Test Random Note",
            path=Path("/test.md"),
            tags=["tag1", "tag2"],
        )

        # When: アウトプットインスタンスを作成する
        output = GetRandomNoteOutput(note=note)

        # Then: 正常にインスタンスが作成されること
        assert isinstance(output, GetRandomNoteOutput)
        assert output.note == note
        assert output.note.title == "Test Random Note"
        assert output.note.path == Path("/test.md")
        assert output.note.tags == ["tag1", "tag2"]

    def test_create_output_with_empty_tags(self) -> None:
        # Given: タグなしのノート情報
        note = AppNote(
            title="No Tags Note",
            path=Path("/notags.md"),
            tags=[],
        )

        # When: アウトプットインスタンスを作成する
        output = GetRandomNoteOutput(note=note)

        # Then: 正常にインスタンスが作成されること
        assert isinstance(output, GetRandomNoteOutput)
        assert output.note.tags == []

    def test_create_output_with_japanese_note(self) -> None:
        # Given: 日本語のノート情報
        note = AppNote(
            title="日本語ノート",
            path=Path("/日本語.md"),
            tags=["日本語", "テスト"],
        )

        # When: アウトプットインスタンスを作成する
        output = GetRandomNoteOutput(note=note)

        # Then: 日本語が正しく処理されること
        assert output.note.title == "日本語ノート"
        assert output.note.path == Path("/日本語.md")
        assert output.note.tags == ["日本語", "テスト"]
