# テストガイドライン

## 概要

このプロジェクトではpytestを使用してテストを実装しています。テストは品質保証と回帰防止のために重要な役割を果たします。

## テスト構造

```
tests/
├── unit/           # 単体テスト
├── integration/    # 結合テスト
└── e2e/           # エンドツーエンドテスト
```

## テスト実行

### 全テスト実行
```bash
make test
# または
uv run pytest
```

### 特定のテストファイル実行
```bash
uv run pytest tests/unit/domain/models/test_note.py
```

### カバレッジ付きテスト実行
```bash
uv run pytest --cov=. --cov-report=term-missing
```

## テストマーカー

pytest.iniで定義されているマーカー：

- `unit`: 単体テスト
- `integration`: 結合テスト
- `e2e`: エンドツーエンドテスト
- `slow`: 実行時間の長いテスト

### マーカーの使用例
```bash
# 単体テストのみ実行
uv run pytest -m unit

# 遅いテストを除外
uv run pytest -m "not slow"
```

## 開発ワークフロー

### テスト駆動開発（TDD）
1. テストを先に書く
2. テストが失敗することを確認
3. 最小限のコードで テストを通す
4. リファクタリング

### テスト前チェック
```bash
# lintとフォーマット、テストを一括実行
make pre-commit
```

## 単体テスト実装ガイド

### Arrange-Act-Assert パターン
全ての単体テストはAAA パターンに従って実装する：

```python
def test_example(self) -> None:
    # Given: テストデータの準備
    note = Note(title="Test", path=Path("/test.md"), tags=["tag"])

    # When: テスト対象の実行
    result = note.title

    # Then: 結果の検証
    assert result == "Test"
```

### コメント規約
Given/When/Then形式でコメントを記述：

- `# Given:` - テストの前提条件・データ準備
- `# When:` - テスト対象の処理実行
- `# Then:` - 期待結果の検証

## パラメータ化テスト

### pytest.param形式の使用
```python
@pytest.mark.parametrize(
    "input_value,expected",
    [
        pytest.param("valid_input", "expected_output", id="valid_case_should_return_expected"),
        pytest.param("", None, id="empty_input_should_return_none"),
        pytest.param(None, None, id="none_input_should_return_none"),
    ],
)
def test_example(self, input_value: str, expected: Optional[str]) -> None:
    # Given: 入力値

    # When: 関数実行
    result = target_function(input_value)

    # Then: 期待結果と一致すること
    assert result == expected
```

### ID命名規則
- 英語表記
- 「条件_should_結果」形式
- スネークケース使用
- 具体的で理解しやすい表現

例：
- `all_fields_valid_should_create_instance_successfully`
- `title_is_none_should_raise_validation_error`
- `empty_tags_should_create_instance_successfully`

## テストクラス構成

### クラス分割
機能ごとにテストクラスを分割：

```python
class TestNoteInitialization:
    """Noteエンティティの初期化テスト"""

class TestNoteEquality:
    """Noteエンティティの等価性テスト"""

class TestNoteTypeValidation:
    """Noteエンティティの型バリデーションテスト"""
```

### docstring
各テストクラスには日本語のdocstringで説明を記述。

## 型アノテーション

### 厳密な型指定
```python
def test_example(
    self,
    title: str,
    path: Path,
    tags: list[str],
    expected: Optional[str],
) -> None:
```

### type: ignore の使用
意図的に無効な型をテストする場合：

```python
with pytest.raises(ValidationError):
    Note(title=invalid_title, path=path, tags=tags)  # type: ignore[arg-type]
```

## テストカバレッジ

### 網羅すべき観点
1. **正常系**: 期待通りの動作
2. **異常系**: エラーハンドリング
3. **境界値**: 極値・限界値
4. **型バリデーション**: 不正な型の拒否

### ドメインモデルテスト例
```python
# 正常系
- 全フィールド有効
- オプショナルフィールドNone
- 最小限の値

# 異常系
- 必須フィールドNone
- 無効な型
- 制約違反

# 境界値
- 空文字列
- 空リスト
- 最大値/最小値
```

## モック・スタブ

### pytest-mock使用
```python
def test_with_mock(self, mocker) -> None:
    # Given: モック作成
    mock_client = mocker.Mock()
    mock_client.get_notes.return_value = []

    # When: モックを使用した処理
    service = NoteService(mock_client)
    result = service.get_all_notes()

    # Then: モックの呼び出し確認
    mock_client.get_notes.assert_called_once()
    assert result == []
```

## ファイル構成

### ディレクトリ構造
```
tests/unit/
├── domain/
│   └── models/
│       ├── test_note.py
│       └── test_tag.py
├── application/
│   └── _common/
│       └── test_*.py
└── infrastructure/
    └── zk/
        └── test_*.py
```

### 命名規則
- テストファイル: `test_*.py`
- テストクラス: `Test*`
- テストメソッド: `test_*`
- 英語表記・スネークケース使用

## CI/CD統合

テストは継続的インテグレーションパイプラインで自動実行されます。全てのテストが通ることがマージ条件です。

## トラブルシューティング

### よくある問題

1. **ImportError**: パッケージパスの確認
2. **テストの分離**: 各テストが独立していることを確認
3. **モック**: 外部依存関係は適切にモック化

### デバッグ
```bash
# 詳細出力でテスト実行
uv run pytest -v -s

# 最初の失敗で停止
uv run pytest -x
```