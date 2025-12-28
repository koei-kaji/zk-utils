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

- `get_notes`: Search and retrieve zk notes with filtering and pagination
- `get_note_content`: Retrieve the full content of a specific zk note
- `get_link_to_notes`: Get all notes that are linked FROM the specified note (outbound links)
- `get_linked_by_notes`: Get all notes that link TO the specified note (inbound links)
- `get_related_notes`: Find notes that could be good candidates for linking
- `get_tags`: Retrieve all available tags from the zk note collection
- `create_note`: Create a new zk note with the specified title and path
- `get_last_modified_note`: Retrieve the most recently modified note
- `get_tagless_notes`: Retrieve all notes that have no tags assigned
- `get_random_note`: Retrieve a randomly selected note from the zk collection

## Environment Variables

- `ZK_DIR`: Path to zk notes directory (required)
