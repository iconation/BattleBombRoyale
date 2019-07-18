from iconservice import *
from ..bomb.bomb import *

class PlayerHasNoBomb(Exception):
    pass

class PlayerHasNoShield(Exception):
    pass

class PlayerAlreadyDead(Exception):
    pass

class PlayerIsNotLootable(Exception):
    pass


# ================================================
#  Constants
# ================================================
class PlayerState:
    ALIVE = 1
    LOOTABLE = 2
    DEAD = 3

class Player:

    def __init__(self,
                 address: str,
                 state: int = PlayerState.ALIVE,
                 bomb: Bomb = None,
                 shield: bool = True,
                 ready: bool = False):
        self._address = address
        self._state = state
        self._bomb = bomb
        self._shield = shield
        self._ready = ready

    # ================================================
    #  Helpers
    # ================================================
    def _is_afk(self, now: int) -> bool:
        if not self.is_alive():
            return False
        if not self.has_bomb():
            return False
        bomb = self.get_bomb()
        return bomb.afk_timeout(now)

    # ================================================
    #  Extern methods
    # ================================================
    # States ==================
    def die(self, now: int) -> None:
        # ==========================
        # Player Checks
        self.check_lootable(now)
        # ==========================
        self._state = PlayerState.DEAD

    def prepare_to_die(self) -> None:
        # ==========================
        # Player Checks
        self.check_alive()
        # ==========================
        self._state = PlayerState.LOOTABLE

    def use_shield(self) -> None:
        # ==========================
        # Player Checks
        self.check_has_shield()
        # ==========================
        self._shield = False

    def remove_bomb(self) -> Bomb:
        bomb = self.get_bomb()
        self._bomb = None
        return bomb

    def get_bomb(self) -> Bomb:
        self.check_has_bomb()
        return self._bomb

    def give_bomb(self, bomb: Bomb) -> None:
        self._bomb = bomb

    def is_alive(self) -> bool:
        return self._state == PlayerState.ALIVE

    def is_dead(self) -> bool:
        return self._state == PlayerState.DEAD

    def is_lootable(self, now: int) -> bool:
        return self._state == PlayerState.LOOTABLE or self._is_afk(now)

    # def is_dead(self) -> bool:
    #     return self._state == PlayerState.DEAD

    def is_ready(self) -> bool:
        return self._ready

    def set_ready(self) -> None:
        self._ready = True

    def has_bomb(self) -> bool:
        return self._bomb is not None

    def has_shield(self) -> bool:
        return self._shield

    # Serialization ==================
    def serialize(self) -> dict:
        obj = {
            'address' : self._address,
            'state' : self._state,
            'shield' : self._shield,
            'ready' : self._ready
        }

        if self.has_bomb():
            obj['bomb'] = self._bomb.serialize()

        return obj

    @staticmethod
    def deserialize(obj) -> 'Player':
        return Player(
            address=obj['address'],
            state=obj['state'],
            shield=obj['shield'],
            ready=obj['ready'],
            bomb=Bomb.deserialize(obj['bomb']) if 'bomb' in obj else None
        )

    # Checks ===========================
    def check_has_bomb(self) -> None:
        if not self.has_bomb():
            raise PlayerHasNoBomb

    def check_has_shield(self) -> None:
        if not self.has_shield():
            raise PlayerHasNoShield

    def check_lootable(self, now: int) -> None:
        if not self.is_lootable(now):
            raise PlayerIsNotLootable

    def check_alive(self) -> None:
        if not self.is_alive():
            raise PlayerAlreadyDead

    # Getters ==================
    @property
    def address(self) -> str:
        return self._address

    # Operators ==================
    def __hash__(self):
        return hash(self._address)

    def __eq__(self, other) -> bool:
        return self._address == other.address
