from pathlib import Path
from typing import Annotated, Literal

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from zk_utils.application.notes import create_note as app_create_note
from zk_utils.application.notes import (
    get_last_modified_note as app_get_last_modified_note,
)
from zk_utils.application.notes import get_link_to_notes as app_get_link_to_notes
from zk_utils.application.notes import get_linked_by_notes as app_get_linked_by_notes
from zk_utils.application.notes import get_note_content as app_get_note_content
from zk_utils.application.notes import get_notes as app_get_notes
from zk_utils.application.notes import get_related_notes as app_get_related_notes
from zk_utils.application.tags import get_tags as app_get_tags
from zk_utils.presentation.injector import injector

mcp = FastMCP("zk-mcp")


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
) -> app_get_notes.GetNotesOutput:
    """
    Search and retrieve a list of zk notes.

    This function allows you to search notes using multiple criteria
    (title, content, tags) and returns paginated results. You can combine
    different search conditions to narrow down the results effectively.

    Returns:
        GetNotesOutput: Search results
    """
    service = injector.get(app_get_notes.GetNotesService)

    input = app_get_notes.GetNotesInput(
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
) -> app_get_note_content.GetNoteContentOutput:
    """
    Retrieve the full content of a specific zk note.

    Given a note's file path, this function returns the complete content of the note
    including its title, content body, tags, and metadata.

    Args:
        path: The file path to the note you want to read

    Returns:
        GetNoteContentOutput: Note content
    """
    service = injector.get(app_get_note_content.GetNoteContentService)
    input_data = app_get_note_content.GetNoteContentInput(path=path)
    return service.handle(input_data)


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
) -> app_get_link_to_notes.GetLinkToNotesOutput:
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
        GetLinkToNotesOutput: Linking notes
    """
    service = injector.get(app_get_link_to_notes.GetLinkToNotesService)
    input_data = app_get_link_to_notes.GetLinkToNotesInput(
        page=page, per_page=per_page, path=path
    )
    return service.handle(input_data)


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
) -> app_get_linked_by_notes.GetLinkedByNotesOutput:
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
        GetLinkedByNotesOutput: Linking notes
    """
    service = injector.get(app_get_linked_by_notes.GetLinkedByNotesService)

    input_data = app_get_linked_by_notes.GetLinkedByNotesInput(
        page=page, per_page=per_page, path=path
    )
    return service.handle(input_data)


@mcp.tool()
def get_related_notes(
    path: Annotated[
        Path,
        Field(
            description="File path to the note for finding link candidates "
            "(e.g., 'notes/my-note.md')"
        ),
    ],
    page: Annotated[
        int, Field(description="Page number (starting from 1) for pagination")
    ] = 1,
    per_page: Annotated[
        int,
        Field(
            description="Number of link candidates to return per page. Default is 10."
        ),
    ] = 10,
) -> app_get_related_notes.GetRelatedNotesOutput:
    """
    Find notes that could be good candidates for linking to the specified note.

    This function returns notes which are not connected to the given note,
    but with at least one linked note in common. It helps discover potential
    connections between notes in your notebook, making it easier to create
    meaningful links and improve note organization.

    Args:
        path: The file path of the note to find link candidates for
        page: Page number for pagination (starting from 1)
        per_page: Number of results per page

    Returns:
        GetRelatedNotesOutput: Notes that could be linked to the specified note
    """
    service = injector.get(app_get_related_notes.GetRelatedNotesService)
    input_data = app_get_related_notes.GetRelatedNotesInput(
        page=page, per_page=per_page, path=path
    )
    return service.handle(input_data)


@mcp.tool()
def get_tags() -> app_get_tags.GetTagsOutput:
    """
    Retrieve all available tags from the zk note collection.

    This function returns a comprehensive list of all tags that are currently
    used across all notes in the zk system. This is useful for discovering
    available tags for filtering or organizing notes.

    Returns:
        GetTagsOutput: All available tags
    """
    service = injector.get(app_get_tags.GetTagsService)

    input_data = app_get_tags.GetTagsInput()
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
) -> app_create_note.CreateNoteOutput:
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
        CreateNoteOutput: created note
    """
    service = injector.get(app_create_note.CreateNoteService)

    input_data = app_create_note.CreateNoteInput(title=title, path=path)
    return service.handle(input_data)


@mcp.tool()
def get_last_modified_note() -> app_get_last_modified_note.GetLastModifiedNoteOutput:
    """ """
    service = injector.get(app_get_last_modified_note.GetLastModifiedNoteService)

    input_data = app_get_last_modified_note.GetLastModifiedNoteInput()
    return service.handle(input_data)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
