# states/top_up_states.py
from aiogram.dispatcher.filters.state import State, StatesGroup

class TopUpStates(StatesGroup):
    waiting_for_bank = State()
    waiting_for_confirmation = State()
    waiting_for_payment = State()
