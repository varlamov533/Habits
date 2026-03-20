from datetime import date, datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
from sqlalchemy import select, insert, delete, update, exists
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
from fastapi import FastAPI, Depends
from models import HabitModel

import tables

load_dotenv()

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 5433))


if not DB_NAME:
    raise ValueError('DB_NAME can`t be null')
elif not DB_USER:
    raise ValueError('DB_USER cant`t be null')
elif not DB_PASSWORD:
    raise ValueError('DB_PASSWORD can`t be null')

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(
    DATABASE_URL,
    pool_size=15,
    max_overflow=25,
)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with async_session() as session:
        yield session


app = FastAPI()

@app.get('/habits/')
async def get_habits(user_id: int=None, is_active: bool=None, conn: AsyncSession = Depends(get_db)):
    query = select(tables.habit)
    if user_id:
        query = query.where(tables.habit.c.user_id == user_id)
    if is_active is not None:
        query = query.where(tables.habit.c.is_active == is_active)

    result = await conn.execute(query)
    rows = result.mappings().all()
    return rows


@app.post('/habits/')
async def create_habit(habit: HabitModel, conn: AsyncSession = Depends(get_db)):
    insert_data = habit.model_dump()
    user_exists = await conn.execute(select(exists().where(tables.users.c.id == insert_data['user_id'])))
    user_exists = user_exists.scalar()
    if not user_exists:
        return {'status': 'error', 'message': f'User {insert_data["user_id"]} not found.'}
    query = insert(tables.habit).values(**insert_data)
    await conn.execute(query)
    await conn.commit()
    return {'status': 'success', 'message': insert_data}


@app.post('/users/create/{username}')
async def create_user(username: str, conn: AsyncSession = Depends(get_db)):
    user_exists = await conn.execute(select(exists().where(tables.users.c.username == username)))
    user_exists = user_exists.scalar()
    if user_exists:
        return {'status': 'error', 'message': f'User {username} is already exists.'}
    await conn.execute(insert(tables.users).values({'username':username}))
    await conn.commit()
    return {'status': 'success', 'username': username}


@app.delete('/users/delete/{username}')
async def delete_user(username: str, conn: AsyncSession = Depends(get_db)):
    user = await conn.execute(select(tables.users).where(tables.users.c.username==username))
    user = user.scalars().all()
    if not user:
        return {'status': 'error', 'message': f'User {username} does not exist.'}
    query = delete(tables.users).where(tables.users.c.username==username)
    await conn.execute(query)
    await conn.commit()
    return {'status': 'success', 'message': username}


@app.put('/habits/update/{habit_id}')
async def update_habit(habit_id: int, habit: HabitModel, conn: AsyncSession = Depends(get_db)):
    new_data = habit.model_dump()

    habit_exists = await conn.execute(select(exists().where(tables.habit.c.id==habit_id)))
    habit_exists = habit_exists.scalar()
    if not habit_exists:
        return {'status': 'error', 'message': f'Habit with {habit_id} does not exists.'}
    query = update(tables.habit).where(tables.habit.c.id==habit_id).values(**new_data)
    await conn.execute(query)
    await conn.commit()
    return {'status': 'success', 'message': new_data}


@app.post('/habits/{habit_id}/checkins/{user_id}')
async def perform_habit(habit_id: int, user_id: int, conn: AsyncSession = Depends(get_db)):
    data = {
        'habit_id': habit_id,
        'user_id': user_id,
        'performed': datetime.now(),
    }
    query = insert(tables.perform_habit).values(**data)
    await conn.execute(query)
    await conn.commit()
    return {'status': 'success', 'message': data}


@app.delete('/habits/{habit_id}/checkins/')
async def delete_performs(habit_id: int, date: date, conn: AsyncSession = Depends(get_db)):
    fin_dt = date + timedelta(days=1)
    query = (
        delete(tables.perform_habit)
        .where(tables.perform_habit.c.habit_id == habit_id)
        .where(tables.perform_habit.c.performed >= date)
        .where(tables.perform_habit.c.performed <= fin_dt)
    )
    result = await conn.execute(query)
    await conn.commit()
    if result.rowcount == 0:
        return {'status': 'success', 'message': 'No records found for this date'}
    return {'status': 'success', 'message': f'{result.rowcount} has been deleted'}


@app.get('/habits/{habit_id}/stats')
async def get_habit_statistic(habit_id: int, start: Optional[date]=None, fin: Optional[date]=None, conn: AsyncSession = Depends(get_db)):
    query = select(tables.perform_habit).where(tables.perform_habit.c.habit_id==habit_id)
    if start:
        query = query.where(tables.perform_habit.c.performed >= start)
    if fin:
        query = query.where(tables.perform_habit.c.performed <= fin)
    result = await conn.execute(query)
    result = result.mappings().all()
    if not result:
        return {'status': 'success', 'message': 'No records found'}
    return {'status': 'success', 'message': result}