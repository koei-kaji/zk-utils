# zk-utils

zk-utils is an MCP (Model Context Protocol) server for zk note management tools. It provides functionality for note search, creation, and link analysis by integrating with zk.

## Prerequisites

- [zk](https://github.com/zk-org/zk) command line tool

## Usage


### MCP Configuration

Add the following to mcp configuration file:

```json
{
  "mcpServers": {
    "zk-mcp": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/koei-kaji/zk-utils", "zk-utils-mcp"],
      "env": {
        "ZK_DIR": "/path/to/your/notes"
      }
    }
  }
}
```

## Available MCP Tools

- `get_notes`: Get note list (with pagination, search, and tag filtering)
- `get_note_content`: Get content of specified note
- `get_link_to_notes`: Get notes linked from specified note
- `get_linked_by_notes`: Get notes linking to specified note
- `get_related_notes`: Get related notes
- `get_tags`: Get tag list
- `create_note`: Create new note

## Environment Variables

- `ZK_DIR`: Path to zk notes directory (required)
