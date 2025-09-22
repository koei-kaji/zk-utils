from injector import inject, singleton

from ..._abc import ABCInput, ABCOutput, ABCService
from ..._common.tag import Tag
from ..if_tag_query_service import IFTagQueryService


class GetTagsInput(ABCInput): ...


class GetTagsOutput(ABCOutput):
    tags: list[Tag]


@singleton
class GetTagsService(ABCService):
    _query_service: IFTagQueryService

    @inject
    def __init__(self, query_service: IFTagQueryService) -> None:
        super().__init__()
        self._query_service = query_service

    def handle(self, input_data: GetTagsInput) -> GetTagsOutput:
        return self._query_service.get_tags(input_data)
