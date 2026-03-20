from pydantic import BaseModel

class HabitModel(BaseModel):
    title: str
    interval: int
    user_id: int
    is_active: bool