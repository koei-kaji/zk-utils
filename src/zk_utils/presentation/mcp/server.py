from pathlib import Path
from typing import Annotated, Literal

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from zk_utils.application.notes.create_note import (
    CreateNoteInput,
    CreateNoteOutput,
    CreateNoteService,
)
from zk_utils.application.notes.get_link_to_notes import (
    GetLinkToNotesInput,
    GetLinkToNotesOutput,
    GetLinkToNotesService,
)
from zk_utils.application.notes.get_linked_by_notes import (
    GetLinkedByNotesInput,
    GetLinkedByNotesOutput,
    GetLinkedByNotesService,
)
from zk_utils.application.notes.get_note_content import (
    GetNoteContentInput,
    GetNoteContentOutput,
    GetNoteContentService,
)
from zk_utils.application.notes.get_notes import (
    GetNotesInput,
    GetNotesOutput,
    GetNotesService,
)
from zk_utils.application.notes.get_related_notes import (
    GetRelatedNotesInput,
    GetRelatedNotesOutput,
    GetRelatedNotesService,
)
from zk_utils.application.tags.get_tags import (
    GetTagsInput,
    GetTagsOutput,
    GetTagsService,
)
from zk_utils.presentation.injector import injector

mcp = FastMCP("Zk")


@mcp.tool()
def get_notes(
    page: Annotated[
        int,
        Field(
            description="Page number (starting from 1) for pagination. "
            "Use this to retrieve results in chunks."
        ),
    ] = 1,
    per_page: Annotated[
        int, Field(description="Number of notes to return per page. Default is 10.")
    ] = 10,
    title_patterns: Annotated[
        list[str],
        Field(
            description="List of patterns to search in note titles. "
            "Example: ['meeting', 'project']"
        ),
    ] = [],
    title_match_mode: Annotated[
        Literal["AND", "OR"],
        Field(
            description="Matching mode for title patterns. "
            "AND: all patterns must match, OR: any pattern matches"
        ),
    ] = "AND",
    search_patterns: Annotated[
        list[str],
        Field(
            description="List of patterns to search in note content. "
            "Example: ['Python', 'API']"
        ),
    ] = [],
    search_match_mode: Annotated[
        Literal["AND", "OR"],
        Field(
            description="Matching mode for content search patterns. "
            "AND: all patterns must match, OR: any pattern matches"
        ),
    ] = "AND",
    tags: Annotated[
        list[str],
        Field(
            description="List of tags to filter notes by. "
            "Example: ['work', 'important']"
        ),
    ] = [],
    tags_match_mode: Annotated[
        Literal["AND", "OR"],
        Field(
            description="Tag matching mode. "
            "AND: notes must have all specified tags, OR: notes with any of the tags"
        ),
    ] = "AND",
) -> GetNotesOutput:
    """
    Search and retrieve a list of zk notes.

    This function allows you to search notes using multiple criteria
    (title, content, tags) and returns paginated results. You can combine
    different search conditions to narrow down the results effectively.

    Returns:
        GetNotesOutput: Search results containing:
            - notes: List of notes (containing title, path, tags,
              created_at, updated_at)
            - total_count: Total number of matching notes
            - page: Current page number
            - per_page: Number of notes per page
            - total_pages: Total number of pages
    """
    service = injector.get(GetNotesService)

    input = GetNotesInput(
        page=page,
        per_page=per_page,
        title_patterns=title_patterns,
        title_match_mode=title_match_mode,
        search_patterns=search_patterns,
        search_match_mode=search_match_mode,
        tags=tags,
        tags_match_mode=tags_match_mode,
    )
    return service.handle(input)


@mcp.tool()
def get_note_content(
    path: Annotated[
        Path,
        Field(
            description="File path to the note "
            "(e.g., 'notes/my-note.md' or '/absolute/path/to/note.md')"
        ),
    ],
) -> GetNoteContentOutput:
    """
    Retrieve the full content of a specific zk note.

    Given a note's file path, this function returns the complete content of the note
    including its title, content body, tags, and metadata.

    Args:
        path: The file path to the note you want to read

    Returns:
        GetNoteContentOutput: Note content containing:
            - title: The note's title
            - content: The full content/body of the note
            - path: The file path of the note
            - tags: List of tags associated with the note
            - created_at: Note creation timestamp
            - updated_at: Last modification timestamp
    """
    service = injector.get(GetNoteContentService)
    input = GetNoteContentInput(path=path)
    return service.handle(input)


@mcp.tool()
def get_link_to_notes(
    path: Annotated[
        Path,
        Field(description="File path to the source note (e.g., 'notes/my-note.md')"),
    ],
    page: Annotated[
        int, Field(description="Page number (starting from 1) for pagination")
    ] = 1,
    per_page: Annotated[
        int,
        Field(description="Number of linked notes to return per page. Default is 10."),
    ] = 10,
) -> GetLinkToNotesOutput:
    """
    Get all notes that are linked FROM the specified note.

    This function finds all the notes that the given note links to (outbound links).
    For example, if note A contains links to notes B and C, calling this function
    with note A's path will return notes B and C.

    Args:
        path: The file path of the source note to analyze for outbound links
        page: Page number for pagination (starting from 1)
        per_page: Number of results per page

    Returns:
        GetLinkToNotesOutput: Paginated list of linked notes containing:
            - notes: List of notes that are linked to from the source note
            - total_count: Total number of outbound links
            - page: Current page number
            - per_page: Number of notes per page
            - total_pages: Total number of pages
    """
    service = injector.get(GetLinkToNotesService)
    input = GetLinkToNotesInput(page=page, per_page=per_page, path=path)
    return service.handle(input)


@mcp.tool()
def get_linked_by_notes(
    path: Annotated[
        Path,
        Field(description="File path to the target note (e.g., 'notes/my-note.md')"),
    ],
    page: Annotated[
        int, Field(description="Page number (starting from 1) for pagination")
    ] = 1,
    per_page: Annotated[
        int,
        Field(description="Number of linking notes to return per page. Default is 10."),
    ] = 10,
) -> GetLinkedByNotesOutput:
    """
    Get all notes that link TO the specified note.

    This function finds all the notes that contain links to the given note
    (inbound links). For example, if notes B and C contain links to note A,
    calling this function with note A's path will return notes B and C.

    Args:
        path: The file path of the target note to find inbound links to
        page: Page number for pagination (starting from 1)
        per_page: Number of results per page

    Returns:
        GetLinkedByNotesOutput: Paginated list of notes that link to the target note
            containing:
            - notes: List of notes that contain links to the target note
            - total_count: Total number of inbound links
            - page: Current page number
            - per_page: Number of notes per page
            - total_pages: Total number of pages
    """
    service = injector.get(GetLinkedByNotesService)

    input_data = GetLinkedByNotesInput(page=page, per_page=per_page, path=path)
    return service.handle(input_data)


@mcp.tool()
def get_related_notes(
    path: Annotated[
        Path,
        Field(
            description="File path to the note for finding related content "
            "(e.g., 'notes/my-note.md')"
        ),
    ],
    page: Annotated[
        int, Field(description="Page number (starting from 1) for pagination")
    ] = 1,
    per_page: Annotated[
        int,
        Field(description="Number of related notes to return per page. Default is 10."),
    ] = 10,
) -> GetRelatedNotesOutput:
    """
    Find notes that are related to the specified note.

    This function discovers notes that are semantically or topically
    related to the given note. Related notes are typically found based on
    shared tags, similar content, or other relationship indicators beyond
    direct linking.

    Args:
        path: The file path of the note to find related content for
        page: Page number for pagination (starting from 1)
        per_page: Number of results per page

    Returns:
        GetRelatedNotesOutput: Paginated list of related notes containing:
            - notes: List of notes that are related to the source note
            - total_count: Total number of related notes found
            - page: Current page number
            - per_page: Number of notes per page
            - total_pages: Total number of pages
    """
    service = injector.get(GetRelatedNotesService)
    input_data = GetRelatedNotesInput(page=page, per_page=per_page, path=path)
    return service.handle(input_data)


@mcp.tool()
def get_tags() -> GetTagsOutput:
    """
    Retrieve all available tags from the zk note collection.

    This function returns a comprehensive list of all tags that are currently
    used across all notes in the zk system. This is useful for discovering
    available tags for filtering or organizing notes.

    Returns:
        GetTagsOutput: All available tags containing:
            - tags: List of all tag names used in the note collection
            - count: Number of unique tags available
    """
    service = injector.get(GetTagsService)

    input_data = GetTagsInput()
    return service.handle(input_data)


@mcp.tool()
def create_note(
    title: Annotated[
        str,
        Field(
            description="Title of the new note (e.g., 'Meeting Notes - Project Alpha')"
        ),
    ],
    path: Annotated[
        Path,
        Field(
            description="File path where the note should be created "
            "(e.g., 'notes/meeting-notes.md')"
        ),
    ],
) -> CreateNoteOutput:
    """
    Create a new zk note with the specified title and path.

    This function creates a new note file in the zk system with the given title
    and saves it to the specified path. The note will be initialized with
    basic structure and metadata.

    Args:
        title: The title/heading for the new note
        path: The file path where the note should be created
              (including filename and extension)

    Returns:
        CreateNoteOutput: Information about the created note containing:
            - title: The note's title
            - path: The file path where the note was created
            - created_at: Timestamp when the note was created
            - success: Boolean indicating if creation was successful

    Raises:
        Exception: If the note cannot be created
                  (e.g., path already exists, permission issues)
    """
    service = injector.get(CreateNoteService)

    input_data = CreateNoteInput(title=title, path=path)
    return service.handle(input_data)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
