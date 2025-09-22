import abc
from typing import TYPE_CHECKING

from .._abc import IFQueryService

if TYPE_CHECKING:
    from .get_tags import GetTagsInput, GetTagsOutput


class IFTagQueryService(IFQueryService):
    @abc.abstractmethod
    def get_tags(self, input_data: "GetTagsInput") -> "GetTagsOutput": ...
