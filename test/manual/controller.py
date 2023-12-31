from datetime import datetime as dt
from fractions import Fraction as frac
from json import dumps as jdumps, loads as jloads
from pathlib import Path
from sys import path

import model


ROOT_DIR = Path(path[0]).parent.parent


class App:
    def __init__(self):
        self.creature: model.Creature = LoadCreature.load() if self._is_live() else MainMenu.start()

    @staticmethod
    def _is_live() -> bool:
        return LoadCreature.default_path.is_file()


class LoadCreature:
    default_path: str | Path = ROOT_DIR / 'data/creature.save'
    game_days_to_real_hours: frac = frac(1, 2)

    @classmethod
    def save(cls, creature: model.Creature):
        data = {
            'timestamp': dt.now().timestamp(),
            'kind': creature.kind.name,
            'name': creature.name,
            'age': creature.age,
            'maturity': creature.mature.value,
            'params': creature.history[-1].__dict__
        }
        data = jdumps(data, ensure_ascii=False)
        cls.default_path.write_text(data, encoding='utf-8')

    @classmethod
    def load(cls) -> model.Creature:
        pass

    @classmethod
    def __params_evolution(cls, saved_state: model.State, hours: float) -> model.State:
        """Пересчитывает параметры существа в соответствии с мат.моделью имитации жизни при закрытом приложении (ТЗ п.3в)."""
        hours*cls.game_days_to_real_hours
        ...
        return saved_state


class MainMenu:

    @staticmethod
    def start():
        """Запускает GUI с фреймом главного меню."""

    @staticmethod
    def choose_kind(chosen_kind: model.Kind) -> model.Creature:
        """Создаёт питомца на основе выбранного пользователем вида."""


class LoadKinds(list):
    def __init__(self, *kinds: model.Kind):
        super().__init__(kinds)


loaded_kinds = LoadKinds(model.cat_kind, model.dog_kind, model.mouse_kind)
