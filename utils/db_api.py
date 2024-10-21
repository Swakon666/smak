# utils/db_api.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
from database.models import Base, User, Event, Ticket
from sqlalchemy.future import select
import logging
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Event, Ticket
import logging
from sqlalchemy.future import select
import logging

# Создание асинхронного движка
engine = create_async_engine(DATABASE_URL, echo=True)

# Создание фабрики сессий
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

async def add_user(telegram_id: int, name: str, age: int, institution: str):
    async with async_session() as session:
        async with session.begin():
            new_user = User(
                telegram_id=telegram_id,
                name=name,
                age=age,
                institution=institution,
                smak_coin=0,
                is_admin=False,
                is_guard=False
            )
            session.add(new_user)
        await session.commit()

async def get_user_by_telegram_id(telegram_id: int):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == telegram_id))
        user = result.scalars().first()
        return user

async def update_balance(telegram_id: int, amount: int):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.telegram_id == telegram_id))
            user = result.scalars().first()
            if user:
                user.smak_coin += amount
                logging.info(f"Баланс пользователя {telegram_id} обновлён на {amount} Smak-коинов.")
        await session.commit()

async def get_all_events():
    async with async_session() as session:
        result = await session.execute(select(Event))
        events = result.scalars().all()
        return events

async def get_event_by_title(selected_event_title: str):
    async with async_session() as session:
        result = await session.execute(select(Event).where(Event.title == selected_event_title))
        event = result.scalars().first()
        return event

async def get_ticket_price(event_id: int, category: str) -> int:
    async with async_session() as session:
        result = await session.execute(select(Event).where(Event.id == event_id))
        event = result.scalars().first()
        if not event:
            return 0
        if category == "Standard":
            return 100  # Замените на реальные значения
        elif category == "Premium":
            return 200  # Замените на реальные значения
        elif category == "VIP":
            return 300  # Замените на реальные значения
        else:
            return 0
        


async def get_available_seats(event_id: int, category: str) -> int:
    async with async_session() as session:
        event = await session.get(Event, event_id)
        if not event:
            return 0
        if category == "Standard":
            return event.seats_standard
        elif category == "Premium":
            return event.seats_premium
        elif category == "VIP":
            return event.seats_vip
        else:
            return 0

async def reduce_available_seats(event_id: int, category: str):
    async with async_session() as session:
        async with session.begin():
            event = await session.get(Event, event_id)
            if category == "Standard" and event.seats_standard > 0:
                event.seats_standard -= 1
            elif category == "Premium" and event.seats_premium > 0:
                event.seats_premium -= 1
            elif category == "VIP" and event.seats_vip > 0:
                event.seats_vip -= 1
        await session.commit()

async def create_ticket(user_id: int, event_id: int, category: str, qr_code_path: str):
    async with async_session() as session:
        async with session.begin():
            # Проверка наличия доступных мест
            available_seats = await get_available_seats(event_id, category)
            if available_seats <= 0:
                return None  # Или выбросить исключение
            # Уменьшение доступных мест
            await reduce_available_seats(event_id, category)
            
            new_ticket = Ticket(
                user_id=user_id,
                event_id=event_id,
                category=category,
                payment_status=True,
                status='Активен',
                qr_code=qr_code_path,
                checked_in=False
            )
            session.add(new_ticket)
        await session.commit()
        return new_ticket

async def get_event_title(event_id: int) -> str:
    async with async_session() as session:
        event = await session.get(Event, event_id)
        if event:
            return event.title
        return "Неизвестное мероприятие"
    
async def check_user_balance(user_id: int, required_balance: int) -> bool:
    """
    Проверяет, достаточно ли у пользователя средств на балансе для выполнения покупки.
    
    :param user_id: ID пользователя
    :param required_balance: Сумма, необходимая для покупки
    :return: True, если средств достаточно, иначе False
    """
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if user and user.smak_coin >= required_balance:
            return True
        return False

async def deduct_balance(user_id: int, amount: int) -> bool:
    """
    Списывает указанную сумму Smak-коинов с баланса пользователя.

    :param user_id: UUID пользователя
    :param amount: Сумма для списания
    :return: True, если списание успешно, иначе False
    """
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(User).where(User.id == user_id))
            user = result.scalars().first()
            if user and user.smak_coin >= amount:
                user.smak_coin -= amount
                logging.info(f"Списание {amount} Smak-коинов с пользователя {user.id}. Новый баланс: {user.smak_coin}")
                return True
            else:
                logging.warning(f"Не удалось списать {amount} Smak-коинов с пользователя {user_id}. Недостаточно средств или пользователь не найден.")
                return False