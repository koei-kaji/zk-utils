from injector import inject, singleton

from ....application._common.tag import Tag
from ....application.tags import IFTagQueryService
from ....application.tags.get_tags import GetTagsInput, GetTagsOutput
from ..zk_client import ZkClient


@singleton
class ZkTagQueryService(IFTagQueryService):
    _client: ZkClient

    @inject
    def __init__(self, client: ZkClient) -> None:
        super().__init__()
        self._client = client

    def get_tags(self, input_data: GetTagsInput) -> GetTagsOutput:
        results = self._client.get_tags()

        tags: list[Tag] = []
        for result in results:
            tag = Tag(name=result.name, note_count=result.note_count)
            tags.append(tag)

        return GetTagsOutput(tags=tags)
