from pathlib import Path
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from zk_utils.domain.models.notes.note import Note
from zk_utils.infrastructure.zk.notes.zk_note_repository import ZkNoteRepository
from zk_utils.infrastructure.zk.zk_client import ZkClient


class TestZkNoteRepositoryFindLastModifiedNote:
    """ZkNoteRepositoryの最新変更ノート取得機能テスト"""

    @pytest.fixture
    def mock_client(self, mocker: MockerFixture) -> Mock:
        return mocker.create_autospec(ZkClient)

    @pytest.fixture
    def repository(self, mock_client: Mock) -> ZkNoteRepository:
        return ZkNoteRepository(client=mock_client)

    def test_find_last_modified_note_success(
        self, repository: ZkNoteRepository, mock_client: Mock
    ) -> None:
        # Given: 最新変更ノートが存在する
        expected_note = Note(
            title="Latest Note",
            path=Path("/path/latest.md"),
            tags=["recent", "updated"],
        )
        mock_client.get_last_modified_note.return_value = expected_note

        # When: 最新変更ノートを取得する
        result = repository.find_last_modified_note()

        # Then: ZkClientのメソッドが呼ばれ、Noteオブジェクトが返されること
        mock_client.get_last_modified_note.assert_called_once()
        assert result.title == expected_note.title
        assert result.path == expected_note.path
        assert result.tags == expected_note.tags

    def test_find_last_modified_note_no_result_should_raise_error(
        self, repository: ZkNoteRepository, mock_client: Mock
    ) -> None:
        # Given: 最新変更ノートが存在しない
        mock_client.get_last_modified_note.return_value = None

        # When & Then: ValueErrorが発生すること
        with pytest.raises(ValueError, match="Last modified note not found"):
            repository.find_last_modified_note()

        mock_client.get_last_modified_note.assert_called_once()

    def test_find_last_modified_note_client_exception_should_propagate(
        self, repository: ZkNoteRepository, mock_client: Mock
    ) -> None:
        # Given: ZkClientで例外が発生する
        mock_client.get_last_modified_note.side_effect = RuntimeError("Client error")

        # When & Then: RuntimeErrorが伝播すること
        with pytest.raises(RuntimeError, match="Client error"):
            repository.find_last_modified_note()

        mock_client.get_last_modified_note.assert_called_once()


class TestZkNoteRepositoryFindNoteContent:
    """ZkNoteRepositoryのノートコンテンツ取得機能テスト"""

    @pytest.fixture
    def mock_client(self, mocker: MockerFixture) -> Mock:
        return mocker.create_autospec(ZkClient)

    @pytest.fixture
    def repository(self, mock_client: Mock) -> ZkNoteRepository:
        return ZkNoteRepository(client=mock_client)

    def test_find_note_content_success(
        self, repository: ZkNoteRepository, mock_client: Mock
    ) -> None:
        # Given: ノートが存在する
        path = Path("/test.md")
        expected_note = Note(
            title="Test Note",
            path=path,
            tags=["test"],
            content="# Test Note\n\nContent here.",
        )
        mock_client.get_note.return_value = expected_note

        # When: ノートコンテンツを取得する
        result = repository.find_note_content(path)

        # Then: ZkClientのメソッドが呼ばれ、Noteオブジェクトが返されること
        mock_client.get_note.assert_called_once_with(path)
        assert result.title == expected_note.title
        assert result.path == expected_note.path
        assert result.tags == expected_note.tags
        assert result.content == expected_note.content


class TestZkNoteRepositoryFindTaglessNotes:
    """ZkNoteRepositoryのタグなしノート取得機能テスト"""

    @pytest.fixture
    def mock_client(self, mocker: MockerFixture) -> Mock:
        return mocker.create_autospec(ZkClient)

    @pytest.fixture
    def repository(self, mock_client: Mock) -> ZkNoteRepository:
        return ZkNoteRepository(client=mock_client)

    def test_find_tagless_notes_success(
        self, repository: ZkNoteRepository, mock_client: Mock
    ) -> None:
        # Given: タグなしノートが存在する
        expected_notes = [
            Note(
                title="Note without tags 1",
                path=Path("/path/note1.md"),
                tags=[],
            ),
            Note(
                title="Note without tags 2",
                path=Path("/path/note2.md"),
                tags=[],
            ),
        ]
        mock_client.get_tagless_notes.return_value = expected_notes

        # When: タグなしノートを取得する
        result = repository.find_tagless_notes()

        # Then: ZkClientのメソッドが呼ばれ、Noteオブジェクトのリストが返されること
        mock_client.get_tagless_notes.assert_called_once()
        assert len(result) == 2
        assert result[0].title == expected_notes[0].title
        assert result[0].path == expected_notes[0].path
        assert result[0].tags == expected_notes[0].tags
        assert result[1].title == expected_notes[1].title
        assert result[1].path == expected_notes[1].path
        assert result[1].tags == expected_notes[1].tags

    def test_find_tagless_notes_empty_result(
        self, repository: ZkNoteRepository, mock_client: Mock
    ) -> None:
        # Given: タグなしノートが存在しない
        mock_client.get_tagless_notes.return_value = []

        # When: タグなしノートを取得する
        result = repository.find_tagless_notes()

        # Then: 空のリストが返されること
        mock_client.get_tagless_notes.assert_called_once()
        assert len(result) == 0

    def test_find_tagless_notes_client_exception_should_propagate(
        self, repository: ZkNoteRepository, mock_client: Mock
    ) -> None:
        # Given: ZkClientで例外が発生する
        mock_client.get_tagless_notes.side_effect = RuntimeError("Client error")

        # When & Then: RuntimeErrorが伝播すること
        with pytest.raises(RuntimeError, match="Client error"):
            repository.find_tagless_notes()

        mock_client.get_tagless_notes.assert_called_once()


class TestZkNoteRepositoryCreateNote:
    """ZkNoteRepositoryのノート作成機能テスト"""

    @pytest.fixture
    def mock_client(self, mocker: MockerFixture) -> Mock:
        return mocker.create_autospec(ZkClient)

    @pytest.fixture
    def repository(self, mock_client: Mock) -> ZkNoteRepository:
        return ZkNoteRepository(client=mock_client)

    def test_create_note_success(
        self, repository: ZkNoteRepository, mock_client: Mock
    ) -> None:
        # Given: ノート作成パラメータ
        title = "New Note"
        path = Path("/notes/new.md")
        created_note = Note(title=title, path=Path("/created/note.md"), tags=[])
        mock_client.create_note.return_value = created_note

        # When: ノートを作成する
        result = repository.create_note(title, path)

        # Then: ZkClientのメソッドが呼ばれ、Noteオブジェクトが返されること
        mock_client.create_note.assert_called_once_with(title, path)
        assert result.title == created_note.title
        assert result.path == created_note.path
        assert result.tags == []
