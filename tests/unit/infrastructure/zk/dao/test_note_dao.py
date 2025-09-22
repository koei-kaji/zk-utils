from pathlib import Path
from typing import Optional

import pytest
from pydantic import ValidationError

from zk_utils.infrastructure.zk.dao.note import Note


class TestNoteInitialization:
    """Note DAOの初期化テスト"""

    @pytest.mark.parametrize(
        "title,path,tags,content,expected_title,expected_path,expected_tags,expected_content",
        [
            pytest.param(
                "Test Note",
                Path("/test/note.md"),
                ["python", "testing"],
                "# Test Note\n\nThis is content.",
                "Test Note",
                Path("/test/note.md"),
                ["python", "testing"],
                "# Test Note\n\nThis is content.",
                id="full_note_data_should_create_instance_successfully",
            ),
            pytest.param(
                "Simple Note",
                Path("relative/path.md"),
                [],
                None,
                "Simple Note",
                Path("relative/path.md"),
                [],
                None,
                id="note_without_tags_and_content_should_create_instance_successfully",
            ),
            pytest.param(
                "日本語タイトル",
                Path("/japanese/note.md"),
                ["日本語", "タグ"],
                "日本語コンテンツ",
                "日本語タイトル",
                Path("/japanese/note.md"),
                ["日本語", "タグ"],
                "日本語コンテンツ",
                id="japanese_text_should_create_instance_successfully",
            ),
            pytest.param(
                "Empty Content",
                Path("/empty.md"),
                ["tag"],
                "",
                "Empty Content",
                Path("/empty.md"),
                ["tag"],
                "",
                id="empty_content_string_should_create_instance_successfully",
            ),
            pytest.param(
                "Single Tag",
                Path("/single.md"),
                ["solo"],
                "Content here",
                "Single Tag",
                Path("/single.md"),
                ["solo"],
                "Content here",
                id="single_tag_should_create_instance_successfully",
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
                Path("/test.md"),
                ["tag"],
                "content",
                id="title_is_none_should_raise_validation_error",
            ),
            pytest.param(
                "Valid Title",
                None,
                ["tag"],
                "content",
                id="path_is_none_should_raise_validation_error",
            ),
            pytest.param(
                "Valid Title",
                Path("/test.md"),
                None,
                "content",
                id="tags_is_none_should_raise_validation_error",
            ),
        ],
    )
    def test_create_note_with_invalid_data_should_raise_validation_error(
        self,
        title: object,
        path: object,
        tags: object,
        content: Optional[str],
    ) -> None:
        # Given: 無効なデータ

        # When & Then: Noteインスタンス作成時にValidationErrorが発生すること
        with pytest.raises(ValidationError):
            Note(title=title, path=path, tags=tags, content=content)  # type: ignore[arg-type]

    def test_create_note_with_empty_title_should_succeed(self) -> None:
        # Given: 空のタイトル(現在の仕様では許可されている)

        # When: 空のタイトルでNoteインスタンスを作成する
        note = Note(title="", path=Path("/empty.md"), tags=["tag"], content=None)

        # Then: 正常にインスタンスが作成されること
        assert note.title == ""
        assert note.path == Path("/empty.md")
        assert note.tags == ["tag"]
        assert note.content is None


class TestNoteEquality:
    """Note DAOの等価性テスト"""

    def test_notes_with_same_data_should_be_equal(self) -> None:
        # Given: 同じデータを持つ2つのNoteインスタンス
        note1 = Note(
            title="Test Note", path=Path("/test.md"), tags=["python"], content="Content"
        )
        note2 = Note(
            title="Test Note", path=Path("/test.md"), tags=["python"], content="Content"
        )

        # When & Then: 同じデータを持つNoteは等価であること
        assert note1 == note2

    def test_notes_with_different_data_should_not_be_equal(self) -> None:
        # Given: 異なるデータを持つ2つのNoteインスタンス
        note1 = Note(
            title="Note 1", path=Path("/note1.md"), tags=["tag1"], content="Content 1"
        )
        note2 = Note(
            title="Note 2", path=Path("/note2.md"), tags=["tag2"], content="Content 2"
        )

        # When & Then: 異なるデータを持つNoteは等価でないこと
        assert note1 != note2

    def test_notes_with_same_content_different_path_should_not_be_equal(self) -> None:
        # Given: 同じコンテンツだが異なるパスを持つ2つのNoteインスタンス
        note1 = Note(
            title="Same Title",
            path=Path("/path1.md"),
            tags=["tag"],
            content="Same content",
        )
        note2 = Note(
            title="Same Title",
            path=Path("/path2.md"),
            tags=["tag"],
            content="Same content",
        )

        # When & Then: 異なるパスを持つNoteは等価でないこと
        assert note1 != note2


class TestNoteStringRepresentation:
    """Note DAOの文字列表現テスト"""

    def test_note_string_representation(self) -> None:
        # Given: Noteインスタンス
        note = Note(
            title="Test Note",
            path=Path("/test.md"),
            tags=["python", "test"],
            content="# Test\n\nContent here.",
        )

        # When: 文字列表現を取得する
        str_repr = str(note)

        # Then: 全てのフィールドが文字列表現に含まれること
        assert "Test Note" in str_repr
        assert "/test.md" in str_repr
        assert "python" in str_repr
        assert "test" in str_repr
        assert "Content here" in str_repr

    def test_note_with_none_content_string_representation(self) -> None:
        # Given: contentがNoneのNoteインスタンス
        note = Note(
            title="No Content Note",
            path=Path("/no-content.md"),
            tags=["empty"],
            content=None,
        )

        # When: 文字列表現を取得する
        str_repr = str(note)

        # Then: contentフィールドがNoneとして表現されること
        assert "No Content Note" in str_repr
        assert "/no-content.md" in str_repr
        assert "empty" in str_repr
        assert "None" in str_repr


class TestNoteTypeValidation:
    """Note DAOの型バリデーションテスト"""

    @pytest.mark.parametrize(
        "invalid_title",
        [
            pytest.param(123, id="title_is_number_should_raise_validation_error"),
            pytest.param([], id="title_is_list_should_raise_validation_error"),
            pytest.param({}, id="title_is_dict_should_raise_validation_error"),
            pytest.param(True, id="title_is_boolean_should_raise_validation_error"),
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
                path=Path("/test.md"),
                tags=["tag"],
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
            pytest.param({}, id="path_is_dict_should_raise_validation_error"),
        ],
    )
    def test_invalid_path_type_should_raise_validation_error(
        self, invalid_path: object
    ) -> None:
        # Given: 無効な型のpath

        # When & Then: ValidationErrorが発生すること
        with pytest.raises(ValidationError):
            Note(
                title="Valid Title",
                path=invalid_path,  # type: ignore[arg-type]
                tags=["tag"],
                content=None,
            )

    @pytest.mark.parametrize(
        "invalid_tags",
        [
            pytest.param(
                "string_tags", id="tags_is_string_should_raise_validation_error"
            ),
            pytest.param(123, id="tags_is_number_should_raise_validation_error"),
            pytest.param({}, id="tags_is_dict_should_raise_validation_error"),
            pytest.param(
                ["valid", 123], id="tags_contains_number_should_raise_validation_error"
            ),
            pytest.param(
                [True, "valid"],
                id="tags_contains_boolean_should_raise_validation_error",
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
                title="Valid Title",
                path=Path("/test.md"),
                tags=invalid_tags,  # type: ignore[arg-type]
                content=None,
            )

    @pytest.mark.parametrize(
        "invalid_content",
        [
            pytest.param(123, id="content_is_number_should_raise_validation_error"),
            pytest.param([], id="content_is_list_should_raise_validation_error"),
            pytest.param({}, id="content_is_dict_should_raise_validation_error"),
            pytest.param(True, id="content_is_boolean_should_raise_validation_error"),
        ],
    )
    def test_invalid_content_type_should_raise_validation_error(
        self, invalid_content: object
    ) -> None:
        # Given: 無効な型のcontent

        # When & Then: ValidationErrorが発生すること
        with pytest.raises(ValidationError):
            Note(
                title="Valid Title",
                path=Path("/test.md"),
                tags=["tag"],
                content=invalid_content,  # type: ignore[arg-type]
            )


class TestNoteBoundaryValues:
    """Note DAOの境界値テスト"""

    def test_note_with_empty_tags_list(self) -> None:
        # Given: 空のタグリスト

        # When: 空のタグリストでNoteインスタンスを作成する
        note = Note(
            title="No Tags Note",
            path=Path("/no-tags.md"),
            tags=[],
            content="Content without tags",
        )

        # Then: 正常にインスタンスが作成されること
        assert note.title == "No Tags Note"
        assert note.path == Path("/no-tags.md")
        assert note.tags == []
        assert note.content == "Content without tags"

    def test_note_with_very_long_title(self) -> None:
        # Given: 非常に長いタイトル
        long_title = "A" * 1000

        # When: 長いタイトルでNoteインスタンスを作成する
        note = Note(
            title=long_title,
            path=Path("/long-title.md"),
            tags=["long"],
            content="Content",
        )

        # Then: 正常にインスタンスが作成されること
        assert note.title == long_title
        assert len(note.title) == 1000
        assert note.path == Path("/long-title.md")
        assert note.tags == ["long"]
        assert note.content == "Content"

    def test_note_with_many_tags(self) -> None:
        # Given: 多数のタグ
        many_tags = [f"tag{i}" for i in range(100)]

        # When: 多数のタグでNoteインスタンスを作成する
        note = Note(
            title="Many Tags Note",
            path=Path("/many-tags.md"),
            tags=many_tags,
            content="Content with many tags",
        )

        # Then: 正常にインスタンスが作成されること
        assert note.title == "Many Tags Note"
        assert note.path == Path("/many-tags.md")
        assert len(note.tags) == 100
        assert note.tags[0] == "tag0"
        assert note.tags[99] == "tag99"
        assert note.content == "Content with many tags"

    def test_note_with_very_long_content(self) -> None:
        # Given: 非常に長いコンテンツ
        long_content = "Content line.\n" * 1000

        # When: 長いコンテンツでNoteインスタンスを作成する
        note = Note(
            title="Long Content Note",
            path=Path("/long-content.md"),
            tags=["large"],
            content=long_content,
        )

        # Then: 正常にインスタンスが作成されること
        assert note.title == "Long Content Note"
        assert note.path == Path("/long-content.md")
        assert note.tags == ["large"]
        assert note.content is not None
        assert len(note.content) > 10000
        assert note.content.startswith("Content line.")
        assert note.content.endswith("Content line.\n")


class TestNoteFieldModification:
    """Note DAOのフィールド変更テスト"""

    def test_note_content_modification(self) -> None:
        # Given: Noteインスタンス
        note = Note(
            title="Test Note",
            path=Path("/test.md"),
            tags=["python"],
            content="Original content",
        )

        # When: contentを変更する
        note.content = "Modified content"

        # Then: contentが変更されること
        assert note.content == "Modified content"
        assert note.title == "Test Note"  # 他のフィールドは変更されない
        assert note.path == Path("/test.md")
        assert note.tags == ["python"]

    def test_note_content_set_to_none(self) -> None:
        # Given: contentを持つNoteインスタンス
        note = Note(
            title="Test Note",
            path=Path("/test.md"),
            tags=["python"],
            content="Original content",
        )

        # When: contentをNoneに設定する
        note.content = None

        # Then: contentがNoneになること
        assert note.content is None
        assert note.title == "Test Note"
        assert note.path == Path("/test.md")
        assert note.tags == ["python"]
