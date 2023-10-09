from abc import ABC, abstractmethod
from collections.abc import Iterable
from enum import Enum
from numbers import Real
from pathlib import Path
from sys import path
from typing import Type, Self

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

    def __repr__(self):
        return '\n'.join(
            f'{cls.__name__.lower()}: {param.value:.1f}'
            for cls, param in self.params.items()
        )

    def __str__(self):
        return f"{self.name}: {'/'.join(f'{p.value:.1f}' for p in self.params.values())}"

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
            image: str | Path = None,
            origin: Creature = None,
            **kwargs
    ):
        self.timer = timer
        self.image = image
        self.origin = origin
        self.state = 'normal'

    @abstractmethod
    def action(self) -> str:
        pass


class NoAction:
    __instance: Self = None

    def __new__(cls):
        if cls.__instance is None:
            self = super().__new__(cls)
            self.image = ROOT_DIR / 'data/images/no_action.png'
            self.state = 'disabled'
            self.action = lambda: None
            cls.__instance = self
        return cls.__instance


class Feed(Action):
    def __init__(
            self,
            amount: int,
            timer: int = None,
            image: str | Path = None,
            origin: Creature = None,
            **kwargs
    ):
        super().__init__(timer, image, origin)
        self.amount = amount

    def action(self) -> str:
        self.origin.params[Satiety].value += self.amount
        return f'вы покормили {self.origin.name}'


class Play(Action):
    def action(self) -> str:
        return f'вы играете с {self.origin.name}'


class PlayRope(Action):
    def action(self) -> str:
        return 'верёвочка!'


class PlayTail(Action):
    def action(self) -> str:
        return 'бегает за хвостом'


class Sleep(Action):
    def action(self) -> str:
        return 'сон'


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
                Feed(amount=20, image=ROOT_DIR / 'data/images/btn1.png'),
                Play(image=ROOT_DIR / 'data/images/btn2.png')
            ],
            creature_actions={
                PlayRope(timer=100),
            }
        ),
        Maturity.YOUNG: MatureOptions(
            10,
            Health(0, 0, 50),
            Satiety(0, 0, 30),
            player_actions=[
                Feed(amount=25, image=ROOT_DIR / 'data/images/btn1.png'),
            ],
            creature_actions={
                PlayRope(timer=100),
                Sleep(timer=120),
            }
        ),
        Maturity.ADULT: MatureOptions(
            20,
            Health(0, 0, 45),
            Satiety(0, 0, 25),
            player_actions=[
                Feed(amount=20, image=ROOT_DIR / 'data/images/btn1.png'),
            ],
            creature_actions={
                Sleep(timer=60),
                PlayRope(timer=180),
            }
        ),
        Maturity.OLD: MatureOptions(
            12,
            Health(0, 0, 35),
            Satiety(0, 0, 20),
            player_actions=[
                Feed(amount=10, image=ROOT_DIR / 'data/images/btn1.png'),
            ],
            creature_actions={
                Sleep(timer=30)
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
                Feed(amount=20, image=ROOT_DIR / 'data/images/btn1.png'),
            ],
            creature_actions={
                PlayTail(timer=100),
            }
        ),
        Maturity.YOUNG: MatureOptions(
            11,
            Health(0, 0, 50),
            Satiety(0, 0, 30),
            player_actions=[
                Feed(amount=25, image=ROOT_DIR / 'data/images/btn1.png'),
            ],
            creature_actions={
                PlayTail(timer=100),
                Sleep(timer=120),
            }
        ),
        Maturity.ADULT: MatureOptions(
            20,
            Health(0, 0, 45),
            Satiety(0, 0, 25),
            player_actions=[
                Feed(amount=20, image=ROOT_DIR / 'data/images/btn1.png'),
            ],
            creature_actions={
                Sleep(timer=60),
                PlayTail(timer=180),
            }
        ),
        Maturity.OLD: MatureOptions(
            12,
            Health(0, 0, 35),
            Satiety(0, 0, 20),
            player_actions=[
                Feed(amount=10, image=ROOT_DIR / 'data/images/btn1.png'),
            ],
            creature_actions={
                Sleep(timer=30)
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
                Feed(amount=20, image=ROOT_DIR / 'data/images/btn1.png'),
            ],
            creature_actions=set()
        ),
        Maturity.YOUNG: MatureOptions(
            11,
            Health(0, 0, 50),
            Satiety(0, 0, 30),
            player_actions=[
                Feed(amount=25, image=ROOT_DIR / 'data/images/btn1.png'),
            ],
            creature_actions=set()
        ),
        Maturity.ADULT: MatureOptions(
            20,
            Health(0, 0, 45),
            Satiety(0, 0, 25),
            player_actions=[
                Feed(amount=20, image=ROOT_DIR / 'data/images/btn1.png'),
            ],
            creature_actions=set()
        ),
        Maturity.OLD: MatureOptions(
            12,
            Health(0, 0, 35),
            Satiety(0, 0, 20),
            player_actions=[
                Feed(amount=10, image=ROOT_DIR / 'data/images/btn1.png'),
            ],
            creature_actions=set()
        ),
    }
)

