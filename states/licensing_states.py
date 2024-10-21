 # states/licensing_states.py
from aiogram.dispatcher.filters.state import State, StatesGroup

class LicensingStates(StatesGroup):
    # Состояние ожидания согласия с лицензионным соглашением
    waiting_for_agreement = State()
    
    # Состояние ожидания подтверждения согласия
    waiting_for_confirmation = State()

