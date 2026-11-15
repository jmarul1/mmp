from abc import ABC, abstractmethod


class Mapper[Raw, Entity](ABC):
    @classmethod
    @abstractmethod
    def map(cls, raw: Raw) -> Entity:
        raise NotImplementedError
