# states/ticket_states.py
from aiogram.dispatcher.filters.state import State, StatesGroup

class TicketPurchaseStates(StatesGroup):
    waiting_for_event_selection = State()
    waiting_for_ticket_category = State()
    waiting_for_confirmation = State()
