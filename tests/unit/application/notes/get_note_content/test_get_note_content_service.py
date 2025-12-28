from pathlib import Path
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from zk_utils.application.notes.get_note_content import (
    GetNoteContentInput,
    GetNoteContentOutput,
    GetNoteContentService,
)
from zk_utils.domain.models.notes.if_note_repository import IFNoteRepository
from zk_utils.domain.models.notes.note import Note as DomainNote


class TestGetNoteContentService:
    """GetNoteContentServiceの単体テスト"""

    @pytest.fixture
    def mock_repository(self, mocker: MockerFixture) -> Mock:
        return mocker.create_autospec(IFNoteRepository)

    @pytest.fixture
    def service(self, mock_repository: Mock) -> GetNoteContentService:
        return GetNoteContentService(repository=mock_repository)

    @pytest.fixture
    def sample_markdown_content(self) -> str:
        """テスト用のマークダウンコンテンツ"""
        return """# Main Title

## Section 1

This is content of section 1.

- Item 1
- Item 2

## Section 2

This is content of section 2.

```python
print("Hello")
```

## Section 3

This is content of section 3.
"""

    def test_handle_without_headings(
        self,
        service: GetNoteContentService,
        mock_repository: Mock,
        sample_markdown_content: str,
    ) -> None:
        """headingsを指定しない場合、全内容とh2一覧が返されること"""
        # Given: リポジトリからノートが取得できる
        domain_note = DomainNote(
            title="Test Note",
            path=Path("/test.md"),
            tags=["test"],
            content=sample_markdown_content,
        )
        mock_repository.find_note_content.return_value = domain_note
        input_data = GetNoteContentInput(path=Path("/test.md"))

        # When: サービスを実行する
        result = service.handle(input_data)

        # Then: 全内容とh2見出し一覧が返されること
        mock_repository.find_note_content.assert_called_once_with(Path("/test.md"))
        assert isinstance(result, GetNoteContentOutput)
        assert result.content == sample_markdown_content
        assert result.headings == ["Section 1", "Section 2", "Section 3"]

    @pytest.mark.parametrize(
        "headings,expected_in_content,expected_not_in_content,description",
        [
            (
                ["Section 1"],
                ["Section 1", "This is content of section 1."],
                ["Section 2", "Section 3"],
                "単一の見出し",
            ),
            (
                ["Section 1", "Section 3"],
                [
                    "Section 1",
                    "This is content of section 1.",
                    "Section 3",
                    "This is content of section 3.",
                ],
                ["Section 2"],
                "複数の見出し",
            ),
            (
                ["Nonexistent Section"],
                [],
                ["Section 1", "Section 2", "Section 3"],
                "存在しない見出し",
            ),
            (
                ["Section 1", "Nonexistent", "Section 2"],
                [
                    "Section 1",
                    "This is content of section 1.",
                    "Section 2",
                    "This is content of section 2.",
                ],
                ["Section 3"],
                "存在する見出しと存在しない見出しの混在",
            ),
        ],
        ids=["single", "multiple", "nonexistent", "mixed"],
    )
    def test_handle_with_headings_variations(
        self,
        service: GetNoteContentService,
        mock_repository: Mock,
        sample_markdown_content: str,
        headings: list[str],
        expected_in_content: list[str],
        expected_not_in_content: list[str],
        description: str,
    ) -> None:
        """様々な見出し指定パターンのテスト"""
        # Given: リポジトリからノートが取得できる
        domain_note = DomainNote(
            title="Test Note",
            path=Path("/test.md"),
            tags=["test"],
            content=sample_markdown_content,
        )
        mock_repository.find_note_content.return_value = domain_note
        input_data = GetNoteContentInput(path=Path("/test.md"), headings=headings)

        # When: サービスを実行する
        result = service.handle(input_data)

        # Then: 期待される内容が含まれていること
        assert isinstance(result, GetNoteContentOutput)
        for expected in expected_in_content:
            assert expected in result.content, (
                f"{description}: '{expected}' が含まれていません"
            )
        for not_expected in expected_not_in_content:
            assert not_expected not in result.content, (
                f"{description}: '{not_expected}' が含まれています"
            )
        assert result.headings == ["Section 1", "Section 2", "Section 3"]

    @pytest.mark.parametrize(
        "content,expected_content,expected_headings,description",
        [
            ("", "", [], "空のコンテンツ"),
            (None, "", [], "Noneのコンテンツ"),
        ],
        ids=["empty", "none"],
    )
    def test_handle_with_empty_or_none_content(
        self,
        service: GetNoteContentService,
        mock_repository: Mock,
        content: str | None,
        expected_content: str,
        expected_headings: list[str],
        description: str,
    ) -> None:
        """空またはNoneのコンテンツの場合のテスト"""
        # Given: リポジトリから空/Noneのノートが取得できる
        domain_note = DomainNote(
            title="Test Note",
            path=Path("/test.md"),
            tags=[],
            content=content,
        )
        mock_repository.find_note_content.return_value = domain_note
        input_data = GetNoteContentInput(path=Path("/test.md"))

        # When: サービスを実行する
        result = service.handle(input_data)

        # Then: 空文字と空のheadingsが返されること
        assert isinstance(result, GetNoteContentOutput)
        assert result.content == expected_content, (
            f"{description}: contentが期待値と異なります"
        )
        assert result.headings == expected_headings, (
            f"{description}: headingsが期待値と異なります"
        )

    def test_handle_with_no_h2_headings(
        self, service: GetNoteContentService, mock_repository: Mock
    ) -> None:
        """h2見出しがない場合、空のheadingsが返されること"""
        # Given: h2見出しがないコンテンツ
        content = """# Main Title

This is just content without h2 headings.

### Section 3.1

This is h3 heading.
"""
        domain_note = DomainNote(
            title="No H2 Note",
            path=Path("/noh2.md"),
            tags=[],
            content=content,
        )
        mock_repository.find_note_content.return_value = domain_note
        input_data = GetNoteContentInput(path=Path("/noh2.md"))

        # When: サービスを実行する
        result = service.handle(input_data)

        # Then: 空のheadingsが返されること
        assert isinstance(result, GetNoteContentOutput)
        assert result.content == content
        assert result.headings == []

    def test_handle_with_japanese_headings(
        self, service: GetNoteContentService, mock_repository: Mock
    ) -> None:
        """日本語の見出しが正しく処理されること"""
        # Given: 日本語の見出しを含むコンテンツ
        content = """# メインタイトル

## セクション1

これはセクション1の内容です。

## セクション2

これはセクション2の内容です。
"""
        domain_note = DomainNote(
            title="日本語ノート",
            path=Path("/japanese.md"),
            tags=["日本語"],
            content=content,
        )
        mock_repository.find_note_content.return_value = domain_note
        input_data = GetNoteContentInput(
            path=Path("/japanese.md"), headings=["セクション1"]
        )

        # When: サービスを実行する
        result = service.handle(input_data)

        # Then: 日本語の見出しが正しく処理されること
        assert isinstance(result, GetNoteContentOutput)
        assert "セクション1" in result.content
        assert "これはセクション1の内容です。" in result.content
        assert "セクション2" not in result.content
        assert result.headings == ["セクション1", "セクション2"]
