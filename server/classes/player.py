from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from uuid import uuid4
from .base import db
from .creature import Creature

class Player(db.Model):
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    creatures: Mapped[List[Creature]] = relationship(back_populates="player")
    
    def __init__(self, name, id=None):
        self.id = uuid4() if id is None else id
        self.name = name
        self.creatures = []

    def get_user_id(self):
        """Func required by oauth"""
        return self.id
    
    def get_redis_active_match_key(self):
        return f"PLAYER_f{(str(self.id))}_MATCH"

    def to_simple_dict(self):
        """For the JSON serialization of Player objects."""
        return {
            "id": str(self.id),
            "name": self.name,
            "creatures": [c.to_simple_dict() for c in self.creatures]
        }
    
    @classmethod
    def find_by_name(cls, db, name):
        return db.session.scalars(select(Player).where(Player.name == name)).one_or_none()
