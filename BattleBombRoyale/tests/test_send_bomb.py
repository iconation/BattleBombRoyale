import os, json, time
import logging

from iconsdk.builder.transaction_builder import DeployTransactionBuilder
from iconsdk.builder.call_builder import CallBuilder
from iconsdk.icon_service import IconService
from iconsdk.libs.in_memory_zip import gen_deploy_data_content
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.signed_transaction import SignedTransaction

from tbears.libs.icon_integrate_test import IconIntegrateTestBase, SCORE_INSTALL_ADDRESS

from BattleBombRoyale.tests.utils import *
from BattleBombRoyale.gamestate.gamestate import GameState
from BattleBombRoyale.player.player import Player
from BattleBombRoyale.bomb.bomb import Bomb

DIR_PATH = os.path.abspath(os.path.dirname(__file__))

class TestBattleBombRoyale(IconIntegrateTestBase):
    TEST_HTTP_ENDPOINT_URI_V3 = "http://127.0.0.1:9000/api/v3"
    SCORE_PROJECT= os.path.abspath(os.path.join(DIR_PATH, '..'))

    _PARTICIPATION_COST = 1 * 10**18

    def get_gamestate(self, token):
        # OK
        result = icx_call(super(), 
            from_=self._j1.get_address(), 
            to_=self._score_address, 
            method="get_gamestate",
            params={'token': token},
            icon_service=self.icon_service,
        )
        result = json.loads(result)
        return GameState.deserialize(result)

    def generate_blocks(self, count):
        # Generates 10 blocks
        for _ in range(count):
            result = icx_transfer_call(super(),
                from_=self._j1, 
                to_=self._j1.get_address(), 
                icon_service=self.icon_service,
                value=0
            )

    def refresh_state(self):
        self.gamestate = self.get_gamestate(self._token)
        self._has_bomb = list(filter(lambda player: player.has_bomb(), self.gamestate.get_all_players()))[0]
        self._has_bomb_wallet = list(filter(lambda wallet: wallet.address == self._has_bomb.address, self._wallet_array))[0]

        self._players_no_bomb = list(filter(lambda player: not player.has_bomb(), self.gamestate.get_all_players()))
        self._wallets_no_bomb = []
        for player in self._players_no_bomb:
            for wallet in self._wallet_array:
                if player.address == wallet.get_address():
                    self._wallets_no_bomb.append(wallet)

    def start_game(self):
        # OK
        result = transaction_call_success(super(), 
            from_=self._j1, 
            to_=self._score_address, 
            method="start_game", 
            icon_service=self.icon_service
        )

        self.refresh_state()

    def set_ready(self):
        # OK
        result = transaction_call_success(super(), 
            from_=self._j1, 
            to_=self._score_address, 
            method="ready_ask", 
            icon_service=self.icon_service
        )

        # OK
        result = transaction_call_success(super(), 
            from_=self._j2, 
            to_=self._score_address, 
            method="ready_ok", 
            icon_service=self.icon_service
        )
        # OK
        result = transaction_call_success(super(), 
            from_=self._j3, 
            to_=self._score_address, 
            method="ready_ok", 
            icon_service=self.icon_service
        )

    def setUp(self):
        super().setUp()

        self.icon_service = None
        # if you want to send request to network, uncomment next line and set self.TEST_HTTP_ENDPOINT_URI_V3
        # self.icon_service = IconService(HTTPProvider(self.TEST_HTTP_ENDPOINT_URI_V3))

        # install SCORE
        self._score_address = self._deploy_score()['scoreAddress']

        self._j1 = self._wallet_array[0]
        self._j2 = self._wallet_array[1]
        self._j3 = self._wallet_array[2]
        self._j4 = self._wallet_array[3]
        self._spectator = self._wallet_array[9]

        for wallet in self._wallet_array:
            icx_transfer_call(super(), self._test1, wallet.get_address(), 100 * 10**18, self.icon_service)

        # ==================================================================
        # !! Some tests below assume there are only 3 players in the game !!
        # ==================================================================
        # OK
        result = transaction_call_success(super(), 
            from_=self._j1, 
            to_=self._score_address, 
            method="create_game", 
            icon_service=self.icon_service,
            value=self._PARTICIPATION_COST
        )
        self._token = result['txHash']

        # OK
        result = transaction_call_success(super(), 
            from_=self._j2, 
            to_=self._score_address, 
            method="join_game", 
            params={'token': self._token},
            icon_service=self.icon_service,
            value=self._PARTICIPATION_COST
        )

        # OK
        result = transaction_call_success(super(), 
            from_=self._j3, 
            to_=self._score_address, 
            method="join_game", 
            params={'token': self._token},
            icon_service=self.icon_service,
            value=self._PARTICIPATION_COST
        )

    def _deploy_score(self, to: str = SCORE_INSTALL_ADDRESS) -> dict:
        # Generates an instance of transaction for deploying SCORE.
        transaction = DeployTransactionBuilder() \
            .from_(self._test1.get_address()) \
            .to(to) \
            .step_limit(100_000_000_000) \
            .nid(3) \
            .nonce(100) \
            .content_type("application/zip") \
            .content(gen_deploy_data_content(self.SCORE_PROJECT)) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, self._test1)

        # process the transaction in local
        result = self.process_transaction(signed_transaction, self.icon_service)

        self.assertTrue('status' in result)
        self.assertEqual(1, result['status'])
        self.assertTrue('scoreAddress' in result)

        return result

    # ===============================================================
    def test_send_bomb_no_shield_ok(self):
        self.set_ready()
        self.start_game()
        # OK
        result = transaction_call_success(super(), 
            from_=self._has_bomb_wallet, 
            to_=self._score_address, 
            method="send_bomb", 
            icon_service=self.icon_service,
            params={"use_shield" : 0}
        )

    def test_send_bomb_shield_ok(self):
        self.set_ready()
        self.start_game()
        # OK
        result = transaction_call_success(super(), 
            from_=self._has_bomb_wallet, 
            to_=self._score_address, 
            method="send_bomb", 
            icon_service=self.icon_service,
            params={"use_shield" : 1}
        )

    def test_send_bomb_METHOD_NOT_PAYABLE(self):
        self.set_ready()
        self.start_game()
        # Fail
        result = transaction_call_error(super(), 
            from_=self._has_bomb_wallet, 
            to_=self._score_address, 
            method="send_bomb", 
            icon_service=self.icon_service,
            params={"use_shield" : 0},
            value=123
        )
        self.assertTrue('Method not payable' in result['failure']['message'])

    def test_send_bomb_PLAYER_HAS_NO_BOMB(self):
        self.set_ready()
        self.start_game()
        # Fail
        result = transaction_call_error(super(), 
            from_=self._wallets_no_bomb[0], 
            to_=self._score_address, 
            method="send_bomb", 
            params={"use_shield" : 0},
            icon_service=self.icon_service
        )
        self.assertEqual(result['failure']['message'], 'PLAYER_HAS_NO_BOMB')

    def test_send_bomb_BOMB_AFK_EXPLODED(self):
        self.set_ready()
        self.start_game()
        time.sleep(Bomb._BOMB_TIME_FOR_AFK_EXPLODING / 1000)
        # Fail
        result = transaction_call_error(super(), 
            from_=self._has_bomb_wallet,
            to_=self._score_address,
            method="send_bomb",
            params={"use_shield" : 0},
            icon_service=self.icon_service
        )
        self.assertEqual(result['failure']['message'], 'BOMB_AFK_EXPLODED')

    def test_send_bomb_GAME_NOT_STARTED(self):
        # Fail
        result = transaction_call_error(super(), 
            from_=self._j1,
            to_=self._score_address,
            method="send_bomb",
            params={"use_shield" : 0},
            icon_service=self.icon_service
        )
        self.assertEqual(result['failure']['message'], 'GAME_NOT_STARTED')

    def test_send_bomb_PLAYER_HAS_NO_SHIELD(self):
        self.set_ready()
        self.start_game()

        # OK
        first = self._has_bomb
        result = transaction_call_success(super(), 
            from_=self._has_bomb_wallet,
            to_=self._score_address,
            method="send_bomb",
            params={"use_shield" : 1},
            icon_service=self.icon_service
        )
        self.refresh_state()

        # OK
        second = self._has_bomb
        result = transaction_call_success(super(), 
            from_=self._has_bomb_wallet,
            to_=self._score_address,
            method="send_bomb",
            params={"use_shield" : 1},
            icon_service=self.icon_service
        )
        self.refresh_state()

        if self._has_bomb != first and self._has_bomb != second:
            # OK
            result = transaction_call_success(super(), 
                from_=self._has_bomb_wallet,
                to_=self._score_address,
                method="send_bomb",
                params={"use_shield" : 1},
                icon_service=self.icon_service
            )
            self.refresh_state()

        # Fail
        result = transaction_call_error(super(), 
            from_=self._has_bomb_wallet,
            to_=self._score_address,
            method="send_bomb",
            params={"use_shield" : 1},
            icon_service=self.icon_service
        )
        self.assertEqual(result['failure']['message'], 'PLAYER_HAS_NO_SHIELD')
