# handlers/__init__.py
from .main_menu import register_handlers
from .admin import register_admin_handlers
from .guard import register_guard_handlers
from .top_up import register_top_up_handlers
from .tickets import register_ticket_handlers  # Добавлено
# Импортируйте другие обработчики при необходимости

def setup_handlers(dp):
    register_handlers(dp)
    register_admin_handlers(dp)
    register_guard_handlers(dp)
    register_top_up_handlers(dp)
    register_ticket_handlers(dp)  # Добавлено
    # Зарегистрируйте другие обработчики здесь

