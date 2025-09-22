import subprocess
from pathlib import Path
from unittest.mock import Mock

import pytest
from injector import Injector

from zk_utils.application.notes.get_note_content import (
    GetNoteContentInput,
    GetNoteContentService,
)


@pytest.mark.integration
class TestGetNoteContentIntegration:
    """GetNoteContentServiceとZkNoteRepositoryの結合テスト"""

    def test_get_note_content_with_valid_path_should_return_content(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        sample_zk_single_note_output: str,
        sample_zk_note_content_output: str,
        sample_note_path: Path,
    ) -> None:
        # Given: 正常なzk出力をモック
        mock_subprocess_run.side_effect = [
            # get_note呼び出し用のモック（ノート情報取得）
            type(
                "MockResult",
                (),
                {"stdout": sample_zk_single_note_output, "returncode": 0, "stderr": ""},
            )(),
            # get_content呼び出し用のモック（コンテンツ取得）
            type(
                "MockResult",
                (),
                {
                    "stdout": sample_zk_note_content_output,
                    "returncode": 0,
                    "stderr": "",
                },
            )(),
        ]

        service = test_injector.get(GetNoteContentService)
        input_data = GetNoteContentInput(path=sample_note_path)

        # When: ノート内容を取得
        result = service.handle(input_data)

        # Then: 期待するコンテンツが返されること
        assert result.content == sample_zk_note_content_output
        assert mock_subprocess_run.call_count == 2

    def test_get_note_content_with_empty_content_should_return_empty_string(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        sample_zk_single_note_output: str,
        sample_note_path: Path,
    ) -> None:
        # Given: 空のコンテンツを返すzkコマンド
        mock_subprocess_run.side_effect = [
            # get_note呼び出し用のモック
            type(
                "MockResult",
                (),
                {"stdout": sample_zk_single_note_output, "returncode": 0, "stderr": ""},
            )(),
            # get_content呼び出し用のモック（空のコンテンツ）
            type("MockResult", (), {"stdout": "", "returncode": 0, "stderr": ""})(),
        ]

        service = test_injector.get(GetNoteContentService)
        input_data = GetNoteContentInput(path=sample_note_path)

        # When: ノート内容を取得
        result = service.handle(input_data)

        # Then: 空文字列が返されること
        assert result.content == ""

    def test_get_note_content_with_unicode_content_should_handle_correctly(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        sample_zk_single_note_output: str,
        sample_note_path: Path,
    ) -> None:
        # Given: Unicode文字を含むコンテンツ
        unicode_content = "# ユニコードテスト\n\n日本語コンテンツ 🎯\n\nαβγδεζ\n"
        mock_subprocess_run.side_effect = [
            type(
                "MockResult",
                (),
                {"stdout": sample_zk_single_note_output, "returncode": 0, "stderr": ""},
            )(),
            type(
                "MockResult",
                (),
                {"stdout": unicode_content, "returncode": 0, "stderr": ""},
            )(),
        ]

        service = test_injector.get(GetNoteContentService)
        input_data = GetNoteContentInput(path=sample_note_path)

        # When: ノート内容を取得
        result = service.handle(input_data)

        # Then: Unicode文字が正しく処理されること
        assert result.content == unicode_content
        assert "日本語コンテンツ" in result.content
        assert "🎯" in result.content
        assert "αβγδεζ" in result.content

    def test_get_note_content_with_large_content_should_handle_correctly(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        sample_zk_single_note_output: str,
        sample_note_path: Path,
    ) -> None:
        # Given: 大きなコンテンツファイル
        large_content = "# 大きなファイル\n\n" + "テスト行\n" * 1000
        mock_subprocess_run.side_effect = [
            type(
                "MockResult",
                (),
                {"stdout": sample_zk_single_note_output, "returncode": 0, "stderr": ""},
            )(),
            type(
                "MockResult",
                (),
                {"stdout": large_content, "returncode": 0, "stderr": ""},
            )(),
        ]

        service = test_injector.get(GetNoteContentService)
        input_data = GetNoteContentInput(path=sample_note_path)

        # When: ノート内容を取得
        result = service.handle(input_data)

        # Then: 大きなコンテンツが正しく処理されること
        assert result.content == large_content
        assert result.content.count("テスト行") == 1000

    def test_get_note_content_with_zk_command_error_should_raise_runtime_error(
        self,
        test_injector: Injector,
        mock_failed_subprocess: Mock,
        sample_note_path: Path,
    ) -> None:
        # Given: zkコマンドがエラーを返す
        service = test_injector.get(GetNoteContentService)
        input_data = GetNoteContentInput(path=sample_note_path)

        # When & Then: RuntimeErrorが発生すること
        with pytest.raises(RuntimeError, match="Error: zk command failed"):
            service.handle(input_data)

    def test_get_note_content_with_markdown_content_should_preserve_formatting(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        sample_zk_single_note_output: str,
        sample_note_path: Path,
    ) -> None:
        # Given: Markdownフォーマットを含むコンテンツ
        markdown_content = """# メインタイトル

## セクション1

これは**太字**で、これは*斜体*です。

### リスト
- 項目1
- 項目2
  - ネストした項目

### コードブロック
```python
def hello():
    print("Hello, World!")
```

### リンク
[リンクテキスト](https://example.com)

### テーブル
| 列1 | 列2 |
|-----|-----|
| A   | B   |
"""
        mock_subprocess_run.side_effect = [
            type(
                "MockResult",
                (),
                {"stdout": sample_zk_single_note_output, "returncode": 0, "stderr": ""},
            )(),
            type(
                "MockResult",
                (),
                {"stdout": markdown_content, "returncode": 0, "stderr": ""},
            )(),
        ]

        service = test_injector.get(GetNoteContentService)
        input_data = GetNoteContentInput(path=sample_note_path)

        # When: ノート内容を取得
        result = service.handle(input_data)

        # Then: Markdownフォーマットが保持されること
        assert result.content == markdown_content
        assert "# メインタイトル" in result.content
        assert "**太字**" in result.content
        assert "```python" in result.content
        assert "| 列1 | 列2 |" in result.content


@pytest.mark.integration
class TestGetNoteContentErrorHandling:
    """GetNoteContentServiceのエラーハンドリングテスト"""

    def test_get_note_content_with_content_fetch_error_should_raise_runtime_error(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        sample_zk_single_note_output: str,
        sample_note_path: Path,
    ) -> None:
        # Given: ノート情報取得は成功するが、コンテンツ取得でエラー
        mock_subprocess_run.side_effect = [
            # 最初の呼び出し（ノート情報取得）は成功
            type(
                "MockResult",
                (),
                {"stdout": sample_zk_single_note_output, "returncode": 0, "stderr": ""},
            )(),
            # 2回目の呼び出し（コンテンツ取得）でエラー
            subprocess.CalledProcessError(
                returncode=1, cmd=["zk", "list"], stderr="Error: content not found"
            ),
        ]

        service = test_injector.get(GetNoteContentService)
        input_data = GetNoteContentInput(path=sample_note_path)

        # When & Then: RuntimeErrorが発生すること
        with pytest.raises(RuntimeError, match="Error: content not found"):
            service.handle(input_data)
