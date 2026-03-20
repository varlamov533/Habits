from sqlalchemy import MetaData, Table, String, Integer, Column, DateTime, Boolean, ForeignKey, UniqueConstraint
from datetime import datetime

metadata = MetaData()


users = Table('users', metadata,
    Column('id', Integer(), primary_key=True),
    Column('username', String(32), nullable=False, unique=True),
)


habit = Table('habit', metadata,
    Column('id', Integer(), primary_key=True),
    Column('title', String(64), nullable=False),
    Column('interval', Integer(), default=1),
    Column('user_id', ForeignKey(users.c.id, ondelete='CASCADE'), nullable=False),
    Column('created_on', DateTime(), default=datetime.now),
    Column('updated_on', DateTime(), default=datetime.now, onupdate=datetime.now),
    Column('is_active', Boolean(), default=True),
    UniqueConstraint('title', 'user_id', name='unique_user_and_title'),
)


perform_habit = Table('perform_habit', metadata,
    Column('habit_id', ForeignKey(habit.c.id, ondelete='CASCADE')),
    Column('user_id', ForeignKey(users.c.id, ondelete='CASCADE')),
    Column('performed', DateTime(), default=datetime.now)
)
