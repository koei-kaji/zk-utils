from pathlib import Path

from zk_utils.infrastructure.zk.zk_client import ZkClient


class TestZkClientInitialization:
    """ZkClientの初期化テスト"""

    def test_create_zk_client_with_valid_path(self) -> None:
        # Given: 有効なパス
        cwd = Path("/test/path")

        # When: ZkClientインスタンスを作成する
        client = ZkClient(cwd=cwd)

        # Then: 正常にインスタンスが作成されること
        assert client._cwd == cwd
