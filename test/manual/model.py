from abc import ABC, abstractmethod
from enum import Enum
from numbers import Real
from typing import Type


class Maturity(Enum):
    CUB = 0
    YOUNG = 1
    ADULT = 2
    OLD = 3


class Creature:
    def __init__(self, kind: 'Kind', name: str):
        self.kind = kind
        self.name = name
        self.age: int = 0
        self.mature: Maturity = Maturity.CUB
        self.params: dict[Type, Parameter] = {
            cls: cls(param.value, param.min, param.max, self)
            for cls, param in kind.value[self.mature].params.items()
        }
        self.history: History = History()

    def update(self):
        for param in self.params.values():
            param.update()

    def _grow_up(self, new_mature: Maturity):
        # Maturity(self.mature.value + 1)
        for cls, param in self.kind.value[new_mature].params.items():
            self.params[cls].min = param.min
            self.params[cls].max = param.max

    def save(self):
        state = State(self.age)
        for param in self.params.values():
            setattr(state, param.__class__.__name__, param.value)
        self.history.append(state)

    def __repr__(self):
        return f"<{self.name}: {'/'.join(f'{p.value:.1f}' for p in self.params.values())}>"


class History(list):
    def get_param_history(self, param_name: str) -> tuple[float, ...]:
        return tuple(
            getattr(state, param_name)
            for state in self
        )


class State:
    """
    Хранитель.
    Атрибуты экземпляра формируются динамически.
    """
    def __init__(self, age: int):
        self.age = age

    def __repr__(self):
        return f"<{'/'.join(f'{v}' for v in self.__dict__.values())}>"


class Parameter(ABC):
    def __init__(
            self,
            value: float,
            min_: float,
            max_: float,
            origin: Creature = None,
    ):
        if min_ <= value <= max_:
            self.__value = value
        else:
            raise ValueError
        self.min = min_
        self.max = max_
        self.origin = origin

    @property
    def range(self):
        return self.min, self.max

    @property
    def value(self) -> float:
        return self.__value

    @value.setter
    def value(self, number: float):
        if isinstance(number, Real):
            if number < self.min:
                self.__value = self.min
            elif self.max < number:
                self.__value = self.max
            else:
                self.__value = number
        else:
            raise TypeError

    @abstractmethod
    def update(self):
        pass


class Health(Parameter):
    def update(self):
        hunger = self.origin.kind.value[self.origin.mature].params[Hunger]
        critical = sum(hunger.range) / 4
        if self.origin.params[Hunger].value < critical:
            self.value -= 0.5


class Hunger(Parameter):
    def update(self):
        self.value -= 1


class KindParameters:
    def __init__(self, days: int, *params: Parameter):
        self.days = days
        self.params: dict[Type, Parameter] = {
            param.__class__: param
            for param in params
        }


class Kind(Enum):
    CAT = {
        Maturity.CUB: KindParameters(
            4,
            Health(10, 0, 20),
            Hunger(5, 0, 25),
        ),
        Maturity.YOUNG: KindParameters(
            10,
            Health(0, 0, 50),
            Hunger(0, 0, 30),
        ),
        Maturity.ADULT: KindParameters(
            20,
            Health(0, 0, 45),
            Hunger(0, 0, 25),
        ),
        Maturity.OLD: KindParameters(
            12,
            Health(0, 0, 35),
            Hunger(0, 0, 20),
        ),
    }

