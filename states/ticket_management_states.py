 # states/ticket_management_states.py
from aiogram.dispatcher.filters.state import State, StatesGroup

class TicketManagementStates(StatesGroup):
    # Состояние выбора мероприятия
    waiting_for_event_selection = State()
    
    # Состояние подтверждения покупки билета
    waiting_for_ticket_confirmation = State()
    
    # Состояние ожидания оплаты билета
    waiting_for_ticket_payment = State()
    
    # Состояние получения билета
    waiting_for_ticket_receipt = State()

