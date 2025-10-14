import logging

logging.basicConfig(level=logging.DEBUG)

from sqlalchemy import select
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from constants import (
    ACTION_CAT_MELEE,
    ACTION_CAT_PROJECTILE,
    ACTION_CAT_BEAM,
    ACTION_CAT_RADIATE,
)

from app import app, db

# the following model classes will all be used to create tables in the db when
# db.create_all() is called
from classes.player import Player
from classes.species import Species
from classes.action import Action
from classes.creature import Creature, CreatureState
from classes.match import Match
from classes.board import Board
from classes.position import Position


def create_and_seed_postgres(app, db):
    with app.app_context():
        db.create_all()
        seed_postgres(db)


def seed_postgres(db):
    """Adds postgres records for testing the game. Will become defunct once
    the early stages of game design and testing have concluded."""

    # add test players

    test_player_1 = duplicate_safe_add_flush(db, Player(name="Safari"))
    test_player_2 = duplicate_safe_add_flush(db, Player(name="Firehawk"))
    test_player_3 = duplicate_safe_add_flush(db, Player(name="Guest"))

    # add test actions

    test_action_melee = duplicate_safe_add_flush(
        db, Action("test melee", 1, 7, ACTION_CAT_MELEE)
    )
    test_action_projectile = duplicate_safe_add_flush(
        db, Action("test projectile", 6, 6, ACTION_CAT_PROJECTILE)
    )
    test_action_beam = duplicate_safe_add_flush(
        db, Action("test beam", 5, 2, ACTION_CAT_BEAM)
    )
    test_action_radiate = duplicate_safe_add_flush(
        db, Action("test radiate", 3, 1, ACTION_CAT_RADIATE)
    )

    # add test species

    test_species = Species("Test Species", 1, 10, 4)
    test_species.actions.extend(
        [
            test_action_melee,
            test_action_projectile,
            test_action_beam,
            test_action_radiate,
        ]
    )
    test_species = duplicate_safe_add_flush(db, test_species)

    # add test creatures to players

    if db.session.query(Creature.id).count() == 0:
        duplicate_safe_add_flush(
            db, Creature(test_species.id, test_player_1.id, 1, "Aardvark")
        )
        duplicate_safe_add_flush(
            db, Creature(test_species.id, test_player_1.id, 1, "Anaconda")
        )
        duplicate_safe_add_flush(
            db, Creature(test_species.id, test_player_1.id, 1, "Armadillo")
        )
        duplicate_safe_add_flush(
            db, Creature(test_species.id, test_player_2.id, 1, "Buffalo")
        )
        duplicate_safe_add_flush(
            db, Creature(test_species.id, test_player_2.id, 1, "Beaver")
        )
        duplicate_safe_add_flush(
            db, Creature(test_species.id, test_player_2.id, 1, "Bear")
        )
        duplicate_safe_add_flush(
            db, Creature(test_species.id, test_player_3.id, 1, "Capybara")
        )
        duplicate_safe_add_flush(
            db, Creature(test_species.id, test_player_3.id, 1, "Camel")
        )
        duplicate_safe_add_flush(
            db, Creature(test_species.id, test_player_3.id, 1, "Cat")
        )

    db.session.commit()


def duplicate_safe_add_flush(db, record_to_add):
    """Safely handles the case when the script tries to add duplicate seeding records"""
    db.session.add(record_to_add)
    try:
        db.session.flush()
        logging.debug(f"Seeded new {type(record_to_add).__name__} in DB")
        return record_to_add
    except (UniqueViolation, IntegrityError):
        db.session.rollback()
        record_class = type(record_to_add)
        return db.session.scalars(
            select(record_class).where(record_class.name == record_to_add.name)
        ).one()


if __name__ == "__main__":
    logging.debug("Creating DB if it does not exist")
    create_and_seed_postgres(app, db)
