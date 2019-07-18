from iconservice import *
from ..utils.utils import *

TAG = 'BattleBombRoyale'

class BombAFKExploded(Exception):
    pass

class Bomb:
    # ================================================
    #  Constants
    # ================================================
    # Bomb time for exploding (in milliseconds)
    _BOMB_TIME_FOR_AFK_EXPLODING = 20 * 1000
    # Initial risk of explosion : 10%
    _BOMB_RISK_INITIAL_CAP = 5
    # Maximum risk of explosion : 50%
    _BOMB_RISK_MAXIMUM_CAP = 50
    # For each pass to another player, the bomb chance of explosion increase
    _BOMB_EXPLOSION_TICK = 5

    def __init__(self, started: int, risk: int = None):
        self._started = started
        self._risk = risk if risk else self._BOMB_RISK_INITIAL_CAP

    # States ==================
    def afk_timeout(self, now: int) -> bool:
        return (self._started + self._BOMB_TIME_FOR_AFK_EXPLODING * 1000) <= now

    def exploded(self) -> bool:
        rand = Utils.rand(0, 100)
        return self._risk > rand

    def tick(self) -> None:
        self._risk += self._BOMB_EXPLOSION_TICK
        if self._risk > self._BOMB_RISK_MAXIMUM_CAP:
            self._risk = self._BOMB_RISK_MAXIMUM_CAP

    def afk_reset(self, started: int) -> None:
        self._started = started

    # Serialization ==================
    def serialize(self) -> dict:
        return {
            'started' : self._started,
            'risk' : self._risk,
        }

    @staticmethod
    def deserialize(obj: dict) -> 'Bomb':
        return Bomb(
            started=obj['started'],
            risk=obj['risk']
        )

    # Checks ===========================
    def check_not_afk_timeout(self, now: int) -> None:
        if self.afk_timeout(now):
            raise BombAFKExploded

    # Getters ==================
    @property
    def risk(self) -> int:
        return self._risk
