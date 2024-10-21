 # states/bar_management_states.py
from aiogram.dispatcher.filters.state import State, StatesGroup

class BarManagementStates(StatesGroup):
    # Состояние для выбора напитка
    waiting_for_drink_selection = State()
    
    # Состояние для подтверждения заказа
    waiting_for_order_confirmation = State()
    
    # Состояние для оплаты заказа
    waiting_for_payment = State()
    
    # Состояние для подтверждения получения заказа
    waiting_for_order_receipt_confirmation = State()

