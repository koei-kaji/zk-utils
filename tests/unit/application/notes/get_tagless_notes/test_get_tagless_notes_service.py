from pathlib import Path
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from zk_utils.application._common.note import Note as AppNote
from zk_utils.application.notes.get_tagless_notes import (
    GetTaglessNotesInput,
    GetTaglessNotesOutput,
    GetTaglessNotesService,
)
from zk_utils.domain.models.notes.if_note_repository import IFNoteRepository
from zk_utils.domain.models.notes.note import Note as DomainNote


class TestGetTaglessNotesService:
    """GetTaglessNotesServiceの単体テスト"""

    @pytest.fixture
    def mock_repository(self, mocker: MockerFixture) -> Mock:
        return mocker.create_autospec(IFNoteRepository)

    @pytest.fixture
    def service(self, mock_repository: Mock) -> GetTaglessNotesService:
        return GetTaglessNotesService(repository=mock_repository)

    def test_handle_with_tagless_notes_should_return_notes_list(
        self, service: GetTaglessNotesService, mock_repository: Mock
    ) -> None:
        # Given: リポジトリからタグなしノートのリストが取得できる
        domain_notes = [
            DomainNote(
                title="Note without tags 1",
                path=Path("/path/note1.md"),
                tags=[],
            ),
            DomainNote(
                title="Note without tags 2",
                path=Path("/path/note2.md"),
                tags=[],
            ),
        ]
        mock_repository.find_tagless_notes.return_value = domain_notes
        input_data = GetTaglessNotesInput()

        # When: サービスを実行する
        result = service.handle(input_data)

        # Then: リポジトリメソッドが呼ばれ、適切な出力が返されること
        mock_repository.find_tagless_notes.assert_called_once()
        assert isinstance(result, GetTaglessNotesOutput)
        assert len(result.notes) == 2
        assert result.notes[0].title == "Note without tags 1"
        assert result.notes[0].path == Path("/path/note1.md")
        assert result.notes[0].tags == []
        assert result.notes[1].title == "Note without tags 2"
        assert result.notes[1].path == Path("/path/note2.md")
        assert result.notes[1].tags == []

    def test_handle_with_empty_result_should_return_empty_list(
        self, service: GetTaglessNotesService, mock_repository: Mock
    ) -> None:
        # Given: リポジトリから空のリストが返される
        mock_repository.find_tagless_notes.return_value = []
        input_data = GetTaglessNotesInput()

        # When: サービスを実行する
        result = service.handle(input_data)

        # Then: 空のリストが返されること
        mock_repository.find_tagless_notes.assert_called_once()
        assert isinstance(result, GetTaglessNotesOutput)
        assert len(result.notes) == 0

    def test_handle_repository_exception_should_propagate(
        self, service: GetTaglessNotesService, mock_repository: Mock
    ) -> None:
        # Given: リポジトリで例外が発生する
        mock_repository.find_tagless_notes.side_effect = RuntimeError(
            "Failed to get tagless notes"
        )
        input_data = GetTaglessNotesInput()

        # When & Then: RuntimeErrorが伝播すること
        with pytest.raises(RuntimeError, match="Failed to get tagless notes"):
            service.handle(input_data)

        mock_repository.find_tagless_notes.assert_called_once()

    def test_handle_with_single_tagless_note_should_return_single_note(
        self, service: GetTaglessNotesService, mock_repository: Mock
    ) -> None:
        # Given: 単一のタグなしノートがリポジトリから取得できる
        domain_note = DomainNote(
            title="Single tagless note",
            path=Path("/single.md"),
            tags=[],
        )
        mock_repository.find_tagless_notes.return_value = [domain_note]
        input_data = GetTaglessNotesInput()

        # When: サービスを実行する
        result = service.handle(input_data)

        # Then: 単一のノートが返されること
        mock_repository.find_tagless_notes.assert_called_once()
        assert isinstance(result, GetTaglessNotesOutput)
        assert len(result.notes) == 1
        assert result.notes[0].title == "Single tagless note"
        assert result.notes[0].path == Path("/single.md")
        assert result.notes[0].tags == []


class TestGetTaglessNotesInput:
    """GetTaglessNotesInputの単体テスト"""

    def test_create_empty_input(self) -> None:
        # Given: パラメータなし

        # When: インスタンスを作成する
        input_data = GetTaglessNotesInput()

        # Then: 正常にインスタンスが作成されること
        assert isinstance(input_data, GetTaglessNotesInput)


class TestGetTaglessNotesOutput:
    """GetTaglessNotesOutputの単体テスト"""

    def test_create_output_with_notes_list(self) -> None:
        # Given: ノートリスト
        notes = [
            AppNote(
                title="Test Note 1",
                path=Path("/test1.md"),
                tags=[],
            ),
            AppNote(
                title="Test Note 2",
                path=Path("/test2.md"),
                tags=[],
            ),
        ]

        # When: アウトプットインスタンスを作成する
        output = GetTaglessNotesOutput(notes=notes)

        # Then: 正常にインスタンスが作成されること
        assert isinstance(output, GetTaglessNotesOutput)
        assert output.notes == notes
        assert len(output.notes) == 2
        assert output.notes[0].title == "Test Note 1"
        assert output.notes[1].title == "Test Note 2"

    def test_create_output_with_empty_list(self) -> None:
        # Given: 空のノートリスト
        notes: list[AppNote] = []

        # When: アウトプットインスタンスを作成する
        output = GetTaglessNotesOutput(notes=notes)

        # Then: 正常にインスタンスが作成されること
        assert isinstance(output, GetTaglessNotesOutput)
        assert output.notes == notes
        assert len(output.notes) == 0
