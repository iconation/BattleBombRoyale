import os

from iconsdk.builder.transaction_builder import DeployTransactionBuilder
from iconsdk.builder.call_builder import CallBuilder
from iconsdk.icon_service import IconService
from iconsdk.libs.in_memory_zip import gen_deploy_data_content
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.signed_transaction import SignedTransaction

from tbears.libs.icon_integrate_test import IconIntegrateTestBase, SCORE_INSTALL_ADDRESS
from BattleBombRoyale.tests.utils import *
from BattleBombRoyale.utils.utils import Utils, SeedUninitialized

DIR_PATH = os.path.abspath(os.path.dirname(__file__))

class TestBattleBombRoyale(IconIntegrateTestBase):
    TEST_HTTP_ENDPOINT_URI_V3 = "http://127.0.0.1:9000/api/v3"
    SCORE_PROJECT= os.path.abspath(os.path.join(DIR_PATH, '..'))

    def setUp(self):
        super().setUp()

    # ===============================================================
    def test_rand_ok(self):
        Utils.srand(bytes.fromhex('b10f89b37dab8d58f1ed92aef0ad6b8d4c0a91d5e3a0ab89f24175e2dbca5ad9'), False)
        result = Utils.rand(0, 0xffffffffffffffff)
        self.assertEqual(result, 17136562176724798638)
        Utils.srand(bytes.fromhex('00'), False)

    def test_unitialized_rand(self):
        ok = False
        try:
            Utils.rand(1, 2)
        except SeedUninitialized as error:
            ok = True
        self.assertTrue(ok)
        
