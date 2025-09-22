from abc import ABC

from ...._base_models import BaseFrozenModel, BaseModel


class Entity(BaseModel): ...


class ValueObject(BaseFrozenModel): ...


class IFRepository(ABC, BaseFrozenModel): ...
