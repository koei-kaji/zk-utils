from unittest.mock import Mock

import pytest
from injector import Injector
from pytest import MonkeyPatch

from zk_utils.application.notes.get_tagless_notes import GetTaglessNotesService
from zk_utils.presentation.injector import injector as app_injector
from zk_utils.presentation.mcp.server import get_tagless_notes


@pytest.mark.integration
class TestGetTaglessNotesMCPEndpoint:
    """MCPサーバーのget_tagless_notesエンドポイントテスト"""

    def test_get_tagless_notes_endpoint_should_return_tagless_notes(
        self,
        mock_subprocess_run: Mock,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Given: タグなしノートの出力をモック
        mock_subprocess_run.return_value.stdout = (
            "/path/to/note1.md|タグなしノート1|\n/path/to/note2.md|Note without tags|\n"
        )

        # テスト用インジェクターをモンキーパッチで差し替え
        test_injector = Injector()
        test_injector.binder.bind(GetTaglessNotesService, to=GetTaglessNotesService)

        # When: MCPエンドポイントを呼び出す
        with monkeypatch.context() as mp:
            mp.setattr("zk_utils.presentation.mcp.server.injector", app_injector)
            result = get_tagless_notes()

        # Then: 期待する結果が返されること
        assert hasattr(result, "notes")
        assert len(result.notes) == 2
        assert result.notes[0].title == "タグなしノート1"
        assert result.notes[0].tags == []
        assert result.notes[1].title == "Note without tags"
        assert result.notes[1].tags == []

    def test_get_tagless_notes_endpoint_with_empty_result(
        self,
        mock_subprocess_run: Mock,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Given: 空の結果を返すzkコマンド
        mock_subprocess_run.return_value.stdout = ""

        # When: MCPエンドポイントを呼び出す
        with monkeypatch.context() as mp:
            mp.setattr("zk_utils.presentation.mcp.server.injector", app_injector)
            result = get_tagless_notes()

        # Then: 空のリストが返されること
        assert hasattr(result, "notes")
        assert len(result.notes) == 0

    def test_get_tagless_notes_endpoint_should_use_global_injector(
        self,
        mock_subprocess_run: Mock,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Given: タグなしノートの出力をモック
        mock_subprocess_run.return_value.stdout = "/single.md|単一のタグなしノート|"

        # When: MCPエンドポイントを呼び出す（グローバルインジェクターを使用）
        result = get_tagless_notes()

        # Then: グローバルインジェクターから正しくサービスが取得されること
        assert hasattr(result, "notes")
        assert len(result.notes) == 1
        assert result.notes[0].title == "単一のタグなしノート"

    def test_get_tagless_notes_endpoint_error_handling(
        self,
        mock_failed_subprocess: Mock,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Given: zkコマンドがエラーを返す

        # When & Then: エンドポイントでエラーハンドリングが行われること
        with pytest.raises(RuntimeError, match="Error: zk command failed"):
            get_tagless_notes()


@pytest.mark.integration
class TestGetTaglessNotesMCPIntegration:
    """get_tagless_notes MCP統合テスト"""

    def test_mcp_endpoint_integration_with_dependency_injection(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Given: テスト用DIコンテナとモックされたzkコマンド出力
        mock_subprocess_run.return_value.stdout = (
            "/integration/note1.md|統合テストノート1|\n"
            "/integration/note2.md|統合テストノート2|\n"
            "/integration/note3.md|統合テストノート3|\n"
        )

        # When: MCPエンドポイントを実行（テスト用インジェクター使用）
        with monkeypatch.context() as mp:
            mp.setattr("zk_utils.presentation.mcp.server.injector", test_injector)
            result = get_tagless_notes()

        # Then: 統合テストが正常に動作すること
        assert hasattr(result, "notes")
        assert len(result.notes) == 3
        assert all(note.tags == [] for note in result.notes)
        assert result.notes[0].title == "統合テストノート1"
        assert result.notes[1].title == "統合テストノート2"
        assert result.notes[2].title == "統合テストノート3"

    def test_mcp_endpoint_service_singleton_behavior(
        self,
        test_injector: Injector,
        mock_subprocess_run: Mock,
        monkeypatch: MonkeyPatch,
    ) -> None:
        # Given: テスト用DIコンテナ
        mock_subprocess_run.return_value.stdout = "/test.md|テストノート|"

        # When: MCPエンドポイントを複数回呼び出し
        with monkeypatch.context() as mp:
            mp.setattr("zk_utils.presentation.mcp.server.injector", test_injector)

            # 同じサービスインスタンスが使用されることを確認
            service1 = test_injector.get(GetTaglessNotesService)
            service2 = test_injector.get(GetTaglessNotesService)

            result1 = get_tagless_notes()
            result2 = get_tagless_notes()

        # Then: シングルトンパターンが機能していること
        assert service1 is service2
        assert len(result1.notes) == len(result2.notes) == 1
        assert result1.notes[0].title == result2.notes[0].title == "テストノート"
