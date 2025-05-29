from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class Player(SQLModel, table=True):
    player_id: Optional[int] = Field(default=None, primary_key=True)
    player_name: str

    gameplayers: List["GamePlayer"] = Relationship(back_populates="player")
    room_players: List["RoomPlayer"] = Relationship(back_populates="player")


class Room(SQLModel, table=True):
    room_id: Optional[int] = Field(default=None, primary_key=True)
    room_code: str
    is_active: bool = True

    room_players: List["RoomPlayer"] = Relationship(back_populates="room")


class RoomPlayer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    room_id: int = Field(foreign_key="room.room_id")
    player_id: int = Field(foreign_key="player.player_id")

    room: Optional[Room] = Relationship(back_populates="room_players")
    player: Optional[Player] = Relationship(back_populates="room_players")


class Game(SQLModel, table=True):
    game_id: Optional[int] = Field(default=None, primary_key=True)
    room_id: int = Field(foreign_key="room.room_id")
    round: int = 1
    is_finished: bool = False

    game_players: List["GamePlayer"] = Relationship(back_populates="game")
    histories: List["GameHistory"] = Relationship(back_populates="game")


class GamePlayer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    game_id: int = Field(foreign_key="game.game_id")
    player_id: int = Field(foreign_key="player.player_id")
    score: int = 0
    bugs: int = 0
    oxygen: int = 0
    position: int = 0
    going_down: bool = True

    game: Optional[Game] = Relationship(back_populates="game_players")
    player: Optional[Player] = Relationship(back_populates="gameplayers")


class SourceCode(SQLModel, table=True):
    source_id: Optional[int] = Field(default=None, primary_key=True)
    map_id: int = Field(foreign_key="map.map_id")
    position: int
    value: int
    type: str  # "code" / "bug" / "debt"
    map: Optional["Map"] = Relationship(back_populates="source_codes")


class Inventory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    game_player_id: int = Field(foreign_key="gameplayer.id")
    item_type: str  # "code", "bug", ...
    value: int


class Map(SQLModel, table=True):
    map_id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    size: int

    source_codes: List["SourceCode"] = Relationship(back_populates="map")


class Action(SQLModel, table=True):
    action_id: Optional[int] = Field(default=None, primary_key=True)
    game_id: int = Field(foreign_key="game.game_id")
    player_id: int = Field(foreign_key="player.player_id")
    action_type: str  # "move", "pickup", "return", etc.
    value: Optional[int] = None


class GameHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    game_id: int = Field(foreign_key="game.game_id")
    event: str
    timestamp: str

    game: Optional[Game] = Relationship(back_populates="histories")
