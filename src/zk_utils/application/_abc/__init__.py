import abc

from ..._base_models import BaseFrozenModel


class ABCInput(BaseFrozenModel): ...


class ABCOutput(BaseFrozenModel): ...


class ABCService(BaseFrozenModel):
    @abc.abstractmethod
    def handle(self, input_data: ABCInput) -> ABCOutput: ...


class IFQueryService(abc.ABC, BaseFrozenModel): ...
