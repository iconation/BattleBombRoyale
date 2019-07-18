from iconservice import *
from ..player.player import *
from ..bomb.bomb import *
from ..utils.utils import *

TAG = 'BattleBombRoyale'

# ================================================
#  Exceptions
# ================================================
class GameAlreadyJoined(Exception):
    pass

class NotEnoughPlayers(Exception):
    pass

class InvalidGameHost(Exception):
    pass

class CannotDistributeBombs(Exception):
    pass

class PlayerNotFound(Exception):
    pass

class NotEnoughFundsForReward(Exception):
    pass

class GameAlreadyStarted(Exception):
    pass

class StartCountdownNotStarted(Exception):
    pass

class ReadyCountdownNotReached(Exception):
    pass

class ReadyCountdownAlreadyStarted(Exception):
    pass

class CannotChangeHost(Exception):
    pass

class GameAlreadyOver(Exception):
    pass

class GameIsntVictory(Exception):
    pass

class GameNotStarted(Exception):
    pass

class PlayerIsNotWinner(Exception):
    pass

class InvalidParticipationCost(Exception):
    pass

class DoNotSuicide(Exception):
    pass

class GameIsFull(Exception):
    pass

class GameState:

    # ================================================
    #  Constants
    # ================================================
    # At least 2 players are required to start a game
    _MINIMUM_PLAYERS_START_GAME = 2
    # Seconds required for the start countdown for each player
    _START_COUNTDOWN_DURATION_PER_PLAYER = 5 * 1000 * 1000
    # Maximum players per game
    _MAXIMUM_PLAYERS_IN_GAME = 10

    def __init__(self,
                 token: str,
                 cost: int,
                 host: str,
                 created: int,
                 started: int = 0,
                 players: dict = None,
                 events: list = None,
                 reward: int = 0,
                 ready_timestamp: int = 0):
        self._cost = cost
        self._token = token
        self._host = host
        self._created = created
        self._started = started
        # Players is a dict with player address as a key
        self._players = players if players else {}
        # Events is a list of hashes containing eventlogs
        self._events = events if events else []
        self._reward = reward
        self._ready_timestamp = ready_timestamp

    # ================================================
    #  Checks
    # ================================================
    def check_game_not_full(self) -> None:
        if self._players_count() >= self._MAXIMUM_PLAYERS_IN_GAME:
            raise GameIsFull

    def check_players_count(self) -> None:
        if self._players_count() < self._MINIMUM_PLAYERS_START_GAME:
            raise NotEnoughPlayers

    def check_player_host(self, player: Player) -> None:
        if player.address != self._host:
            raise InvalidGameHost

    def check_game_not_already_started(self) -> None:
        if self.is_started():
            raise GameAlreadyStarted

    def check_ready_countdown_started(self) -> None:
        if self._ready_timestamp == 0:
            raise StartCountdownNotStarted

    def check_ready_countdown_reached(self, now: int) -> None:
        if now < self._ready_timestamp:
            raise ReadyCountdownNotReached

    def check_ready_countdown_not_already_started(self) -> None:
        if self._ready_timestamp != 0:
            raise ReadyCountdownAlreadyStarted

    def check_is_victory(self) -> None:
        if not self.is_victory():
            raise GameIsntVictory

    def check_winner(self, player: Player) -> None:
        if self.get_winner() != player:
            raise PlayerIsNotWinner

    def check_address_is_player(self, player_address: str) -> None:
        if not player_address in self._players:
            raise PlayerNotFound

    def check_address_not_in_game(self, player_address: str) -> None:
        if player_address in self._players:
            raise GameAlreadyJoined

    def check_enough_reward(self, amount: int) -> None:
        if self._reward < amount:
            raise NotEnoughFundsForReward

    def check_game_over(self):
        if not self._token:
            raise GameAlreadyOver

    def check_is_started(self):
        if not self.is_started():
            raise GameNotStarted

    def check_enough_players_without_bomb(self, players_without_bomb: list):
        if not players_without_bomb:
            # Not enough players are hands free
            raise CannotDistributeBombs

    def check_suicide(self, looter: Player, looted: Player) -> None:
        if looter == looted:
            raise DoNotSuicide

    def check_participation_cost(self, cost: int) -> None:
        if cost != self._cost:
            raise InvalidParticipationCost

    # ================================================
    #  Helpers
    # ================================================
    def _send_bomb_failure(self, player: Player) -> None:
        # Sorry player, but you're gonna die.
        player.prepare_to_die()

    def _send_bomb_success(self, player: Player, receiver: Player, now: int) -> None:
        # Update the bomb instance
        bomb = player.remove_bomb()
        bomb.afk_reset(now)
        bomb.tick()
        # Enjoy your bomb, receiver
        receiver.give_bomb(bomb)

    def _get_all_players_without_bomb(self, immune: Player) -> list:
        # Only pick players without bombs in hand
        # Conditions list :
        # - Player be must alive
        # - Player must not already hold a bomb
        # - The player must not be immune
        return list(filter(
            lambda player:
            player.is_alive() and
            not player.has_bomb() and
            (player != immune if immune else True),
            self.get_all_players()))

    def _get_random_player_without_bomb(self, immune: Player = None) -> Player:
        players_without_bomb = self._get_all_players_without_bomb(immune)
        self.check_enough_players_without_bomb(players_without_bomb)
        # Pick one player randomly
        return Utils.rand_pick(players_without_bomb)

    def _change_host(self, leaver: Player) -> None:
        # Get all players, except the leaver
        players = list(filter(lambda player: player != leaver, self.get_all_players()))
        # Pick a new host randomly
        random_player = Utils.rand_pick(players)
        self._host = random_player.address

    def is_victory(self) -> bool:
        # 1 alive, everybody else is dead
        return (len(self.get_players_alive()) == 1
                and len(self.get_players_dead()) == (len(self.get_all_players()) - 1))

    def get_winner(self) -> Player:
        return self.get_players_alive()[0]

    def _players_count(self) -> int:
        return len(self._players)

    def get_participation_cost(self) -> int:
        return self._cost

    def get_loot_reward(self) -> int:
        # Looting reward = 10% of Participation cost
        return int(self.get_participation_cost() * (10 / 100.0))

    def _is_host(self, player: Player) -> bool:
        return player.address == self._host

    def _spawn_new_bomb(self, started: int) -> None:
        # Pick a random player without a bomb, create one and give it to him
        random_player_without_bomb = self._get_random_player_without_bomb()
        bomb = Bomb(started)
        random_player_without_bomb.give_bomb(bomb)

    # ================================================
    #  Extern methods
    # ================================================
    # States ==================
    def join(self, player: Player) -> None:
        # ==========================
        # Check
        self.check_address_not_in_game(player.address)
        self.check_game_not_full()

        # ==========================
        # Process
        self._players[player.address] = player

    def quit(self, leaver: Player) -> None:
        # ==========================
        # Check
        self.check_address_is_player(leaver.address)

        # ==========================
        # Process
        del self._players[leaver.address]

        # If none is left, game over
        if self._players_count() == 0:
            self.over()
            return

        # Rotate host if leaver is host
        if self._is_host(leaver):
            self._change_host(leaver)

    def ready_ask(self, host: Player, now: int) -> None:
        # ==========================
        # Check
        self.check_players_count()
        self.check_game_not_already_started()
        self.check_ready_countdown_not_already_started()
        # Only the host can ask ready
        self.check_player_host(host)

        # ==========================
        # Process
        # Register now the ready timestamp
        self._ready_timestamp = now + (self._players_count() * self._START_COUNTDOWN_DURATION_PER_PLAYER)
        # Check host as ready
        host.set_ready()

    def ready_ok(self, player: Player) -> None:
        # ==========================
        # Check
        self.check_game_not_already_started()
        self.check_ready_countdown_started()

        # ==========================
        # Process
        player.set_ready()

    def start(self, started: int) -> list:
        # ==========================
        # Remove afkers
        afkers = self.get_not_ready_players()
        for afker in afkers:
            self.quit(afker)

        # ==========================
        # Check
        self.check_game_not_already_started()
        # Only check for countdown if everybody wasn't ready
        if afkers:
            self.check_ready_countdown_reached(started)
        self.check_players_count()

        # ==========================
        # Process
        self._spawn_new_bomb(started)
        self._started = started

        return afkers

    def over(self) -> None:
        # ==========================
        # Check
        self.check_game_over()
        self._token = None

    def send_bomb(self, player: Player, now: int, use_shield: bool) -> Player:
        # ==========================
        # Player Check
        player.check_alive()

        # ==========================
        # Bomb Check
        bomb = player.get_bomb()
        bomb.check_not_afk_timeout(now)

        if use_shield:
            # No matter if it exploded or not, use the shield
            player.use_shield()

        if bomb.exploded() and not use_shield:
            # Boom!
            self._send_bomb_failure(player)
            return None

        # Find some receiver randomly
        receiver = self._get_random_player_without_bomb(player)
        self._send_bomb_success(player, receiver, now)
        return receiver

    def get_player(self, address: str) -> Player:
        self.check_address_is_player(address)
        return self._players[address]

    def loot_player(self, looter: Player, looted: Player, now: int) -> None:
        # ==========================
        self.check_suicide(looter, looted)

        # ==========================
        # Finish him!
        looted.die(now)
        looted.remove_bomb()

        # Transfer a new bomb to someone else if the game is not over
        if not self.is_victory():
            self._spawn_new_bomb(now)

    def get_not_ready_players(self) -> list:
        return list(filter(lambda player: not player.is_ready(), self.get_all_players()))

    def get_players_alive(self) -> list:
        return list(filter(lambda player: player.is_alive(), self.get_all_players()))

    def get_players_lootable(self) -> list:
        return list(filter(lambda player: player.is_lootable(), self.get_all_players()))

    def get_players_dead(self) -> list:
        return list(filter(lambda player: player.is_dead(), self.get_all_players()))

    def get_player_with_bomb(self) -> Player:
        for player in self.get_all_players():
            if player.has_bomb():
                return player

    def get_all_players(self) -> list:
        return self._players.values()

    def deposit_reward(self, amount) -> None:
        self.check_participation_cost(amount)
        self._reward += amount

    def withdraw_reward(self, amount) -> None:
        # ==========================
        # Reward Checks
        self.check_enough_reward(amount)
        self._reward -= amount

    def remaining_reward(self) -> int:
        return self._reward

    def operator_fees(self) -> int:
        # Operator fees = 2% of winner reward
        return int(self._reward * 0.02)

    def winner_reward(self) -> int:
        # Winner reward = (all remaining ICX in the lottery - operator fees)
        return self._reward - self.operator_fees()

    def is_started(self) -> bool:
        return self._started != 0

    def is_over(self) -> bool:
        return self._token is None

    def add_event(self, transaction: str) -> None:
        # Multiple events can be triggered in the same transaction
        # We don't need to add the transaction hash multiple times in the game event list.
        if not transaction in self._events:
            self._events.append(transaction)

    # Serialization ==================
    def serialize(self) -> dict:
        return {
            'token' : self._token,
            'cost' : self._cost,
            'host' : self._host,
            'created' : self._created,
            'started' : self._started,
            'players' : {k: v.serialize() for k, v in self._players.items()},
            'reward' : self._reward,
            'events' : self._events,
            'ready_timestamp' : self._ready_timestamp
        }

    @staticmethod
    def deserialize(obj: dict) -> 'GameState':
        return GameState(
            token=obj['token'],
            cost=obj['cost'],
            host=obj['host'],
            created=obj['created'],
            started=obj['started'],
            players={k: Player.deserialize(v) for k, v in obj['players'].items()},
            reward=obj['reward'],
            events=obj['events'],
            ready_timestamp=obj['ready_timestamp']
        )

    def to_json(self) -> str:
        return json_dumps(self.serialize())

    @staticmethod
    def from_json(json: str) -> 'GameState':
        return GameState.deserialize(json_loads(json))

    # Getters ==================
    @property
    def token(self) -> str:
        return self._token
