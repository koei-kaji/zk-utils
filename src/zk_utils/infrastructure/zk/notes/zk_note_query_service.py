import math
from typing import TypeVar

from injector import inject, singleton

from ....application._common.note import Note
from ....application._common.pagination import Pagination
from ....application.notes import IFNoteQueryService
from ....application.notes.get_link_to_notes import (
    GetLinkToNotesInput,
    GetLinkToNotesOutput,
)
from ....application.notes.get_linked_by_notes import (
    GetLinkedByNotesInput,
    GetLinkedByNotesOutput,
)
from ....application.notes.get_notes import GetNotesInput, GetNotesOutput
from ....application.notes.get_related_notes import (
    GetRelatedNotesInput,
    GetRelatedNotesOutput,
)
from ..zk_client import ZkClient

T = TypeVar("T")


@singleton
class ZkNoteQueryService(IFNoteQueryService):
    _client: ZkClient

    @inject
    def __init__(self, client: ZkClient) -> None:
        super().__init__()
        self._client = client

    def _paginate(
        self, items: list[T], page: int, per_page: int
    ) -> tuple[list[T], Pagination]:
        total = len(items)
        total_pages = math.ceil(total / per_page) if per_page > 0 else 1

        # ページ番号の正規化
        page = max(1, min(page, total_pages))

        # スライス計算
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_items = items[start_idx:end_idx]

        pagination = Pagination(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )

        return paginated_items, pagination

    def get_notes(self, input_data: GetNotesInput) -> GetNotesOutput:
        # title の検索条件を追加
        title_conditions: list[str] = []
        if len(input_data.title_patterns) > 0:
            title_filters = [f"title: {t}" for t in input_data.title_patterns]
            title_conditions = [
                "--match",
                f" {input_data.title_match_mode} ".join(title_filters),
            ]

        # 全文検索の検索条件を追加
        search_conditions: list[str] = []
        if len(input_data.search_patterns) > 0:
            search_filters = input_data.search_patterns
            search_conditions = [
                "--match",
                f" {input_data.search_match_mode} ".join(search_filters),
            ]

        # tag
        tag_conditions: list[str] = []
        if len(input_data.tags) > 0:
            tag_delimiter = ", " if input_data.tags_match_mode == "AND" else "OR"
            tag_conditions = ["--tag", f"{tag_delimiter}".join(input_data.tags)]

        # created after
        created_after_conditions = []
        if input_data.created_after is not None:
            created_after_conditions = ["--created-after", input_data.created_after]

        # modified after
        modified_after_conditions = []
        if input_data.modified_after is not None:
            modified_after_conditions = ["--modified-after", input_data.modified_after]

        results = self._client.get_notes(
            title_conditions
            + search_conditions
            + tag_conditions
            + created_after_conditions
            + modified_after_conditions
        )

        notes: list[Note] = []
        for result in results:
            note = Note(title=result.title, path=result.path, tags=result.tags)
            notes.append(note)

        paginated_notes, pagination = self._paginate(
            notes, input_data.page, input_data.per_page
        )

        return GetNotesOutput(pagination=pagination, notes=paginated_notes)

    def get_link_to_notes(
        self, input_data: GetLinkToNotesInput
    ) -> GetLinkToNotesOutput:
        results = self._client.get_notes(["--link-to", str(input_data.path)])

        notes: list[Note] = []
        for result in results:
            note = Note(title=result.title, path=result.path, tags=result.tags)
            notes.append(note)

        paginated_notes, pagination = self._paginate(
            notes, input_data.page, input_data.per_page
        )

        return GetLinkToNotesOutput(pagination=pagination, notes=paginated_notes)

    def get_linked_by_notes(
        self, input_data: GetLinkedByNotesInput
    ) -> GetLinkedByNotesOutput:
        results = self._client.get_notes(["--linked-by", str(input_data.path)])

        notes: list[Note] = []
        for result in results:
            note = Note(title=result.title, path=result.path, tags=result.tags)
            notes.append(note)

        paginated_notes, pagination = self._paginate(
            notes, input_data.page, input_data.per_page
        )

        return GetLinkedByNotesOutput(pagination=pagination, notes=paginated_notes)

    def get_related_notes(
        self, input_data: GetRelatedNotesInput
    ) -> GetRelatedNotesOutput:
        results = self._client.get_notes(["--related", str(input_data.path)])

        notes: list[Note] = []
        for result in results:
            note = Note(title=result.title, path=result.path, tags=result.tags)
            notes.append(note)

        paginated_notes, pagination = self._paginate(
            notes, input_data.page, input_data.per_page
        )

        return GetRelatedNotesOutput(pagination=pagination, notes=paginated_notes)
