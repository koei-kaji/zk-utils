from pathlib import Path
from typing import Annotated, Literal

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from zk_utils.application.notes.create_note import CreateNoteInput, CreateNoteService
from zk_utils.application.notes.get_link_to_notes import (
    GetLinkToNotesInput,
    GetLinkToNotesService,
)
from zk_utils.application.notes.get_linked_by_notes import (
    GetLinkedByNotesInput,
    GetLinkedByNotesService,
)
from zk_utils.application.notes.get_note_content import (
    GetNoteContentInput,
    GetNoteContentService,
)
from zk_utils.application.notes.get_notes import GetNotesInput, GetNotesService
from zk_utils.application.notes.get_related_notes import (
    GetRelatedNotesInput,
    GetRelatedNotesService,
)
from zk_utils.application.tags.get_tags import GetTagsInput, GetTagsService
from zk_utils.presentation.injector import injector

mcp = FastMCP("Zk")


@mcp.tool()
def get_notes(
    page: Annotated[int, Field(description="page")] = 1,
    per_page: Annotated[int, Field(description="per_page")] = 10,
    title_patterns: Annotated[list[str], Field(description="title_patterns")] = [],
    title_match_mode: Annotated[
        Literal["AND", "OR"], Field(description="match_mode")
    ] = "AND",
    search_patterns: Annotated[list[str], Field(description="search_patterns")] = [],
    search_match_mode: Annotated[
        Literal["AND", "OR"], Field(description="match_mode")
    ] = "AND",
    tags: Annotated[list[str], Field(description="tags")] = [],
    tags_match_mode: Annotated[
        Literal["AND", "OR"], Field(description="match_mode")
    ] = "AND",
) -> dict:
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
    output = service.handle(input)

    return output.model_dump()


@mcp.tool()
def get_note_content(path: Annotated[Path, Field(description="path")]) -> dict:
    service = injector.get(GetNoteContentService)
    input = GetNoteContentInput(path=path)
    output = service.handle(input)

    return output.model_dump()


@mcp.tool()
def get_link_to_notes(
    path: Annotated[Path, Field(description="path")],
    page: Annotated[int, Field(description="page")] = 1,
    per_page: Annotated[int, Field(description="per_page")] = 10,
) -> dict:
    service = injector.get(GetLinkToNotesService)
    input = GetLinkToNotesInput(page=page, per_page=per_page, path=path)
    output = service.handle(input)

    return output.model_dump()


@mcp.tool()
def get_linked_by_notes(
    path: Annotated[Path, Field(description="path")],
    page: Annotated[int, Field(description="page")] = 1,
    per_page: Annotated[int, Field(description="per_page")] = 10,
) -> dict:
    service = injector.get(GetLinkedByNotesService)

    input_data = GetLinkedByNotesInput(page=page, per_page=per_page, path=path)
    output = service.handle(input_data)

    return output.model_dump()


@mcp.tool()
def get_related_notes(
    path: Annotated[Path, Field(description="path")],
    page: Annotated[int, Field(description="page")] = 1,
    per_page: Annotated[int, Field(description="per_page")] = 10,
) -> dict:
    service = injector.get(GetRelatedNotesService)
    input_data = GetRelatedNotesInput(page=page, per_page=per_page, path=path)
    output = service.handle(input_data)

    return output.model_dump()


@mcp.tool()
def get_tags() -> dict:
    service = injector.get(GetTagsService)

    input_data = GetTagsInput()
    output = service.handle(input_data)

    return output.model_dump()


@mcp.tool()
def create_note(
    title: Annotated[str, Field(description="title")],
    path: Annotated[Path, Field(description="path")],
) -> dict:
    service = injector.get(CreateNoteService)

    input_data = CreateNoteInput(title=title, path=path)
    output = service.handle(input_data)

    return output.model_dump()


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
