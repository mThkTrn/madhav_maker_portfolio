from extensions import db

# Import models to ensure they're registered with SQLAlchemy
# These imports are used to ensure SQLAlchemy knows about all models when creating tables
from .tournament import Tournament
from .game import Game
from .player import Player
from .question import Question
from .team_alias import TeamAlias
from .room_alias import RoomAlias
from .admin import Admin
from .reader import Reader, ReaderTournament
from .alert import Alert
from .protest import Protest

# Make models available at the package level
__all__ = [
    'Tournament',
    'Game',
    'Player',
    'Question',
    'TeamAlias',
    'RoomAlias',
    'Admin',
    'Alert',
    'Reader',
    'ReaderTournament',
    'Protest'
]
