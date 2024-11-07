import unittest
from wallet_management.wallets.wallet_types import WalletType
from wallet_management.wallets.team_wallets import TeamWallet

class TestWalletManagement(unittest.TestCase):
    def setUp(self):
        self.test_wallet = TeamWallet()

    def test_wallet_type(self):
        self.assertEqual(self.test_wallet.wallet_type, WalletType.TEAM)

    def test_wallet_creation(self):
        self.assertIsNotNone(self.test_wallet)

if __name__ == '__main__':
    unittest.main()
