# Docker使用ガイド

このドキュメントでは、zk-utilsをDockerで実行する方法を説明します。

## 前提条件

- Docker
- Docker Compose（オプション）
- ホストマシンにzkノートディレクトリが存在すること

## ビルド

```bash
docker build -t zk-utils-mcp .
```

## 実行方法

### 方法1: docker runを使用

```bash
docker run -it --rm \
  -v /path/to/your/zk-notes:/zk-notes:ro \
  -e ZK_DIR=/zk-notes \
  zk-utils-mcp
```

### 方法2: docker-composeを使用

1. 環境変数を設定（オプション）:

```bash
export ZK_NOTES_DIR=/path/to/your/zk-notes
```

または、`.env`ファイルを作成:

```env
ZK_NOTES_DIR=/path/to/your/zk-notes
```

2. コンテナを起動:

```bash
docker-compose up
```

## 環境変数

- `ZK_DIR`: zkノートディレクトリのパス（コンテナ内のパス、デフォルト: `/zk-notes`）
- `ZK_NOTES_DIR`: ホストマシンのzkノートディレクトリ（docker-compose.yml用、デフォルト: `./zk-notes`）

## ボリュームマウント

zkノートディレクトリは読み取り専用（`:ro`）でマウントされます。MCPサーバーはノートの読み取りとリンク解析を行いますが、ノートの変更は行いません。

ノートの作成機能を使用する場合は、読み取り専用フラグを削除してください:

```bash
docker run -it --rm \
  -v /path/to/your/zk-notes:/zk-notes \
  -e ZK_DIR=/zk-notes \
  zk-utils-mcp
```

## MCPクライアントとの接続

MCPサーバーはstdio transportで動作するため、Claudeデスクトップアプリなどのクライアントから接続する際は、dockerコマンドをMCPサーバーのコマンドとして設定します。

例（Claude desktop設定）:

```json
{
  "mcpServers": {
    "zk-utils": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-v",
        "/path/to/your/zk-notes:/zk-notes:ro",
        "-e",
        "ZK_DIR=/zk-notes",
        "zk-utils-mcp"
      ]
    }
  }
}
```

## トラブルシューティング

### zkコマンドが見つからない

コンテナ内でzkが正しくインストールされているか確認:

```bash
docker run --rm zk-utils-mcp zk --version
```

### ZK_DIRが正しく設定されていない

環境変数とボリュームマウントが正しく設定されているか確認:

```bash
docker run --rm \
  -v /path/to/your/zk-notes:/zk-notes:ro \
  -e ZK_DIR=/zk-notes \
  zk-utils-mcp \
  sh -c 'echo $ZK_DIR && ls -la /zk-notes'
```
