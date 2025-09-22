from pathlib import Path

import pytest
from injector import Injector

from zk_utils.application.notes.create_note import CreateNoteService
from zk_utils.application.notes.get_link_to_notes import GetLinkToNotesService
from zk_utils.application.notes.get_linked_by_notes import GetLinkedByNotesService
from zk_utils.application.notes.get_note_content import GetNoteContentService
from zk_utils.application.notes.get_notes import GetNotesService
from zk_utils.application.notes.get_related_notes import GetRelatedNotesService
from zk_utils.application.tags.get_tags import GetTagsService
from zk_utils.domain.models.notes import IFNoteRepository
from zk_utils.infrastructure.zk.notes.zk_note_query_service import ZkNoteQueryService
from zk_utils.infrastructure.zk.notes.zk_note_repository import ZkNoteRepository
from zk_utils.infrastructure.zk.tags.zk_tag_query_service import ZkTagQueryService
from zk_utils.infrastructure.zk.zk_client import ZkClient
from zk_utils.presentation.injector import injector as app_injector


@pytest.mark.integration
class TestInjectorConfiguration:
    """DIコンテナの設定と依存関係解決テスト"""

    def test_injector_should_be_configured_correctly(
        self,
        test_injector: Injector,
    ) -> None:
        # Given: DIコンテナ

        # When & Then: インジェクターが正しく設定されていること
        assert test_injector is not None
        assert isinstance(test_injector, Injector)

    def test_zk_client_should_be_resolvable_as_singleton(
        self,
        test_injector: Injector,
    ) -> None:
        # Given: DIコンテナ

        # When: ZkClientを複数回取得
        client1 = test_injector.get(ZkClient)
        client2 = test_injector.get(ZkClient)

        # Then: 同一インスタンスが返されること（シングルトン）
        assert isinstance(client1, ZkClient)
        assert isinstance(client2, ZkClient)
        assert client1 is client2

    def test_zk_client_should_have_correct_cwd_configuration(
        self,
        test_injector: Injector,
    ) -> None:
        # Given: DIコンテナ

        # When: ZkClientを取得
        client = test_injector.get(ZkClient)

        # Then: cwdが設定されていること
        assert hasattr(client, "_cwd")
        assert isinstance(client._cwd, Path)


@pytest.mark.integration
class TestNoteServicesDependencyResolution:
    """ノート関連サービスの依存関係解決テスト"""

    def test_get_notes_service_should_be_resolvable_with_dependencies(
        self,
        test_injector: Injector,
    ) -> None:
        # Given: DIコンテナ

        # When: GetNotesServiceを取得
        service = test_injector.get(GetNotesService)

        # Then: 正しく依存関係が解決されること
        assert isinstance(service, GetNotesService)
        assert hasattr(service, "_query_service")
        assert isinstance(service._query_service, ZkNoteQueryService)

    def test_get_note_content_service_should_be_resolvable_with_dependencies(
        self,
        test_injector: Injector,
    ) -> None:
        # Given: DIコンテナ

        # When: GetNoteContentServiceを取得
        service = test_injector.get(GetNoteContentService)

        # Then: 正しく依存関係が解決されること
        assert isinstance(service, GetNoteContentService)
        assert hasattr(service, "_repository")
        assert isinstance(service._repository, ZkNoteRepository)

    def test_create_note_service_should_be_resolvable_with_dependencies(
        self,
        test_injector: Injector,
    ) -> None:
        # Given: DIコンテナ

        # When: CreateNoteServiceを取得
        service = test_injector.get(CreateNoteService)

        # Then: 正しく依存関係が解決されること
        assert isinstance(service, CreateNoteService)
        assert hasattr(service, "_repository")
        assert isinstance(service._repository, IFNoteRepository)

    def test_get_link_to_notes_service_should_be_resolvable_with_dependencies(
        self,
        test_injector: Injector,
    ) -> None:
        # Given: DIコンテナ

        # When: GetLinkToNotesServiceを取得
        service = test_injector.get(GetLinkToNotesService)

        # Then: 正しく依存関係が解決されること
        assert isinstance(service, GetLinkToNotesService)
        assert hasattr(service, "_query_service")
        assert isinstance(service._query_service, ZkNoteQueryService)

    def test_get_linked_by_notes_service_should_be_resolvable_with_dependencies(
        self,
        test_injector: Injector,
    ) -> None:
        # Given: DIコンテナ

        # When: GetLinkedByNotesServiceを取得
        service = test_injector.get(GetLinkedByNotesService)

        # Then: 正しく依存関係が解決されること
        assert isinstance(service, GetLinkedByNotesService)
        assert hasattr(service, "_query_service")
        assert isinstance(service._query_service, ZkNoteQueryService)

    def test_get_related_notes_service_should_be_resolvable_with_dependencies(
        self,
        test_injector: Injector,
    ) -> None:
        # Given: DIコンテナ

        # When: GetRelatedNotesServiceを取得
        service = test_injector.get(GetRelatedNotesService)

        # Then: 正しく依存関係が解決されること
        assert isinstance(service, GetRelatedNotesService)
        assert hasattr(service, "_query_service")
        assert isinstance(service._query_service, ZkNoteQueryService)


@pytest.mark.integration
class TestTagServicesDependencyResolution:
    """タグ関連サービスの依存関係解決テスト"""

    def test_get_tags_service_should_be_resolvable_with_dependencies(
        self,
        test_injector: Injector,
    ) -> None:
        # Given: DIコンテナ

        # When: GetTagsServiceを取得
        service = test_injector.get(GetTagsService)

        # Then: 正しく依存関係が解決されること
        assert isinstance(service, GetTagsService)
        assert hasattr(service, "_query_service")
        assert isinstance(service._query_service, ZkTagQueryService)


@pytest.mark.integration
class TestInfrastructureServicesDependencyResolution:
    """インフラ層サービスの依存関係解決テスト"""

    def test_zk_note_query_service_should_be_resolvable_with_dependencies(
        self,
        test_injector: Injector,
    ) -> None:
        # Given: DIコンテナ

        # When: ZkNoteQueryServiceを取得
        service = test_injector.get(ZkNoteQueryService)

        # Then: 正しく依存関係が解決されること
        assert isinstance(service, ZkNoteQueryService)
        assert hasattr(service, "_client")
        assert isinstance(service._client, ZkClient)

    def test_zk_note_repository_should_be_resolvable_with_dependencies(
        self,
        test_injector: Injector,
    ) -> None:
        # Given: DIコンテナ

        # When: ZkNoteRepositoryを取得
        repository = test_injector.get(ZkNoteRepository)

        # Then: 正しく依存関係が解決されること
        assert isinstance(repository, ZkNoteRepository)
        assert hasattr(repository, "_client")
        assert isinstance(repository._client, ZkClient)

    def test_zk_tag_query_service_should_be_resolvable_with_dependencies(
        self,
        test_injector: Injector,
    ) -> None:
        # Given: DIコンテナ

        # When: ZkTagQueryServiceを取得
        service = test_injector.get(ZkTagQueryService)

        # Then: 正しく依存関係が解決されること
        assert isinstance(service, ZkTagQueryService)
        assert hasattr(service, "_client")
        assert isinstance(service._client, ZkClient)


@pytest.mark.integration
class TestSingletonBehavior:
    """シングルトンパターンの動作テスト"""

    def test_application_services_should_be_singleton(
        self,
        test_injector: Injector,
    ) -> None:
        # Given: DIコンテナ

        # When: 同じサービスを複数回取得
        service1 = test_injector.get(GetNotesService)
        service2 = test_injector.get(GetNotesService)

        # Then: 同一インスタンスが返されること
        assert service1 is service2

    def test_infrastructure_services_should_be_singleton(
        self,
        test_injector: Injector,
    ) -> None:
        # Given: DIコンテナ

        # When: 同じインフラサービスを複数回取得
        service1 = test_injector.get(ZkNoteQueryService)
        service2 = test_injector.get(ZkNoteQueryService)

        # Then: 同一インスタンスが返されること
        assert service1 is service2

    def test_shared_dependencies_should_be_same_instance(
        self,
        test_injector: Injector,
    ) -> None:
        # Given: DIコンテナ

        # When: 複数のサービスが共有する依存関係を確認
        notes_service = test_injector.get(GetNotesService)
        content_service = test_injector.get(GetNoteContentService)

        notes_query_service = notes_service._query_service
        content_repository = content_service._repository

        # ZkClientが共有されていることを確認
        notes_client = notes_query_service._client  # type: ignore[attr-defined]
        content_client = content_repository._client  # type: ignore[attr-defined]

        # Then: 同一のZkClientインスタンスが使用されること
        assert notes_client is content_client


@pytest.mark.integration
class TestInterfaceImplementationBinding:
    """インターフェースと実装のバインディングテスト"""

    def test_note_repository_interface_should_be_bound_to_zk_implementation(
        self,
        test_injector: Injector,
    ) -> None:
        # Given: DIコンテナ

        # When: IFNoteRepositoryインターフェースを要求
        repository = test_injector.get(IFNoteRepository)  # type: ignore[type-abstract]

        # Then: ZkNoteRepositoryの実装が返されること
        assert isinstance(repository, ZkNoteRepository)

    def test_services_should_use_correct_implementation_bindings(
        self,
        test_injector: Injector,
    ) -> None:
        # Given: DIコンテナ

        # When: 各サービスの依存関係を確認
        create_service = test_injector.get(CreateNoteService)
        content_service = test_injector.get(GetNoteContentService)

        # Then: 正しい実装がバインドされていること
        assert isinstance(create_service._repository, ZkNoteRepository)
        assert isinstance(content_service._repository, ZkNoteRepository)


@pytest.mark.integration
class TestGlobalInjectorIntegration:
    """グローバルインジェクターとの統合テスト"""

    def test_global_injector_should_be_accessible(self) -> None:
        # Given: グローバルインジェクター

        # When & Then: アプリケーションのインジェクターにアクセス可能なこと
        assert app_injector is not None
        assert isinstance(app_injector, Injector)

    def test_global_injector_should_resolve_services_correctly(self) -> None:
        # Given: グローバルインジェクター

        # When: グローバルインジェクターからサービスを取得
        service = app_injector.get(GetNotesService)

        # Then: 正しくサービスが解決されること
        assert isinstance(service, GetNotesService)
        assert hasattr(service, "_query_service")
