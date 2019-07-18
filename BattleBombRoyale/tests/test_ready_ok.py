import os

from iconsdk.builder.transaction_builder import DeployTransactionBuilder
from iconsdk.builder.call_builder import CallBuilder
from iconsdk.icon_service import IconService
from iconsdk.libs.in_memory_zip import gen_deploy_data_content
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.signed_transaction import SignedTransaction

from tbears.libs.icon_integrate_test import IconIntegrateTestBase, SCORE_INSTALL_ADDRESS
from BattleBombRoyale.tests.utils import *

DIR_PATH = os.path.abspath(os.path.dirname(__file__))

class TestBattleBombRoyale(IconIntegrateTestBase):
    TEST_HTTP_ENDPOINT_URI_V3 = "http://127.0.0.1:9000/api/v3"
    SCORE_PROJECT= os.path.abspath(os.path.join(DIR_PATH, '..'))

    _PARTICIPATION_COST = 1 * 10**18

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
    
    def ready_ask(self):
        # OK
        result = transaction_call_success(super(), 
            from_=self._j1, 
            to_=self._score_address, 
            method="ready_ask", 
            icon_service=self.icon_service
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
    def test_ready_ok_ok(self):
        self.ready_ask()
        # OK
        result = transaction_call_success(super(), 
            from_=self._j2, 
            to_=self._score_address, 
            method="ready_ok", 
            icon_service=self.icon_service
        )

    def test_ready_ok_PLAYER_IS_NOT_REGISTERED (self):
        self.ready_ask()
        # Fail
        result = transaction_call_error(super(), 
            from_=self._j3, 
            to_=self._score_address, 
            method="ready_ok", 
            icon_service=self.icon_service
        )
        self.assertEqual(result['failure']['message'], 'PLAYER_IS_NOT_REGISTERED')

    def test_ready_ok_GAME_ALREADY_STARTED (self):
        self.ready_ask()
        # OK
        result = transaction_call_success(super(), 
            from_=self._j2, 
            to_=self._score_address, 
            method="ready_ok", 
            icon_service=self.icon_service
        )
        # OK
        result = transaction_call_success(super(), 
            from_=self._j1, 
            to_=self._score_address, 
            method="start_game", 
            icon_service=self.icon_service
        )
        # Fail
        result = transaction_call_error(super(), 
            from_=self._j2, 
            to_=self._score_address, 
            method="ready_ok", 
            icon_service=self.icon_service
        )
        self.assertEqual(result['failure']['message'], 'GAME_ALREADY_STARTED')

    def test_ready_ok_START_COUNTDOWN_NOT_STARTED (self):
        # Fail
        result = transaction_call_error(super(), 
            from_=self._j2, 
            to_=self._score_address, 
            method="ready_ok", 
            icon_service=self.icon_service
        )
        self.assertEqual(result['failure']['message'], 'START_COUNTDOWN_NOT_STARTED')
