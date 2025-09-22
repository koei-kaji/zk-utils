from pathlib import Path
from typing import Optional

import pytest
from pydantic import ValidationError

from zk_utils.domain.models.notes.note import Note


class TestNoteInitialization:
    """Noteエンティティの初期化テスト"""

    @pytest.mark.parametrize(
        "title,path,tags,content,expected_title,expected_path,expected_tags,expected_content",
        [
            pytest.param(
                "Test Note",
                Path("/test/path.md"),
                ["tag1", "tag2"],
                "content",
                "Test Note",
                Path("/test/path.md"),
                ["tag1", "tag2"],
                "content",
                id="all_fields_are_valid_values_should_create_instance_successfully",
            ),
            pytest.param(
                "Test Note",
                Path("/test/path.md"),
                ["tag1"],
                None,
                "Test Note",
                Path("/test/path.md"),
                ["tag1"],
                None,
                id="content_is_none_should_create_instance_successfully",
            ),
            pytest.param(
                "Empty Tags",
                Path("/empty/tags.md"),
                [],
                None,
                "Empty Tags",
                Path("/empty/tags.md"),
                [],
                None,
                id="tags_is_empty_list_should_create_instance_successfully",
            ),
            pytest.param(
                "Relative Path",
                Path("relative/path.md"),
                ["tag"],
                None,
                "Relative Path",
                Path("relative/path.md"),
                ["tag"],
                None,
                id="relative_path_should_create_instance_successfully",
            ),
        ],
    )
    def test_create_note_with_valid_data(
        self,
        title: str,
        path: Path,
        tags: list[str],
        content: Optional[str],
        expected_title: str,
        expected_path: Path,
        expected_tags: list[str],
        expected_content: Optional[str],
    ) -> None:
        # Given: 有効なデータ

        # When: Noteインスタンスを作成する
        note = Note(title=title, path=path, tags=tags, content=content)

        # Then: 各フィールドが期待値と一致すること
        assert note.title == expected_title
        assert note.path == expected_path
        assert note.tags == expected_tags
        assert note.content == expected_content

    @pytest.mark.parametrize(
        "title,path,tags,content",
        [
            pytest.param(
                None,
                Path("/test/path.md"),
                ["tag1"],
                None,
                id="title_is_none_should_raise_validation_error",
            ),
            pytest.param(
                "Test Note",
                None,
                ["tag1"],
                None,
                id="path_is_none_should_raise_validation_error",
            ),
            pytest.param(
                "Test Note",
                Path("/test/path.md"),
                None,
                None,
                id="tags_is_none_should_raise_validation_error",
            ),
        ],
    )
    def test_create_note_with_invalid_data_should_raise_validation_error(
        self,
        title: Optional[str],
        path: Optional[Path],
        tags: Optional[list[str]],
        content: Optional[str],
    ) -> None:
        # Given: 無効なデータ

        # When & Then: Noteインスタンス作成時にValidationErrorが発生すること
        with pytest.raises(ValidationError):
            Note(title=title, path=path, tags=tags, content=content)  # type: ignore[arg-type]

    def test_create_note_with_empty_title_should_succeed(self) -> None:
        # Given: 空文字のtitle(現在の仕様では許可されている)

        # When: 空文字のtitleでNoteインスタンスを作成する
        note = Note(title="", path=Path("/test/path.md"), tags=["tag1"], content=None)

        # Then: 正常にインスタンスが作成されること
        assert note.title == ""
        assert note.path == Path("/test/path.md")
        assert note.tags == ["tag1"]
        assert note.content is None


class TestNoteEquality:
    """Noteエンティティの等価性テスト"""

    def test_notes_with_same_data_should_be_equal(self) -> None:
        # Given: 同じデータを持つ2つのNoteインスタンス
        note1 = Note(
            title="Test Note",
            path=Path("/test/path.md"),
            tags=["tag1", "tag2"],
            content="content",
        )
        note2 = Note(
            title="Test Note",
            path=Path("/test/path.md"),
            tags=["tag1", "tag2"],
            content="content",
        )

        # When & Then: 同じデータを持つNoteは等価であること
        assert note1 == note2

    def test_notes_with_different_data_should_not_be_equal(self) -> None:
        # Given: 異なるデータを持つ2つのNoteインスタンス
        note1 = Note(
            title="Test Note 1",
            path=Path("/test/path1.md"),
            tags=["tag1"],
            content="content1",
        )
        note2 = Note(
            title="Test Note 2",
            path=Path("/test/path2.md"),
            tags=["tag2"],
            content="content2",
        )

        # When & Then: 異なるデータを持つNoteは等価でないこと
        assert note1 != note2


class TestNoteStringRepresentation:
    """Noteエンティティの文字列表現テスト"""

    def test_note_string_representation(self) -> None:
        # Given: Noteインスタンス
        note = Note(
            title="Test Note",
            path=Path("/test/path.md"),
            tags=["tag1", "tag2"],
            content="test content",
        )

        # When: 文字列表現を取得する
        str_repr = str(note)

        # Then: 全てのフィールドが文字列表現に含まれること
        assert "Test Note" in str_repr
        assert "/test/path.md" in str_repr
        assert "tag1" in str_repr
        assert "tag2" in str_repr
        assert "test content" in str_repr


class TestNoteTypeValidation:
    """Noteエンティティの型バリデーションテスト"""

    @pytest.mark.parametrize(
        "invalid_title",
        [
            pytest.param(123, id="title_is_number_should_raise_validation_error"),
            pytest.param([], id="title_is_list_should_raise_validation_error"),
            pytest.param({}, id="title_is_dict_should_raise_validation_error"),
        ],
    )
    def test_invalid_title_type_should_raise_validation_error(
        self, invalid_title: object
    ) -> None:
        # Given: 無効な型のtitle

        # When & Then: ValidationErrorが発生すること
        with pytest.raises(ValidationError):
            Note(
                title=invalid_title,  # type: ignore[arg-type]
                path=Path("/test/path.md"),
                tags=["tag1"],
                content=None,
            )

    @pytest.mark.parametrize(
        "invalid_path",
        [
            pytest.param(
                "/string/path", id="path_is_string_should_raise_validation_error"
            ),
            pytest.param(123, id="path_is_number_should_raise_validation_error"),
            pytest.param([], id="path_is_list_should_raise_validation_error"),
        ],
    )
    def test_invalid_path_type_should_raise_validation_error(
        self, invalid_path: object
    ) -> None:
        # Given: 無効な型のpath

        # When & Then: ValidationErrorが発生すること
        with pytest.raises(ValidationError):
            Note(title="Test Note", path=invalid_path, tags=["tag1"], content=None)  # type: ignore[arg-type]

    @pytest.mark.parametrize(
        "invalid_tags",
        [
            pytest.param(
                "string_tags", id="tags_is_string_should_raise_validation_error"
            ),
            pytest.param(123, id="tags_is_number_should_raise_validation_error"),
            pytest.param({}, id="tags_is_dict_should_raise_validation_error"),
            pytest.param(
                ["valid_tag", 123],
                id="tags_contains_number_should_raise_validation_error",
            ),
        ],
    )
    def test_invalid_tags_type_should_raise_validation_error(
        self, invalid_tags: object
    ) -> None:
        # Given: 無効な型のtags

        # When & Then: ValidationErrorが発生すること
        with pytest.raises(ValidationError):
            Note(
                title="Test Note",
                path=Path("/test/path.md"),
                tags=invalid_tags,  # type: ignore[arg-type]
                content=None,
            )
