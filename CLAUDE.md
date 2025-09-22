# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

zk-utilsは、zkノート管理ツール用のMCP（Model Context Protocol）サーバーです。zkと連携してノート検索、作成、リンク解析などの機能を提供します。

## Architecture

プロジェクトはDDD（ドメイン駆動設計）とクリーンアーキテクチャを採用しています：

```
src/zk_utils/
├── domain/          # ドメインモデル（Note, Tag等）
├── application/     # ユースケース・アプリケーションサービス
├── infrastructure/ # 外部システム（zkコマンド）との連携
└── presentation/   # MCPサーバー（FastMCP）とDI設定
```

### Key Components

- **ZkClient**: zkコマンドラインツールとの連携（subprocess経由）
- **FastMCP**: MCPサーバーフレームワーク
- **Injector**: 依存性注入コンテナ
- **Note Domain Model**: title, path, tags, contentを持つノートエンティティ

### MCP Tools

MCPサーバーは以下のツールを提供：
- `get_notes`: ノート一覧取得（ページネーション、検索、タグフィルタ対応）
- `get_note_content`: 指定ノートの内容取得
- `get_link_to_notes`: 指定ノートからのリンク先取得
- `get_linked_by_notes`: 指定ノートへのリンク元取得
- `get_related_notes`: 関連ノート取得
- `get_tags`: タグ一覧取得
- `create_note`: 新規ノート作成

## Development Commands

### Setup
```bash
# 依存関係のインストール
uv sync
```

### Testing
```bash
# 全テスト実行
make test
# または
uv run pytest

# 特定のテストファイル実行
uv run pytest tests/test_specific.py

# カバレッジ付きテスト実行（pytest.iniで設定済み）
uv run pytest --cov=. --cov-report=term-missing
```

### Linting & Formatting
```bash
# lintチェック（ruff + mypy）
make lint
# または
uv run ruff check .
uv run mypy --show-error-codes .

# フォーマット実行
make format
# または
uv run ruff check . --select I --fix-only --exit-zero
uv run ruff format .

# 全体チェック（format + lint + test）
make pre-commit
```

### MCP Server Development
```bash
# MCPサーバー起動（開発用）
make mcp-run
# または
ZK_DIR=. uv run mcp dev src/zk_utils/presentation/mcp/server.py
```

## Environment Variables

- `ZK_DIR`: zkノートディレクトリのパス（MCPサーバー実行時に必要）

## Key Dependencies

- **mcp[cli]**: MCPサーバーフレームワーク
- **pydantic-settings**: 設定管理
- **injector**: 依存性注入
- **ruff**: リンター・フォーマッター
- **mypy**: 型チェック
- **pytest**: テストフレームワーク

## Notes

- zkコマンドラインツールが事前にインストールされている必要があります
- すべてのzkコマンド実行はsubprocessを通じて行われます
- MCPサーバーはstdio transportで動作します