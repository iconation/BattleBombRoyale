from iconservice import *
from ..utils.utils import *

TAG = 'BattleBombRoyale'

class InvalidAccountName(Exception):
    pass

class Account:
    # ================================================
    #  Constants
    # ================================================
    _NAME_MIN_CHARACTERS = 3
    _NAME_MAX_CHARACTERS = 12

    # ================================================
    def __init__(self, address: str, name: str):
        self._address = address
        self._name = name

    # States ==================
    def set_name(self, name: str):
        self._check_valid_name(name)
        self._name = name

    # Serialization ==================
    def serialize(self) -> dict:
        return {
            'address' : self._address,
            'name' : self._name
        }

    @staticmethod
    def deserialize(obj: dict) -> 'Account':
        return Account(
            address=obj['address'],
            name=obj['name']
        )

    def to_json(self) -> str:
        return json_dumps(self.serialize())

    @staticmethod
    def from_json(json: str) -> 'Account':
        return Account.deserialize(json_loads(json))

    # Checks ===========================
    def _check_valid_name(self, name: str) -> None:
        if (len(name) < self._NAME_MIN_CHARACTERS
                or len(name) > self._NAME_MAX_CHARACTERS
                or not Utils.is_ascii(name)):
            raise InvalidAccountName

    # Getters ==================
