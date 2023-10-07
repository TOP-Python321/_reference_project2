from abc import ABC, abstractmethod
from collections.abc import Iterable
from enum import Enum
from numbers import Real
from pathlib import Path
from sys import path
from typing import Type


ROOT_DIR = Path(path[0]).parent.parent


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
            for cls, param in kind[self.mature].params.items()
        }
        self.player_actions: list[Action] = [
            act.__class__(**(act.__dict__ | {'origin': self}))
            for act in kind[self.mature].player_actions
        ]
        self.creature_actions: set[Action] = {
            act.__class__(**(act.__dict__ | {'origin': self}))
            for act in kind[self.mature].creature_actions
        }
        self.history: History = History()

    def update(self):
        for param in self.params.values():
            param.update()

    def _grow_up(self, new_mature: Maturity):
        # Maturity(self.mature.value + 1)
        for cls, param in self.kind[new_mature].params.items():
            self.params[cls].min = param.min
            self.params[cls].max = param.max

    def autosave(self):
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
        hunger = self.origin.kind[self.origin.mature].params[Satiety]
        critical = sum(hunger.range) / 4
        if self.origin.params[Satiety].value < critical:
            self.value -= 0.5


class Satiety(Parameter):
    def update(self):
        self.value -= 1


class Action(ABC):
    name: str
    
    def __init__(
            self,
            timer: int = None,
            origin: Creature = None,
    ):
        self.timer = timer
        self.origin = origin
    
    @abstractmethod
    def action(self):
        pass


class Feed(Action):
    def __init__(
            self,
            amount: int,
            timer: int = None,
            origin: Creature = None,
    ):
        super().__init__(timer, origin)
        self.amount = amount
    
    def action(self):
        self.origin.params[Satiety].value += self.amount


class PlayRope(Action):
    def action(self):
        print('верёвочка!')


class PlayTail(Action):
    def action(self):
        print('бегает за хвостом')


class Sleep(Action):
    def action(self):
        print('сон')


class MatureOptions:
    def __init__(
            self, 
            days: int, 
            *params: Parameter, 
            player_actions: list[Action], 
            creature_actions: set[Action]
    ):
        self.days = days
        self.params: dict[Type, Parameter] = {
            param.__class__: param
            for param in params
        }
        self.player_actions = player_actions
        self.creature_actions = creature_actions


AgesParameters = dict[Maturity, MatureOptions] | Iterable[tuple[Maturity, MatureOptions]]

class Kind(dict):
    def __init__(
            self,
            name: str,
            image_path: str | Path,
            ages_parameters: AgesParameters,
    ):
        super().__init__(ages_parameters)
        self.name = name
        self.image = Path(image_path)



cat_kind = Kind(
    'Кот',
    ROOT_DIR / 'data/images/cat.png',
    {
        Maturity.CUB: MatureOptions(
            4,
            Health(10, 0, 20),
            Satiety(5, 0, 25),
            player_actions=[
                Feed(20),
            ],
            creature_actions={
                PlayRope(100),
            }
        ),
        Maturity.YOUNG: MatureOptions(
            10,
            Health(0, 0, 50),
            Satiety(0, 0, 30),
            player_actions=[
                Feed(25),
            ],
            creature_actions={
                PlayRope(100),
                Sleep(120),
            }
        ),
        Maturity.ADULT: MatureOptions(
            20,
            Health(0, 0, 45),
            Satiety(0, 0, 25),
            player_actions=[
                Feed(20),
            ],
            creature_actions={
                Sleep(60),
                PlayRope(180),
            }
        ),
        Maturity.OLD: MatureOptions(
            12,
            Health(0, 0, 35),
            Satiety(0, 0, 20),
            player_actions=[
                Feed(10),
            ],
            creature_actions={
                Sleep(30)
            }
        ),
    }
)
dog_kind = Kind(
    'Пёс',
    ROOT_DIR / 'data/images/dog.png',
    {
        Maturity.CUB: MatureOptions(
            4,
            Health(12, 0, 25),
            Satiety(7, 0, 25),
            player_actions=[
                Feed(20),
            ],
            creature_actions={
                PlayTail(100),
            }
        ),
        Maturity.YOUNG: MatureOptions(
            11,
            Health(0, 0, 50),
            Satiety(0, 0, 30),
            player_actions=[
                Feed(25),
            ],
            creature_actions={
                PlayTail(100),
                Sleep(120),
            }
        ),
        Maturity.ADULT: MatureOptions(
            20,
            Health(0, 0, 45),
            Satiety(0, 0, 25),
            player_actions=[
                Feed(20),
            ],
            creature_actions={
                Sleep(60),
                PlayTail(180),
            }
        ),
        Maturity.OLD: MatureOptions(
            12,
            Health(0, 0, 35),
            Satiety(0, 0, 20),
            player_actions=[
                Feed(10),
            ],
            creature_actions={
                Sleep(30)
            }
        ),
    }
)
mouse_kind = Kind(
    'Мыш',
    ROOT_DIR / 'data/images/mouse.png',
    {
        Maturity.CUB: MatureOptions(
            4,
            Health(5, 0, 15),
            Satiety(5, 0, 15),
            player_actions=[
                Feed(20),
            ],
            creature_actions=set()
        ),
        Maturity.YOUNG: MatureOptions(
            11,
            Health(0, 0, 50),
            Satiety(0, 0, 30),
            player_actions=[
                Feed(25),
            ],
            creature_actions=set()
        ),
        Maturity.ADULT: MatureOptions(
            20,
            Health(0, 0, 45),
            Satiety(0, 0, 25),
            player_actions=[
                Feed(20),
            ],
            creature_actions=set()
        ),
        Maturity.OLD: MatureOptions(
            12,
            Health(0, 0, 35),
            Satiety(0, 0, 20),
            player_actions=[
                Feed(10),
            ],
            creature_actions=set()
        ),
    }
)

