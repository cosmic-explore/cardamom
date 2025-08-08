from  psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError

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

    test_player_1 = Player(name="Safari")
    test_player_2 = Player(name="Firehawk")
    duplicate_safe_add_flush(db, test_player_1)
    duplicate_safe_add_flush(db, test_player_2)

    # add test actions

    test_action = Action("test attack", 5, 1)
    duplicate_safe_add_flush(db, test_action)

    # add test species

    test_species = (Species("Test Species", 1, 1, 4))
    test_species.actions.append(test_action)
    duplicate_safe_add_flush(db, test_species)

    # add test creatures to players

    duplicate_safe_add_flush(db, Creature(test_species.id, test_player_1.id, 1, "A"))
    duplicate_safe_add_flush(db, Creature(test_species.id, test_player_2.id, 1, "B"))

    db.session.commit()

def duplicate_safe_add_flush(db, record_to_add):
    """Safely handles the case when the script tries to add duplicate seeding records"""
    db.session.add(record_to_add)
    try:
        db.session.flush()
        return record_to_add
    except (UniqueViolation, IntegrityError):
        db.session.rollback()
        return None
