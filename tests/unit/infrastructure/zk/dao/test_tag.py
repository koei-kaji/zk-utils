import pytest
from pydantic import ValidationError

from zk_utils.infrastructure.zk.dao.tag import Tag


class TestTagInitialization:
    """Tagエンティティの初期化テスト"""

    @pytest.mark.parametrize(
        "name,note_count,expected_name,expected_note_count",
        [
            pytest.param(
                "python",
                5,
                "python",
                5,
                id="valid_name_and_positive_count_should_create_instance_successfully",
            ),
            pytest.param(
                "test-tag",
                0,
                "test-tag",
                0,
                id="valid_name_and_zero_count_should_create_instance_successfully",
            ),
            pytest.param(
                "日本語タグ",
                10,
                "日本語タグ",
                10,
                id="japanese_name_should_create_instance_successfully",
            ),
            pytest.param(
                "tag_with_underscore",
                999,
                "tag_with_underscore",
                999,
                id="name_with_underscore_should_create_instance_successfully",
            ),
            pytest.param(
                "",
                1,
                "",
                1,
                id="empty_name_should_create_instance_successfully",
            ),
        ],
    )
    def test_create_tag_with_valid_data(
        self,
        name: str,
        note_count: int,
        expected_name: str,
        expected_note_count: int,
    ) -> None:
        # Given: 有効なデータ

        # When: Tagインスタンスを作成する
        tag = Tag(name=name, note_count=note_count)

        # Then: 各フィールドが期待値と一致すること
        assert tag.name == expected_name
        assert tag.note_count == expected_note_count

    @pytest.mark.parametrize(
        "name,note_count",
        [
            pytest.param(
                None,
                5,
                id="name_is_none_should_raise_validation_error",
            ),
            pytest.param(
                "valid_tag",
                None,
                id="note_count_is_none_should_raise_validation_error",
            ),
            pytest.param(
                "valid_tag",
                "not_a_number",
                id="note_count_is_string_should_raise_validation_error",
            ),
        ],
    )
    def test_create_tag_with_invalid_data_should_raise_validation_error(
        self,
        name: object,
        note_count: object,
    ) -> None:
        # Given: 無効なデータ

        # When & Then: Tagインスタンス作成時にValidationErrorが発生すること
        with pytest.raises(ValidationError):
            Tag(name=name, note_count=note_count)  # type: ignore[arg-type]

    def test_create_tag_with_negative_note_count_should_succeed(self) -> None:
        # Given: 負のnote_count(現在の仕様では許可されている)

        # When: 負のnote_countでTagインスタンスを作成する
        tag = Tag(name="valid_tag", note_count=-1)

        # Then: 正常にインスタンスが作成されること
        assert tag.name == "valid_tag"
        assert tag.note_count == -1


class TestTagEquality:
    """Tagエンティティの等価性テスト"""

    def test_tags_with_same_data_should_be_equal(self) -> None:
        # Given: 同じデータを持つ2つのTagインスタンス
        tag1 = Tag(name="python", note_count=5)
        tag2 = Tag(name="python", note_count=5)

        # When & Then: 同じデータを持つTagは等価であること
        assert tag1 == tag2

    def test_tags_with_different_data_should_not_be_equal(self) -> None:
        # Given: 異なるデータを持つ2つのTagインスタンス
        tag1 = Tag(name="python", note_count=5)
        tag2 = Tag(name="java", note_count=3)

        # When & Then: 異なるデータを持つTagは等価でないこと
        assert tag1 != tag2

    def test_tags_with_same_name_different_count_should_not_be_equal(self) -> None:
        # Given: 同じ名前だが異なるカウントを持つ2つのTagインスタンス
        tag1 = Tag(name="python", note_count=5)
        tag2 = Tag(name="python", note_count=10)

        # When & Then: 異なるカウントを持つTagは等価でないこと
        assert tag1 != tag2


class TestTagStringRepresentation:
    """Tagエンティティの文字列表現テスト"""

    def test_tag_string_representation(self) -> None:
        # Given: Tagインスタンス
        tag = Tag(name="python", note_count=5)

        # When: 文字列表現を取得する
        str_repr = str(tag)

        # Then: 名前とカウントが文字列表現に含まれること
        assert "python" in str_repr
        assert "5" in str_repr

    def test_tag_with_special_characters_string_representation(self) -> None:
        # Given: 特殊文字を含む名前のTagインスタンス
        tag = Tag(name="C++/Java", note_count=3)

        # When: 文字列表現を取得する
        str_repr = str(tag)

        # Then: 特殊文字を含む名前が文字列表現に含まれること
        assert "C++/Java" in str_repr
        assert "3" in str_repr


class TestTagTypeValidation:
    """Tagエンティティの型バリデーションテスト"""

    @pytest.mark.parametrize(
        "invalid_name",
        [
            pytest.param(123, id="name_is_number_should_raise_validation_error"),
            pytest.param([], id="name_is_list_should_raise_validation_error"),
            pytest.param({}, id="name_is_dict_should_raise_validation_error"),
            pytest.param(True, id="name_is_boolean_should_raise_validation_error"),
        ],
    )
    def test_invalid_name_type_should_raise_validation_error(
        self, invalid_name: object
    ) -> None:
        # Given: 無効な型のname

        # When & Then: ValidationErrorが発生すること
        with pytest.raises(ValidationError):
            Tag(name=invalid_name, note_count=5)  # type: ignore[arg-type]

    @pytest.mark.parametrize(
        "invalid_note_count",
        [
            pytest.param("5", id="note_count_is_string_should_raise_validation_error"),
            pytest.param([], id="note_count_is_list_should_raise_validation_error"),
            pytest.param({}, id="note_count_is_dict_should_raise_validation_error"),
            pytest.param(
                True, id="note_count_is_boolean_should_raise_validation_error"
            ),
            pytest.param(5.5, id="note_count_is_float_should_raise_validation_error"),
        ],
    )
    def test_invalid_note_count_type_should_raise_validation_error(
        self, invalid_note_count: object
    ) -> None:
        # Given: 無効な型のnote_count

        # When & Then: ValidationErrorが発生すること
        with pytest.raises(ValidationError):
            Tag(name="valid_tag", note_count=invalid_note_count)  # type: ignore[arg-type]


class TestTagBoundaryValues:
    """Tagエンティティの境界値テスト"""

    def test_tag_with_zero_note_count(self) -> None:
        # Given: note_countが0のTag

        # When: Tagインスタンスを作成する
        tag = Tag(name="unused_tag", note_count=0)

        # Then: 正常にインスタンスが作成されること
        assert tag.name == "unused_tag"
        assert tag.note_count == 0

    def test_tag_with_large_note_count(self) -> None:
        # Given: 大きなnote_countのTag

        # When: Tagインスタンスを作成する
        tag = Tag(name="popular_tag", note_count=999999)

        # Then: 正常にインスタンスが作成されること
        assert tag.name == "popular_tag"
        assert tag.note_count == 999999

    def test_tag_with_single_character_name(self) -> None:
        # Given: 1文字の名前のTag

        # When: Tagインスタンスを作成する
        tag = Tag(name="a", note_count=1)

        # Then: 正常にインスタンスが作成されること
        assert tag.name == "a"
        assert tag.note_count == 1

    def test_tag_with_very_long_name(self) -> None:
        # Given: 非常に長い名前のTag
        long_name = "a" * 1000

        # When: Tagインスタンスを作成する
        tag = Tag(name=long_name, note_count=1)

        # Then: 正常にインスタンスが作成されること
        assert tag.name == long_name
        assert tag.note_count == 1
        assert len(tag.name) == 1000
