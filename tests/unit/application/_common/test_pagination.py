import pytest
from pydantic import ValidationError

from zk_utils.application._common.pagination import Pagination


class TestPaginationInitialization:
    """Paginationモデルの初期化テスト"""

    @pytest.mark.parametrize(
        "page,per_page,total,total_pages,has_next,has_prev",
        [
            pytest.param(
                1,
                10,
                100,
                10,
                True,
                False,
                id="first_page_with_multiple_pages_should_create_instance_successfully",
            ),
            pytest.param(
                5,
                20,
                200,
                10,
                True,
                True,
                id="middle_page_should_create_instance_successfully",
            ),
            pytest.param(
                10,
                10,
                100,
                10,
                False,
                True,
                id="last_page_should_create_instance_successfully",
            ),
            pytest.param(
                1,
                50,
                25,
                1,
                False,
                False,
                id="single_page_should_create_instance_successfully",
            ),
            pytest.param(
                1,
                10,
                0,
                0,
                False,
                False,
                id="zero_total_should_create_instance_successfully",
            ),
            pytest.param(
                3,
                15,
                45,
                3,
                False,
                True,
                id="exact_division_last_page_should_create_instance_successfully",
            ),
        ],
    )
    def test_create_pagination_with_valid_data(
        self,
        page: int,
        per_page: int,
        total: int,
        total_pages: int,
        has_next: bool,
        has_prev: bool,
    ) -> None:
        # Given: 有効なページネーションデータ

        # When: Paginationインスタンスを作成する
        pagination = Pagination(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev,
        )

        # Then: 各フィールドが期待値と一致すること
        assert pagination.page == page
        assert pagination.per_page == per_page
        assert pagination.total == total
        assert pagination.total_pages == total_pages
        assert pagination.has_next == has_next
        assert pagination.has_prev == has_prev

    @pytest.mark.parametrize(
        "page,per_page,total,total_pages,has_next,has_prev",
        [
            pytest.param(
                None,
                10,
                100,
                10,
                True,
                False,
                id="page_is_none_should_raise_validation_error",
            ),
            pytest.param(
                1,
                None,
                100,
                10,
                True,
                False,
                id="per_page_is_none_should_raise_validation_error",
            ),
            pytest.param(
                1,
                10,
                None,
                10,
                True,
                False,
                id="total_is_none_should_raise_validation_error",
            ),
            pytest.param(
                1,
                10,
                100,
                None,
                True,
                False,
                id="total_pages_is_none_should_raise_validation_error",
            ),
            pytest.param(
                1,
                10,
                100,
                10,
                None,
                False,
                id="has_next_is_none_should_raise_validation_error",
            ),
            pytest.param(
                1,
                10,
                100,
                10,
                True,
                None,
                id="has_prev_is_none_should_raise_validation_error",
            ),
        ],
    )
    def test_create_pagination_with_invalid_data_should_raise_validation_error(
        self,
        page: object,
        per_page: object,
        total: object,
        total_pages: object,
        has_next: object,
        has_prev: object,
    ) -> None:
        # Given: 無効なデータ

        # When & Then: Paginationインスタンス作成時にValidationErrorが発生すること
        with pytest.raises(ValidationError):
            Pagination(
                page=page,  # type: ignore[arg-type]
                per_page=per_page,  # type: ignore[arg-type]
                total=total,  # type: ignore[arg-type]
                total_pages=total_pages,  # type: ignore[arg-type]
                has_next=has_next,  # type: ignore[arg-type]
                has_prev=has_prev,  # type: ignore[arg-type]
            )


class TestPaginationEquality:
    """Paginationモデルの等価性テスト"""

    def test_paginations_with_same_data_should_be_equal(self) -> None:
        # Given: 同じデータを持つ2つのPaginationインスタンス
        pagination1 = Pagination(
            page=2, per_page=10, total=50, total_pages=5, has_next=True, has_prev=True
        )
        pagination2 = Pagination(
            page=2, per_page=10, total=50, total_pages=5, has_next=True, has_prev=True
        )

        # When & Then: 同じデータを持つPaginationは等価であること
        assert pagination1 == pagination2

    def test_paginations_with_different_data_should_not_be_equal(self) -> None:
        # Given: 異なるデータを持つ2つのPaginationインスタンス
        pagination1 = Pagination(
            page=1, per_page=10, total=50, total_pages=5, has_next=True, has_prev=False
        )
        pagination2 = Pagination(
            page=2, per_page=10, total=50, total_pages=5, has_next=True, has_prev=True
        )

        # When & Then: 異なるデータを持つPaginationは等価でないこと
        assert pagination1 != pagination2

    def test_paginations_with_same_page_different_total_should_not_be_equal(
        self,
    ) -> None:
        # Given: 同じページだが異なるtotalを持つ2つのPaginationインスタンス
        pagination1 = Pagination(
            page=1, per_page=10, total=50, total_pages=5, has_next=True, has_prev=False
        )
        pagination2 = Pagination(
            page=1,
            per_page=10,
            total=100,
            total_pages=10,
            has_next=True,
            has_prev=False,
        )

        # When & Then: 異なるtotalを持つPaginationは等価でないこと
        assert pagination1 != pagination2


class TestPaginationStringRepresentation:
    """Paginationモデルの文字列表現テスト"""

    def test_pagination_string_representation(self) -> None:
        # Given: Paginationインスタンス
        pagination = Pagination(
            page=3, per_page=20, total=150, total_pages=8, has_next=True, has_prev=True
        )

        # When: 文字列表現を取得する
        str_repr = str(pagination)

        # Then: 全てのフィールドが文字列表現に含まれること
        assert "3" in str_repr  # page
        assert "20" in str_repr  # per_page
        assert "150" in str_repr  # total
        assert "8" in str_repr  # total_pages
        assert "True" in str_repr  # has_next, has_prev

    def test_pagination_with_false_flags_string_representation(self) -> None:
        # Given: has_next, has_prevがFalseのPaginationインスタンス
        pagination = Pagination(
            page=1, per_page=10, total=5, total_pages=1, has_next=False, has_prev=False
        )

        # When: 文字列表現を取得する
        str_repr = str(pagination)

        # Then: Falseフラグが文字列表現に含まれること
        assert "1" in str_repr
        assert "10" in str_repr
        assert "5" in str_repr
        assert "False" in str_repr


class TestPaginationTypeValidation:
    """Paginationモデルの型バリデーションテスト"""

    @pytest.mark.parametrize(
        "invalid_page",
        [
            pytest.param("1", id="page_is_string_should_raise_validation_error"),
            pytest.param(1.5, id="page_is_float_should_raise_validation_error"),
            pytest.param([], id="page_is_list_should_raise_validation_error"),
            pytest.param({}, id="page_is_dict_should_raise_validation_error"),
        ],
    )
    def test_invalid_page_type_should_raise_validation_error(
        self, invalid_page: object
    ) -> None:
        # Given: 無効な型のpage

        # When & Then: ValidationErrorが発生すること
        with pytest.raises(ValidationError):
            Pagination(
                page=invalid_page,  # type: ignore[arg-type]
                per_page=10,
                total=100,
                total_pages=10,
                has_next=True,
                has_prev=False,
            )

    @pytest.mark.parametrize(
        "invalid_per_page",
        [
            pytest.param("10", id="per_page_is_string_should_raise_validation_error"),
            pytest.param(10.5, id="per_page_is_float_should_raise_validation_error"),
            pytest.param(True, id="per_page_is_boolean_should_raise_validation_error"),
        ],
    )
    def test_invalid_per_page_type_should_raise_validation_error(
        self, invalid_per_page: object
    ) -> None:
        # Given: 無効な型のper_page

        # When & Then: ValidationErrorが発生すること
        with pytest.raises(ValidationError):
            Pagination(
                page=1,
                per_page=invalid_per_page,  # type: ignore[arg-type]
                total=100,
                total_pages=10,
                has_next=True,
                has_prev=False,
            )

    @pytest.mark.parametrize(
        "invalid_boolean",
        [
            pytest.param("true", id="boolean_is_string_should_raise_validation_error"),
            pytest.param(1, id="boolean_is_int_should_raise_validation_error"),
            pytest.param([], id="boolean_is_list_should_raise_validation_error"),
        ],
    )
    def test_invalid_has_next_type_should_raise_validation_error(
        self, invalid_boolean: object
    ) -> None:
        # Given: 無効な型のhas_next

        # When & Then: ValidationErrorが発生すること
        with pytest.raises(ValidationError):
            Pagination(
                page=1,
                per_page=10,
                total=100,
                total_pages=10,
                has_next=invalid_boolean,  # type: ignore[arg-type]
                has_prev=False,
            )

    def test_invalid_has_prev_type_should_raise_validation_error(self) -> None:
        # Given: 無効な型のhas_prev

        # When & Then: ValidationErrorが発生すること
        with pytest.raises(ValidationError):
            Pagination(
                page=1,
                per_page=10,
                total=100,
                total_pages=10,
                has_next=True,
                has_prev="false",  # type: ignore[arg-type]
            )


class TestPaginationBoundaryValues:
    """Paginationモデルの境界値テスト"""

    def test_pagination_with_zero_values(self) -> None:
        # Given: ゼロ値を含むページネーション

        # When: ゼロ値でPaginationインスタンスを作成する
        pagination = Pagination(
            page=1, per_page=10, total=0, total_pages=0, has_next=False, has_prev=False
        )

        # Then: 正常にインスタンスが作成されること
        assert pagination.page == 1
        assert pagination.per_page == 10
        assert pagination.total == 0
        assert pagination.total_pages == 0
        assert pagination.has_next is False
        assert pagination.has_prev is False

    def test_pagination_with_large_numbers(self) -> None:
        # Given: 大きな数値のページネーション

        # When: 大きな数値でPaginationインスタンスを作成する
        pagination = Pagination(
            page=99999,
            per_page=1000,
            total=99999000,
            total_pages=99999,
            has_next=False,
            has_prev=True,
        )

        # Then: 正常にインスタンスが作成されること
        assert pagination.page == 99999
        assert pagination.per_page == 1000
        assert pagination.total == 99999000
        assert pagination.total_pages == 99999
        assert pagination.has_next is False
        assert pagination.has_prev is True

    @pytest.mark.parametrize(
        "page,per_page,total,total_pages,has_next,has_prev",
        [
            pytest.param(
                0,
                10,
                100,
                10,
                True,
                False,
                id="zero_page_should_create_instance_successfully",
            ),
            pytest.param(
                -1,
                10,
                100,
                10,
                True,
                False,
                id="negative_page_should_create_instance_successfully",
            ),
            pytest.param(
                1,
                -5,
                100,
                10,
                True,
                False,
                id="negative_per_page_should_create_instance_successfully",
            ),
            pytest.param(
                1,
                10,
                -50,
                -5,
                False,
                False,
                id="negative_totals_should_create_instance_successfully",
            ),
        ],
    )
    def test_pagination_with_edge_case_numbers(
        self,
        page: int,
        per_page: int,
        total: int,
        total_pages: int,
        has_next: bool,
        has_prev: bool,
    ) -> None:
        # Given: エッジケースとなる数値

        # When: エッジケース数値でPaginationインスタンスを作成する
        pagination = Pagination(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
            has_next=has_next,
            has_prev=has_prev,
        )

        # Then: 正常にインスタンスが作成されること
        assert pagination.page == page
        assert pagination.per_page == per_page
        assert pagination.total == total
        assert pagination.total_pages == total_pages
        assert pagination.has_next == has_next
        assert pagination.has_prev == has_prev


class TestPaginationImmutability:
    """Paginationモデルの不変性テスト"""

    def test_pagination_fields_are_immutable(self) -> None:
        # Given: Paginationインスタンス
        pagination = Pagination(
            page=1, per_page=10, total=50, total_pages=5, has_next=True, has_prev=False
        )

        # When & Then: フィールドの変更を試みるとValidationErrorが発生すること
        with pytest.raises(ValidationError):
            pagination.page = 2

        with pytest.raises(ValidationError):
            pagination.per_page = 20

        with pytest.raises(ValidationError):
            pagination.total = 100

        with pytest.raises(ValidationError):
            pagination.total_pages = 10

        with pytest.raises(ValidationError):
            pagination.has_next = False

        with pytest.raises(ValidationError):
            pagination.has_prev = True
