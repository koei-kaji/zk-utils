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
from zk_utils.application.notes import get_random_note as app_get_random_note
from zk_utils.application.notes import get_related_notes as app_get_related_notes
from zk_utils.application.notes import get_tagless_notes as app_get_tagless_notes
from zk_utils.application.tags import get_tags as app_get_tags
from zk_utils.presentation.injector import injector

mcp = FastMCP("zk-mcp")


@mcp.tool()
def get_notes(
    page: Annotated[int, Field(description="Page number (starting from 1)")] = 1,
    per_page: Annotated[int, Field(description="Number of notes per page")] = 10,
    title_patterns: Annotated[
        list[str], Field(description="Patterns to search in note titles")
    ] = [],
    title_match_mode: Annotated[
        Literal["AND", "OR"], Field(description="Title pattern matching mode (AND/OR)")
    ] = "AND",
    search_patterns: Annotated[
        list[str], Field(description="Patterns to search in note content")
    ] = [],
    search_match_mode: Annotated[
        Literal["AND", "OR"],
        Field(description="Content pattern matching mode (AND/OR)"),
    ] = "AND",
    tags: Annotated[list[str], Field(description="Tags to filter notes by")] = [],
    tags_match_mode: Annotated[
        Literal["AND", "OR"], Field(description="Tag matching mode (AND/OR)")
    ] = "AND",
) -> app_get_notes.GetNotesOutput:
    """Search and retrieve zk notes with filtering and pagination."""
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
    path: Annotated[Path, Field(description="File path to the note")],
) -> app_get_note_content.GetNoteContentOutput:
    """Retrieve the full content of a specific zk note."""
    service = injector.get(app_get_note_content.GetNoteContentService)
    input_data = app_get_note_content.GetNoteContentInput(path=path)
    return service.handle(input_data)


@mcp.tool()
def get_link_to_notes(
    path: Annotated[Path, Field(description="File path to the source note")],
    page: Annotated[int, Field(description="Page number (starting from 1)")] = 1,
    per_page: Annotated[int, Field(description="Number of notes per page")] = 10,
) -> app_get_link_to_notes.GetLinkToNotesOutput:
    """Get all notes that are linked FROM the specified note (outbound links)."""
    service = injector.get(app_get_link_to_notes.GetLinkToNotesService)
    input_data = app_get_link_to_notes.GetLinkToNotesInput(
        page=page, per_page=per_page, path=path
    )
    return service.handle(input_data)


@mcp.tool()
def get_linked_by_notes(
    path: Annotated[Path, Field(description="File path to the target note")],
    page: Annotated[int, Field(description="Page number (starting from 1)")] = 1,
    per_page: Annotated[int, Field(description="Number of notes per page")] = 10,
) -> app_get_linked_by_notes.GetLinkedByNotesOutput:
    """Get all notes that link TO the specified note (inbound links)."""
    service = injector.get(app_get_linked_by_notes.GetLinkedByNotesService)

    input_data = app_get_linked_by_notes.GetLinkedByNotesInput(
        page=page, per_page=per_page, path=path
    )
    return service.handle(input_data)


@mcp.tool()
def get_related_notes(
    path: Annotated[Path, Field(description="File path to the note")],
    page: Annotated[int, Field(description="Page number (starting from 1)")] = 1,
    per_page: Annotated[int, Field(description="Number of notes per page")] = 10,
) -> app_get_related_notes.GetRelatedNotesOutput:
    """Find notes that could be good candidates for linking."""
    service = injector.get(app_get_related_notes.GetRelatedNotesService)
    input_data = app_get_related_notes.GetRelatedNotesInput(
        page=page, per_page=per_page, path=path
    )
    return service.handle(input_data)


@mcp.tool()
def get_tags() -> app_get_tags.GetTagsOutput:
    """Retrieve all available tags from the zk note collection."""
    service = injector.get(app_get_tags.GetTagsService)

    input_data = app_get_tags.GetTagsInput()
    return service.handle(input_data)


@mcp.tool()
def create_note(
    title: Annotated[str, Field(description="Title of the new note")],
    path: Annotated[
        Path, Field(description="File path where the note should be created")
    ],
) -> app_create_note.CreateNoteOutput:
    """Create a new zk note with the specified title and path."""
    service = injector.get(app_create_note.CreateNoteService)

    input_data = app_create_note.CreateNoteInput(title=title, path=path)
    return service.handle(input_data)


@mcp.tool()
def get_last_modified_note() -> app_get_last_modified_note.GetLastModifiedNoteOutput:
    """Retrieve the most recently modified note."""
    service = injector.get(app_get_last_modified_note.GetLastModifiedNoteService)

    input_data = app_get_last_modified_note.GetLastModifiedNoteInput()
    return service.handle(input_data)


@mcp.tool()
def get_tagless_notes() -> app_get_tagless_notes.GetTaglessNotesOutput:
    """Retrieve all notes that have no tags assigned."""
    service = injector.get(app_get_tagless_notes.GetTaglessNotesService)

    input_data = app_get_tagless_notes.GetTaglessNotesInput()
    return service.handle(input_data)


@mcp.tool()
def get_random_note() -> app_get_random_note.GetRandomNoteOutput:
    """Retrieve a randomly selected note from the zk collection."""
    service = injector.get(app_get_random_note.GetRandomNoteService)

    input_data = app_get_random_note.GetRandomNoteInput()
    return service.handle(input_data)


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
