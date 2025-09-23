from pathlib import Path
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from zk_utils.application._common.note import Note as AppNote
from zk_utils.application.notes.get_last_modified_note import (
    GetLastModifiedNoteInput,
    GetLastModifiedNoteOutput,
    GetLastModifiedNoteService,
)
from zk_utils.domain.models.notes.if_note_repository import IFNoteRepository
from zk_utils.domain.models.notes.note import Note as DomainNote


class TestGetLastModifiedNoteService:
    """GetLastModifiedNoteServiceの単体テスト"""

    @pytest.fixture
    def mock_repository(self, mocker: MockerFixture) -> Mock:
        return mocker.create_autospec(IFNoteRepository)

    @pytest.fixture
    def service(self, mock_repository: Mock) -> GetLastModifiedNoteService:
        return GetLastModifiedNoteService(repository=mock_repository)

    def test_handle_success(
        self, service: GetLastModifiedNoteService, mock_repository: Mock
    ) -> None:
        # Given: リポジトリから最新変更ノートが取得できる
        domain_note = DomainNote(
            title="Latest Note",
            path=Path("/path/latest.md"),
            tags=["recent", "updated"],
        )
        mock_repository.find_last_modified_note.return_value = domain_note
        input_data = GetLastModifiedNoteInput()

        # When: サービスを実行する
        result = service.handle(input_data)

        # Then: リポジトリメソッドが呼ばれ、適切な出力が返されること
        mock_repository.find_last_modified_note.assert_called_once()
        assert isinstance(result, GetLastModifiedNoteOutput)
        assert result.note.title == domain_note.title
        assert result.note.path == domain_note.path
        assert result.note.tags == domain_note.tags

    def test_handle_repository_exception_should_propagate(
        self, service: GetLastModifiedNoteService, mock_repository: Mock
    ) -> None:
        # Given: リポジトリで例外が発生する
        mock_repository.find_last_modified_note.side_effect = ValueError(
            "Last modified note not found"
        )
        input_data = GetLastModifiedNoteInput()

        # When & Then: ValueErrorが伝播すること
        with pytest.raises(ValueError, match="Last modified note not found"):
            service.handle(input_data)

        mock_repository.find_last_modified_note.assert_called_once()

    def test_handle_with_empty_input(
        self, service: GetLastModifiedNoteService, mock_repository: Mock
    ) -> None:
        # Given: 空の入力データとリポジトリからの正常なレスポンス
        domain_note = DomainNote(
            title="Default Note",
            path=Path("/default.md"),
            tags=[],
        )
        mock_repository.find_last_modified_note.return_value = domain_note
        input_data = GetLastModifiedNoteInput()

        # When: サービスを実行する
        result = service.handle(input_data)

        # Then: 正常に処理されること
        assert isinstance(result, GetLastModifiedNoteOutput)
        assert result.note.title == "Default Note"
        assert result.note.path == Path("/default.md")
        assert result.note.tags == []


class TestGetLastModifiedNoteInput:
    """GetLastModifiedNoteInputの単体テスト"""

    def test_create_empty_input(self) -> None:
        # Given: パラメータなし

        # When: インスタンスを作成する
        input_data = GetLastModifiedNoteInput()

        # Then: 正常にインスタンスが作成されること
        assert isinstance(input_data, GetLastModifiedNoteInput)


class TestGetLastModifiedNoteOutput:
    """GetLastModifiedNoteOutputの単体テスト"""

    def test_create_output_with_note(self) -> None:
        # Given: ノート情報
        note = AppNote(
            title="Test Note",
            path=Path("/test.md"),
            tags=["tag1", "tag2"],
        )

        # When: アウトプットインスタンスを作成する
        output = GetLastModifiedNoteOutput(note=note)

        # Then: 正常にインスタンスが作成されること
        assert isinstance(output, GetLastModifiedNoteOutput)
        assert output.note == note
        assert output.note.title == "Test Note"
        assert output.note.path == Path("/test.md")
        assert output.note.tags == ["tag1", "tag2"]
