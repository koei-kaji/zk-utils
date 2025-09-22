import abc
from typing import Generic, TypeVar

from ..._base_models import BaseFrozenModel


class ABCInput(BaseFrozenModel): ...


class ABCOutput(BaseFrozenModel): ...


T = TypeVar("T", bound=ABCInput)
U = TypeVar("U", bound=ABCOutput)


class ABCService(BaseFrozenModel, Generic[T, U]):
    @abc.abstractmethod
    def handle(self, input_data: T) -> U: ...


class IFQueryService(abc.ABC, BaseFrozenModel): ...
