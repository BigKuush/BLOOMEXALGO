from typing import Dict, Set
from algosdk import account, mnemonic
from algosdk.future.transaction import LogicSig

class AccessControl:
    """
    Управление доступом к смарт-контрактам и функциям платформы
    """
    def __init__(self):
        self.roles: Dict[str, Set[str]] = {
            "ADMIN": set(),
            "BUSINESS_OWNER": set(),
            "INVESTOR": set(),
            "SUPPLY_CHAIN_OPERATOR": set(),
            "SOCIAL_IMPACT_OPERATOR": set()
        }
        self.role_permissions: Dict[str, Set[str]] = {
            "ADMIN": {
                "manage_roles",
                "manage_contracts",
                "manage_platform",
                "view_all"
            },
            "BUSINESS_OWNER": {
                "create_tokenization",
                "manage_business",
                "view_business_analytics"
            },
            "INVESTOR": {
                "stake_tokens",
                "view_investments",
                "participate_dao"
            },
            "SUPPLY_CHAIN_OPERATOR": {
                "manage_supply_chain",
                "update_tracking",
                "view_supply_analytics"
            },
            "SOCIAL_IMPACT_OPERATOR": {
                "manage_social_programs",
                "distribute_surplus",
                "view_impact_metrics"
            }
        }

    def add_role(self, address: str, role: str) -> bool:
        """Добавляет роль для адреса"""
        if role not in self.roles:
            raise ValueError(f"Invalid role: {role}")
        self.roles[role].add(address)
        return True

    def remove_role(self, address: str, role: str) -> bool:
        """Удаляет роль у адреса"""
        if role not in self.roles:
            raise ValueError(f"Invalid role: {role}")
        if address in self.roles[role]:
            self.roles[role].remove(address)
            return True
        return False

    def has_role(self, address: str, role: str) -> bool:
        """Проверяет наличие роли у адреса"""
        return address in self.roles.get(role, set())

    def has_permission(self, address: str, permission: str) -> bool:
        """Проверяет наличие разрешения у адреса"""
        for role, permissions in self.role_permissions.items():
            if self.has_role(address, role) and permission in permissions:
                return True
        return False

    @staticmethod
    def create_logic_signature(program: bytes, args: list = None) -> LogicSig:
        """Создает Logic Signature для смарт-контракта"""
        if args is None:
            args = []
        return LogicSig(program, args)
