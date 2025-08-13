from sqlalchemy import ForeignKey, Column, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from .base import db, Base
from.action import Action
from uuid import uuid4

species_action_table = Table(
    "species_action",
    Base.metadata,
    Column("species_id", ForeignKey("species.id")),
    Column("action_id", ForeignKey("action.id"))
)

class Species(db.Model):
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    base_attack: Mapped[int] = mapped_column(nullable=False)
    base_hp: Mapped[int] = mapped_column(nullable=False)
    base_speed: Mapped[int] = mapped_column(nullable=False)

    actions: Mapped[List[Action]] = relationship(secondary=species_action_table)
    
    def __init__(self, name, base_attack, base_hp, base_speed, id=None):
        self.id = uuid4() if id is None else id
        self.name = name
        self.base_attack = base_attack,
        self.base_hp = base_hp
        self.base_speed = base_speed
        self.actions = []

    def to_simple_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "base_attack": self.base_attack,
            "base_hp": self.base_hp,
            "base_speed": self.base_speed,
            "actions": [a.to_simple_dict() for a in self.actions]
        }
    
    @classmethod
    def from_dict(cls, simple_dict):
        species = Species(
            simple_dict["name"],
            simple_dict["base_attack"],
            simple_dict["base_hp"],
            simple_dict["base_speed"],
            id=simple_dict["id"]
        )
        species.actions = [Action.from_dict(a) for a in simple_dict["actions"]]
        return species
