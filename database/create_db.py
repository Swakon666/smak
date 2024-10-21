# smak_bot/Smak/smak_bot/database/create_db.py
import sys
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
from database.models import Base, Event
from utils.db_api import async_session
from datetime import datetime, timedelta
import asyncio

# Добавляем корневую директорию проекта в sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

async def create_tables():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Таблицы успешно созданы.")
    
    # Закрываем движок после завершения работы
    await engine.dispose()

async def add_sample_events():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session_maker = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session_maker() as session:
        event1 = Event(
            title="Музыкальный фестиваль",
            description="Фестиваль современной музыки.",
            date=datetime.utcnow() + timedelta(days=10),
            location="Москва, Красная площадь",
            seats_standard=100,
            seats_premium=50,
            seats_vip=20
        )
        
        event2 = Event(
            title="Конференция по IT",
            description="Конференция для IT-специалистов.",
            date=datetime.utcnow() + timedelta(days=20),
            location="Санкт-Петербург, Концертный зал",
            seats_standard=150,
            seats_premium=75,
            seats_vip=30
        )
        
        session.add_all([event1, event2])
        await session.commit()
        print("Примерные мероприятия добавлены.")
    
    await engine.dispose()

async def main():
    await create_tables()
    await add_sample_events()

if __name__ == '__main__':
    asyncio.run(main())
