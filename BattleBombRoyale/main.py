from iconservice import *
from .gamestate.gamestate import *
from .player.player import *
from .account.account import *
from .utils.utils import *

TAG = 'BattleBombRoyale'

# ================================================
#  Exceptions
# ================================================
class GameAlreadyExists(Exception):
    pass

class GameDoesntExist(Exception):
    pass

class SenderNotScoreOwner(Exception):
    pass

class PlayerAlreadyRegistered(Exception):
    pass

class MaximumGamesCountReached(Exception):
    pass

class PlayerIsNotRegistered(Exception):
    pass

class ForbiddenParticipationCost(Exception):
    pass

class AccountDoesntExist(Exception):
    pass

class NotEnoughOperatorFees(Exception):
    pass

# ================================================
#  SCORE Interface
# ================================================
class BattleBombRoyale(IconScoreBase):

    # ================================================
    #  DB Variables
    # ================================================
    # gamestates : A dictionary of created games containing all
    #              variables related to the corresponding game
    _GAMESTATES = 'gamestates'
    # games : A list of references to the created games
    _GAMES = 'games'
    # player_rooms : A dictionary of players containing a game
    #               token if the player is playing inside
    _PLAYER_ROOMS = 'player_rooms'
    # accounts : A dictionary of players containing
    #                   global player accounts
    _ACCOUNTS = 'accounts'
    # operator_fees : Sum of all operator fees retrieved
    _OPERATOR_FEES = 'operator_fees'

    # ================================================
    #  Error codes
    # ================================================
    _INVALID_PARTICIPATION_COST = 'INVALID_PARTICIPATION_COST'
    _FORBIDDEN_PARTICIPATION_COST = 'FORBIDDEN_PARTICIPATION_COST'
    _GAME_ALREADY_EXISTS = 'GAME_ALREADY_EXISTS'
    _GAME_DOESNT_EXIST = 'GAME_DOESNT_EXIST'
    _GAME_ALREADY_JOINED = 'GAME_ALREADY_JOINED'
    _NOT_ENOUGH_PLAYERS = 'NOT_ENOUGH_PLAYERS'
    _INVALID_GAME_HOST = 'INVALID_GAME_HOST'
    _CANNOT_DISTRIBUTE_BOMBS = 'CANNOT_DISTRIBUTE_BOMBS'
    _SENDER_NOT_SCORE_OWNER = 'SENDER_NOT_SCORE_OWNER'
    _PLAYER_HAS_NO_BOMB = 'PLAYER_HAS_NO_BOMB'
    _PLAYER_HAS_NO_SHIELD = 'PLAYER_HAS_NO_SHIELD'
    _PLAYER_ALREADY_DEAD = 'PLAYER_ALREADY_DEAD'
    _PLAYER_NOT_FOUND = 'PLAYER_NOT_FOUND'
    _DO_NOT_SUICIDE = 'DO_NOT_SUICIDE'
    _PLAYER_IS_NOT_LOOTABLE = 'PLAYER_IS_NOT_LOOTABLE'
    _BOMB_AFK_EXPLODED = 'BOMB_AFK_EXPLODED'
    _NOT_ENOUGH_FUNDS_FOR_REWARD = 'NOT_ENOUGH_FUNDS_FOR_REWARD'
    _PLAYER_ALREADY_REGISTERED = 'PLAYER_ALREADY_REGISTERED'
    _PLAYER_IS_NOT_REGISTERED = 'PLAYER_IS_NOT_REGISTERED'
    _GAME_NOT_STARTED = 'GAME_NOT_STARTED'
    _GAME_ALREADY_STARTED = 'GAME_ALREADY_STARTED'
    _READY_COUNTDOWN_ALREADY_STARTED = 'READY_COUNTDOWN_ALREADY_STARTED'
    _START_COUNTDOWN_NOT_STARTED = 'START_COUNTDOWN_NOT_STARTED'
    _READY_COUNTDOWN_NOT_REACHED = 'READY_COUNTDOWN_NOT_REACHED'
    _GAME_ALREADY_OVER = 'GAME_ALREADY_OVER'
    _CANNOT_CHANGE_HOST = 'CANNOT_CHANGE_HOST'
    _GAME_ISNT_VICTORY = 'GAME_ISNT_VICTORY'
    _PLAYER_IS_NOT_WINNER = 'PLAYER_IS_NOT_WINNER'
    _INVALID_ACCOUNT_NAME = 'INVALID_ACCOUNT_NAME'
    _NOT_ENOUGH_OPERATOR_FEES = 'NOT_ENOUGH_OPERATOR_FEES'
    _GAME_IS_FULL = 'GAME_IS_FULL'
    _MAXIMUM_GAMES_COUNT_REACHED = 'MAXIMUM_GAMES_COUNT_REACHED'

    # ================================================
    #  Constants
    # ================================================
    # Allowed participation cost
    _ALLOWED_PARTICIPATION_COST = [
        1   * 10 ** 18,
        2   * 10 ** 18,
        5   * 10 ** 18,
        10  * 10 ** 18,
        25  * 10 ** 18,
        50  * 10 ** 18,
        100 * 10 ** 18
    ]

    # Number of simultaneous games allowed
    _MAXIMUM_GAMES_COUNT = 10000

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._gamestates = DictDB(self._GAMESTATES, db, value_type=str)
        self._games = ArrayDB(self._GAMES, db, value_type=str)
        self._player_rooms = DictDB(self._PLAYER_ROOMS, db, value_type=str)
        self._accounts = DictDB(self._ACCOUNTS, db, value_type=str)
        self._operator_fees = VarDB(self._OPERATOR_FEES, db, value_type=int)

    def on_install(self) -> None:
        super().on_install()

    def on_update(self) -> None:
        super().on_update()

    # ================================================
    #  Checks
    # ================================================
    def _check_maximum_games_count(self) -> None:
        if len(self._games) >= self._MAXIMUM_GAMES_COUNT:
            raise MaximumGamesCountReached

    def _check_game_doesnt_exist(self, token: str) -> None:
        if token in self._games:
            raise GameAlreadyExists

    def _check_game_already_exists(self, token: str) -> None:
        if not token in self._games:
            raise GameDoesntExist

    def _check_is_score_operator(self, sender: Address) -> None:
        if self.owner != sender:
            raise SenderNotScoreOwner

    def _check_player_not_registered(self, address: str) -> None:
        if address in self._player_rooms:
            raise PlayerAlreadyRegistered

    def _check_player_registred(self, address: str) -> None:
        if not address in self._player_rooms:
            raise PlayerIsNotRegistered

    def _check_account_exists(self, address: str) -> None:
        if not address in self._accounts:
            raise AccountDoesntExist

    def _check_allowed_participation_cost(self, cost: int) -> None:
        if not cost in self._ALLOWED_PARTICIPATION_COST:
            raise ForbiddenParticipationCost

    def _check_enough_operator_fees(self, amount: int) -> None:
        current = self._operator_fees.get()
        if (amount < 0) or (current < amount):
            raise NotEnoughOperatorFees

    # ================================================
    #  Event Logs
    # ================================================
    @eventlog(indexed=3)
    def LootRewardEvent(self,
                        timestamp: int,
                        looter: Address,
                        looted: Address,
                        reward: int,
                        token: str) -> None:
        pass

    def _trigger_loot_reward_event(self,
                                   game: GameState,
                                   looter: Player,
                                   looted: Player,
                                   reward: int) -> None:
        looter_address = Address.from_string(looter.address)
        looted_address = Address.from_string(looted.address)
        game.add_event(self.tx.hash.hex())
        self.LootRewardEvent(self.now(), looter_address, looted_address, reward, game.token)

    @eventlog(indexed=2)
    def RefundRewardEvent(self, timestamp: int, address: Address, reward: int, token: str) -> None:
        pass

    def _trigger_refund_reward_event(self, game: GameState, player: Player, reward: int) -> None:
        address = Address.from_string(player.address)
        game.add_event(self.tx.hash.hex())
        self.RefundRewardEvent(self.now(), address, reward, game.token)

    @eventlog(indexed=2)
    def CreateGameEvent(self, timestamp: int, address: Address, token: str) -> None:
        pass

    def _trigger_create_game_event(self, game: GameState, player: Player) -> None:
        address = Address.from_string(player.address)
        game.add_event(self.tx.hash.hex())
        self.CreateGameEvent(self.now(), address, game.token)

    @eventlog(indexed=2)
    def StartGameEvent(self, timestamp: int, address: Address, token: str) -> None:
        pass

    def _trigger_start_game_event(self, game: GameState, player: Player) -> None:
        address = Address.from_string(player.address)
        game.add_event(self.tx.hash.hex())
        self.StartGameEvent(self.now(), address, game.token)

    @eventlog(indexed=2)
    def QuitGameEvent(self, timestamp: int, address: Address, token: str) -> None:
        pass

    def _trigger_quit_game_event(self, game: GameState, player: Player) -> None:
        address = Address.from_string(player.address)
        game.add_event(self.tx.hash.hex())
        self.QuitGameEvent(self.now(), address, game.token)

    @eventlog(indexed=2)
    def AfkStartGameEvent(self, timestamp: int, address: Address, token: str) -> None:
        pass

    def _trigger_afk_start_game_event(self, game: GameState, player: Player) -> None:
        address = Address.from_string(player.address)
        game.add_event(self.tx.hash.hex())
        self.AfkStartGameEvent(self.now(), address, game.token)

    @eventlog(indexed=2)
    def JoinGameEvent(self, timestamp: int, address: Address, token: str) -> None:
        pass

    def _trigger_join_game_event(self, game: GameState, player: Player) -> None:
        address = Address.from_string(player.address)
        game.add_event(self.tx.hash.hex())
        self.JoinGameEvent(self.now(), address, game.token)

    @eventlog(indexed=2)
    def RecvBombEvent(self, timestamp: int, receiver: Address, risk: int, token: str) -> None:
        pass

    def _trigger_recv_bomb_event(self, game: GameState, receiver: Player, bomb: Bomb) -> None:
        receiver_address = Address.from_string(receiver.address)
        game.add_event(self.tx.hash.hex())
        self.RecvBombEvent(self.now(), receiver_address, bomb.risk, game.token)

    @eventlog(indexed=2)
    def SendBombEvent(self,
                      timestamp: int,
                      sender: Address,
                      use_shield: bool,
                      risk: int,
                      token: str) -> None:
        pass

    def _trigger_send_bomb_event(self,
                                 game: GameState,
                                 sender: Player,
                                 use_shield: bool,
                                 bomb: Bomb) -> None:
        sender_address = Address.from_string(sender.address)
        game.add_event(self.tx.hash.hex())
        self.SendBombEvent(self.now(), sender_address, use_shield, bomb.risk, game.token)

    @eventlog(indexed=2)
    def ExplodedBombEvent(self, timestamp: int, exploded: Address, token: str) -> None:
        pass

    def _trigger_exploded_bomb_event(self, game: GameState, exploded: Player) -> None:
        exploded_address = Address.from_string(exploded.address)
        game.add_event(self.tx.hash.hex())
        self.ExplodedBombEvent(self.now(), exploded_address, game.token)

    @eventlog(indexed=2)
    def WinGameEvent(self, timestamp: int, winner: Address, amount: int, token: str) -> None:
        pass

    def _trigger_win_game_event(self, game: GameState, winner: Player) -> None:
        winner_address = Address.from_string(winner.address)
        game.add_event(self.tx.hash.hex())
        self.WinGameEvent(self.now(), winner_address, game.winner_reward(), game.token)

    @eventlog(indexed=2)
    def ReadyAskEvent(self, timestamp: int, host: Address) -> None:
        pass

    def _trigger_ready_ask_event(self, game: GameState, host: Player) -> None:
        host_address = Address.from_string(host.address)
        game.add_event(self.tx.hash.hex())
        self.ReadyAskEvent(self.now(), host_address)

    # ================================================
    #  Helpers
    # ================================================
    def _player_register_game(self, game: GameState, player: Player) -> None:
        self._player_rooms[player.address] = game.token

    def _player_unregister_game(self, player: Player, token: str) -> None:
        # Only unregister players still in the current game
        if self.get_player_room(player.address) == token:
            self._player_rooms.remove(player.address)

    def _get_gamestate_object(self, token: str) -> GameState:
        """ Must call _check_game_already_exists before """
        gamestate_json = self._get_gamestate(token)
        return GameState.from_json(gamestate_json)

    def _get_gamestate(self, token: str) -> str:
        """ Must call _check_game_already_exists before """
        return self._gamestates[token]

    def _get_player_room(self, address: str) -> str:
        """ Must call _check_player_registred before """
        return self._player_rooms[address]

    def _get_account(self, address: str) -> str:
        """ Must call _check_account_exists before """
        return self._accounts[address]

    def _get_account_object(self, address: str) -> Account:
        """ Must call _check_account_exists before """
        account_json = self._get_account(address)
        return Account.from_json(account_json)

    def _get_default_account(self, address: str) -> Account:
        # Give a pseudo random name to the player
        return Account(address, "Player_" + address[-4:])

    def _game_destroy(self, token: str) -> None:
        games = []
        # Iterate through games list and find the deleted game
        while self._games:
            cur = self._games.pop()
            if cur != token:
                games.append(cur)
            else:
                break

        # Add again the other games
        while games:
            cur = games.pop()
            self._games.put(cur)

    def _update_account_db(self, account: Account, address: str) -> None:
        self._accounts[address] = account.to_json()

    def _gamestate_cleanup(self, game: GameState, token: str) -> None:
        # Unregister all players to the game
        for player in game.get_all_players():
            self._player_unregister_game(player, token)
        # Cleanup the gamestate from the statedb
        self._gamestate_destroy(token)

    def _update_game_db(self, game: GameState, token: str) -> None:
        if game.is_over():
            self._gamestate_cleanup(game, token)
            self._game_destroy(token)
        else:
            self._gamestates[token] = game.to_json()

    def _gamestate_destroy(self, token: str) -> None:
        self._gamestates.remove(token)

    def _send_reward(self, game: GameState, player: Player, amount: int) -> None:
        address = Address.from_string(player.address)
        game.check_enough_reward(amount)
        game.withdraw_reward(amount)
        self.icx.transfer(address, amount)

    def _send_loot_reward(self, game: GameState, looter: Player, looted: Player) -> None:
        reward = game.get_loot_reward()
        self._send_reward(game, looter, reward)
        self._trigger_loot_reward_event(game, looter, looted, reward)

    def _send_win_reward(self, game: GameState, winner: Player, reward: int) -> None:
        self._send_reward(game, winner, reward)
        # Win Reward is already shared in WinGameEvent
        # We don't need to trigger another event for that

    def _refund_participation_cost(self, game: GameState, leaver: Player) -> None:
        refund = game.get_participation_cost()
        self._send_reward(game, leaver, refund)
        self._trigger_refund_reward_event(game, leaver, refund)

    def _send_operator_fees(self, game: GameState):
        new_fees = game.remaining_reward()
        current_fees = self._operator_fees.get()
        self._operator_fees.set(current_fees + new_fees)

    def _process_victory(self, game: GameState, winner: Player, reward: int) -> None:
        game.check_is_started()
        game.check_is_victory()
        game.check_winner(winner)
        # Only one player remaining, victory!
        self._send_win_reward(game, winner, reward)
        # Handle operator fees
        self._send_operator_fees(game)
        # Close the game
        game.over()

    # ================================================
    #  Extern methods
    # ================================================
    @payable
    @external(readonly=False)
    def create_game(self) -> None:
        amount = self.msg.value
        token = self.tx.hash.hex()
        created = self.now()
        address = str(self.msg.sender)

        # ==========================
        # Input Checks
        try:
            self._check_maximum_games_count()
            self._check_allowed_participation_cost(amount)
            self._check_game_doesnt_exist(token)
            self._check_player_not_registered(address)
        except ForbiddenParticipationCost:
            revert(self._FORBIDDEN_PARTICIPATION_COST)
        except GameAlreadyExists:
            revert(self._GAME_ALREADY_EXISTS)
        except PlayerAlreadyRegistered:
            revert(self._PLAYER_ALREADY_REGISTERED)
        except MaximumGamesCountReached:
            revert(self._MAXIMUM_GAMES_COUNT_REACHED)

        # ==========================
        # Build new GameState
        try:
            player = Player(address)
            game = GameState(token, amount, player.address, created)
            game.deposit_reward(amount)
            game.join(player)
            self._trigger_create_game_event(game, player)
            self._trigger_join_game_event(game, player)
        except GameAlreadyJoined:
            revert(self._GAME_ALREADY_JOINED)
        except GameIsFull:
            revert(self._GAME_IS_FULL)

        # ==========================
        # Update Game DB
        self._player_register_game(game, player)
        self._games.put(token)
        self._update_game_db(game, token)

    @payable
    @external(readonly=False)
    def join_game(self, token: str) -> None:
        amount = self.msg.value
        address = str(self.msg.sender)

        # ==========================
        # Input Checks
        try:
            self._check_player_not_registered(address)
        except PlayerAlreadyRegistered:
            revert(self._PLAYER_ALREADY_REGISTERED)

        # ==========================
        # Game Token Checks
        try:
            self._check_game_already_exists(token)
        except GameDoesntExist:
            revert(self._GAME_DOESNT_EXIST)

        # ==========================
        # Retrieve GameState
        game = self._get_gamestate_object(token)

        # ==========================
        # GameState Checks
        try:
            game.check_game_not_already_started()
            game.deposit_reward(amount)
        except GameAlreadyStarted:
            revert(self._GAME_ALREADY_STARTED)
        except InvalidParticipationCost:
            revert(self._INVALID_PARTICIPATION_COST)

        # ==========================
        # Process GameState
        try:
            player = Player(address)
            game.join(player)
            self._trigger_join_game_event(game, player)
        except GameAlreadyJoined:
            revert(self._GAME_ALREADY_JOINED)
        except GameIsFull:
            revert(self._GAME_IS_FULL)

        # ==========================
        # Update Game DB
        self._player_register_game(game, player)
        self._update_game_db(game, token)

    @external(readonly=False)
    def win_game(self) -> None:
        address = str(self.msg.sender)

        # ==========================
        # Input Checks
        try:
            self._check_player_registred(address)
        except PlayerIsNotRegistered:
            revert(self._PLAYER_IS_NOT_REGISTERED)

        # ==========================
        # Retrieve Game Token
        token = self._get_player_room(address)

        # ==========================
        # Game Token Checks
        try:
            self._check_game_already_exists(token)
        except GameDoesntExist:
            revert(self._GAME_DOESNT_EXIST)

        # ==========================
        # Retrieve GameState
        game = self._get_gamestate_object(token)

        # ==========================
        # Process GameState
        try:
            winner = game.get_player(address)
            reward = game.winner_reward()
            self._process_victory(game, winner, reward)
        except GameNotStarted:
            revert(self._GAME_NOT_STARTED)
        except GameIsntVictory:
            revert(self._GAME_ISNT_VICTORY)
        except PlayerIsNotWinner:
            revert(self._PLAYER_IS_NOT_WINNER)
        except NotEnoughFundsForReward:
            revert(self._NOT_ENOUGH_FUNDS_FOR_REWARD)
        except PlayerNotFound:
            revert(self._PLAYER_NOT_FOUND)
        except GameAlreadyOver:
            revert(self._GAME_ALREADY_OVER)

        # ==========================
        # Update Game DB
        self._update_game_db(game, token)

    @external(readonly=False)
    def loot_player(self, looted_address: str) -> None:
        seed = str(bytes.hex(self.tx.hash)) + str(self.now()) + str(self.msg.sender)
        now = self.now()
        looter_address = str(self.msg.sender)

        # ==========================
        # Input Checks
        try:
            self._check_player_registred(looter_address)
        except PlayerIsNotRegistered:
            revert(self._PLAYER_IS_NOT_REGISTERED)

        # ==========================
        # Retrieve Game Token
        token = self._get_player_room(looter_address)

        # ==========================
        # Game Token Checks
        try:
            self._check_game_already_exists(token)
        except GameDoesntExist:
            revert(self._GAME_DOESNT_EXIST)

        # ==========================
        # Retrieve GameState
        game = self._get_gamestate_object(token)

        # ==========================
        # Process GameState
        try:
            Utils.srand(seed)
            game.check_is_started()

            looter = game.get_player(looter_address)
            looted = game.get_player(looted_address)

            game.loot_player(looter, looted, now)

            # Send the looting reward for the looter
            self._send_loot_reward(game, looter, looted)

            if game.is_victory():
                # Warn everybody that we have a winner!
                # We need to trigger this event ahead of the
                # win_game call, because win_game destroys the game
                winner = game.get_winner()
                self._trigger_win_game_event(game, winner)

        except GameNotStarted:
            revert(self._GAME_NOT_STARTED)
        except PlayerNotFound:
            revert(self._PLAYER_NOT_FOUND)
        except DoNotSuicide:
            revert(self._DO_NOT_SUICIDE)
        except PlayerHasNoBomb:
            revert(self._PLAYER_HAS_NO_BOMB)
        except PlayerAlreadyDead:
            revert(self._PLAYER_ALREADY_DEAD)
        except PlayerIsNotLootable:
            revert(self._PLAYER_IS_NOT_LOOTABLE)
        except NotEnoughFundsForReward:
            revert(self._NOT_ENOUGH_FUNDS_FOR_REWARD)
        except CannotDistributeBombs:
            revert(self._CANNOT_DISTRIBUTE_BOMBS)

        # ==========================
        # Update Game DB
        self._update_game_db(game, token)

    @external(readonly=False)
    def send_bomb(self, use_shield: int) -> None:
        seed = str(bytes.hex(self.tx.hash)) + str(self.now()) + str(self.msg.sender)
        now = self.now()
        address = str(self.msg.sender)
        # Hack because ICON Python SDK doesn't support bool parameters
        # https://github.com/icon-project/icon-sdk-python/issues/30
        use_shield = False if (use_shield == 0) else True

        # ==========================
        # Input Checks
        try:
            self._check_player_registred(address)
        except PlayerIsNotRegistered:
            revert(self._PLAYER_IS_NOT_REGISTERED)

        # ==========================
        # Retrieve Game Token
        token = self._get_player_room(address)

        # ==========================
        # Game Token Checks
        try:
            self._check_game_already_exists(token)
        except GameDoesntExist:
            revert(self._GAME_DOESNT_EXIST)

        # ==========================
        # Retrieve GameState
        game = self._get_gamestate_object(token)

        # ==========================
        # Process GameState
        try:
            Utils.srand(seed)
            game.check_is_started()
            sender = game.get_player(address)
            bomb = sender.get_bomb()
            self._trigger_send_bomb_event(game, sender, use_shield, bomb)
            receiver = game.send_bomb(sender, now, use_shield)
            if receiver:
                bomb = receiver.get_bomb()
                self._trigger_recv_bomb_event(game, receiver, bomb)
            else:
                self._trigger_exploded_bomb_event(game, sender)
        except PlayerHasNoShield:
            revert(self._PLAYER_HAS_NO_SHIELD)
        except PlayerNotFound:
            revert(self._PLAYER_NOT_FOUND)
        except GameNotStarted:
            revert(self._GAME_NOT_STARTED)
        except PlayerHasNoBomb:
            revert(self._PLAYER_HAS_NO_BOMB)
        except PlayerAlreadyDead:
            revert(self._PLAYER_ALREADY_DEAD)
        except CannotDistributeBombs:
            revert(self._CANNOT_DISTRIBUTE_BOMBS)
        except BombAFKExploded:
            revert(self._BOMB_AFK_EXPLODED)

        # ==========================
        # Update Game DB
        self._update_game_db(game, token)

    @external(readonly=False)
    def ready_ask(self) -> None:
        address = str(self.msg.sender)
        now = self.now()

        # ==========================
        # Input Checks
        try:
            self._check_player_registred(address)
        except PlayerIsNotRegistered:
            revert(self._PLAYER_IS_NOT_REGISTERED)

        # ==========================
        # Retrieve Game Token
        token = self._get_player_room(address)

        # ==========================
        # Game Token Checks
        try:
            self._check_game_already_exists(token)
        except GameDoesntExist:
            revert(self._GAME_DOESNT_EXIST)

        # ==========================
        # Retrieve GameState
        game = self._get_gamestate_object(token)

        # ==========================
        # GameState Checks
        try:
            host = game.get_player(address)
            game.ready_ask(host, now)
            self._trigger_ready_ask_event(game, host)
        except PlayerNotFound:
            revert(self._PLAYER_NOT_FOUND)
        except GameAlreadyStarted:
            revert(self._GAME_ALREADY_STARTED)
        except ReadyCountdownAlreadyStarted:
            revert(self._READY_COUNTDOWN_ALREADY_STARTED)
        except NotEnoughPlayers:
            revert(self._NOT_ENOUGH_PLAYERS)
        except InvalidGameHost:
            revert(self._INVALID_GAME_HOST)

        # ==========================
        # Update Game DB
        self._update_game_db(game, token)

    @external(readonly=False)
    def ready_ok(self) -> None:
        address = str(self.msg.sender)

        # ==========================
        # Input Checks
        try:
            self._check_player_registred(address)
        except PlayerIsNotRegistered:
            revert(self._PLAYER_IS_NOT_REGISTERED)

        # ==========================
        # Retrieve Game Token
        token = self._get_player_room(address)

        # ==========================
        # Game Token Checks
        try:
            self._check_game_already_exists(token)
        except GameDoesntExist:
            revert(self._GAME_DOESNT_EXIST)

        # ==========================
        # Retrieve GameState
        game = self._get_gamestate_object(token)

        # ==========================
        # GameState Checks
        try:
            player = game.get_player(address)
            game.ready_ok(player)
        except PlayerNotFound:
            revert(self._PLAYER_NOT_FOUND)
        except GameAlreadyStarted:
            revert(self._GAME_ALREADY_STARTED)
        except StartCountdownNotStarted:
            revert(self._START_COUNTDOWN_NOT_STARTED)

        # ==========================
        # Update Game DB
        self._update_game_db(game, token)

    @external(readonly=False)
    def start_game(self) -> None:
        seed = str(bytes.hex(self.tx.hash)) + str(self.now()) + str(self.msg.sender)
        started = self.now()
        address = str(self.msg.sender)

        # ==========================
        # Input Checks
        try:
            self._check_player_registred(address)
        except PlayerIsNotRegistered:
            revert(self._PLAYER_IS_NOT_REGISTERED)

        # ==========================
        # Retrieve Game Token
        token = self._get_player_room(address)

        # ==========================
        # Game Token Checks
        try:
            self._check_game_already_exists(token)
        except GameDoesntExist:
            revert(self._GAME_DOESNT_EXIST)

        # ==========================
        # Retrieve GameState
        game = self._get_gamestate_object(token)

        # ==========================
        # GameState Checks
        try:
            player = game.get_player(address)
        except PlayerNotFound:
            revert(self._PLAYER_NOT_FOUND)

        # ==========================
        # Process GameState
        try:
            Utils.srand(seed)

            # Go!
            afkers = game.start(started)
            self._trigger_start_game_event(game, player)
            receiver = game.get_player_with_bomb()
            self._trigger_recv_bomb_event(game, receiver, receiver.get_bomb())

            # Remove & Refund players not ready
            for afker in afkers:
                self._player_unregister_game(afker, game.token)
                self._trigger_afk_start_game_event(game, afker)
                self._refund_participation_cost(game, afker)

        except GameAlreadyStarted:
            revert(self._GAME_ALREADY_STARTED)
        except ReadyCountdownNotReached:
            revert(self._READY_COUNTDOWN_NOT_REACHED)
        except CannotDistributeBombs:
            revert(self._CANNOT_DISTRIBUTE_BOMBS)
        except NotEnoughPlayers:
            revert(self._NOT_ENOUGH_PLAYERS)

        # ==========================
        # Update Game DB
        self._update_game_db(game, token)

    @external(readonly=False)
    def set_account_name(self, name: str) -> None:
        address = str(self.msg.sender)

        # ==========================
        # Retrieve Player Account
        try:
            self._check_account_exists(address)
        except AccountDoesntExist:
            # Create a new account
            account = self._get_default_account(address)
        else:
            # Get account from State DB
            account = self._get_account_object(address)

        # ==========================
        # Process Player Account
        try:
            account.set_name(name)
        except InvalidAccountName:
            revert(self._INVALID_ACCOUNT_NAME)

        # ==========================
        # Update Account DB
        self._update_account_db(account, address)

    @external(readonly=False)
    def quit_game(self) -> None:
        seed = str(bytes.hex(self.tx.hash)) + str(self.now()) + str(self.msg.sender)
        address = str(self.msg.sender)

        # ==========================
        # Input Checks
        try:
            self._check_player_registred(address)
        except PlayerIsNotRegistered:
            revert(self._PLAYER_IS_NOT_REGISTERED)

        # ==========================
        # Retrieve Game Token
        token = self._get_player_room(address)

        # ==========================
        # Game Token Checks
        try:
            self._check_game_already_exists(token)
        except GameDoesntExist:
            revert(self._GAME_DOESNT_EXIST)

        # ==========================
        # Retrieve GameState
        game = self._get_gamestate_object(token)

        # ==========================
        # Process GameState
        try:
            Utils.srand(seed)
            leaver = game.get_player(address)
            self._player_unregister_game(leaver, game.token)
            self._trigger_quit_game_event(game, leaver)

            # Refund the participation cost if the game hasn't started yet
            if not game.is_started():
                self._refund_participation_cost(game, leaver)
                game.quit(leaver)

        except PlayerNotFound:
            revert(self._PLAYER_NOT_FOUND)
        except CannotChangeHost:
            revert(self._CANNOT_CHANGE_HOST)
        except NotEnoughFundsForReward:
            revert(self._NOT_ENOUGH_FUNDS_FOR_REWARD)
        except GameAlreadyOver:
            revert(self._GAME_ALREADY_OVER)

        # ==========================
        # Update Game DB
        self._update_game_db(game, token)

    @external(readonly=True)
    def get_gamestate(self, token: str) -> str:
        try:
            self._check_game_already_exists(token)
        except GameDoesntExist:
            return ""
        return self._get_gamestate(token)

    @external(readonly=True)
    def get_account(self, address: str) -> str:
        try:
            self._check_account_exists(address)
        except AccountDoesntExist:
            return self._get_default_account(address).to_json()
        return self._get_account(address)

    @external(readonly=True)
    def get_operator_fees(self) -> int:
        return self._operator_fees.get()

    @external(readonly=True)
    def get_player_room(self, address: str) -> str:
        try:
            self._check_player_registred(address)
        except PlayerIsNotRegistered:
            return ""
        return self._get_player_room(address)

    @external(readonly=True)
    def get_all_gamestates(self) -> str:
        result = list(map(self.get_gamestate, self._games))
        return json_dumps(result)

    # =========================================
    # = [ Administration ] ====================
    # =========================================
    @external(readonly=False)
    def reset_games(self) -> None:
        # ==========================
        # Input Checks
        try:
            self._check_is_score_operator(self.msg.sender)
        except SenderNotScoreOwner:
            revert(self._SENDER_NOT_SCORE_OWNER)

        # ==========================
        # Process GameState
        for token in self._games:
            self.reset_game(token)
        # Cleanup references
        while self._games:
            self._games.pop()

    @external(readonly=False)
    def reset_player(self, address: Address) -> None:
        address = str(address)

        # ==========================
        # Input Checks
        try:
            self._check_is_score_operator(self.msg.sender)
            self._check_player_registred(address)
        except SenderNotScoreOwner:
            revert(self._SENDER_NOT_SCORE_OWNER)
        except PlayerIsNotRegistered:
            revert(self._PLAYER_IS_NOT_REGISTERED)

        # ==========================
        # Process Player
        # ==========================
        player = Player(address)
        self._player_unregister_game(player, self._get_player_room(player.address))

    @external(readonly=False)
    def reset_game(self, token: str) -> None:
        # ==========================
        # Input Checks
        try:
            self._check_is_score_operator(self.msg.sender)
        except SenderNotScoreOwner:
            revert(self._SENDER_NOT_SCORE_OWNER)

        # ==========================
        # Process GameState
        game = GameState.from_json(self._gamestates[token])

        # Refund players
        for player in game.get_all_players():
            self._refund_participation_cost(game, player)

        # Clean memory
        self._gamestate_cleanup(game, token)
        self._game_destroy(token)

    @external(readonly=False)
    def withdraw_operator_fees(self, address: Address, amount: int) -> None:
        # ==========================
        # Input Checks
        try:
            self._check_is_score_operator(self.msg.sender)
            self._check_enough_operator_fees(amount)
        except SenderNotScoreOwner:
            revert(self._SENDER_NOT_SCORE_OWNER)
        except NotEnoughOperatorFees:
            revert(self._NOT_ENOUGH_OPERATOR_FEES)

        current = self._operator_fees.get()
        self.icx.transfer(address, amount)
        self._operator_fees.set(current - amount)
