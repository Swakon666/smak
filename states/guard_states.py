 # states/guard_states.py
from aiogram.dispatcher.filters.state import State, StatesGroup

class GuardStates(StatesGroup):
    # Состояние ожидания сканирования QR-кода билета
    waiting_for_qr_scan = State()
    
    # Состояние проверки статуса билета
    waiting_for_ticket_status_check = State()
    
    # Состояние подтверждения входа на мероприятие
    waiting_for_entry_confirmation = State()

