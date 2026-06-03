from aiogram.fsm.state import StatesGroup, State


class URL(StatesGroup):
    waiting = State()


status = False
