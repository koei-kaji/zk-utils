"""テスト用の共通設定"""

import os
import tempfile

# テスト実行前にZK_DIR環境変数を設定
os.environ.setdefault("ZK_DIR", tempfile.mkdtemp())
