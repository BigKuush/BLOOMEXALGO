from typing import Optional
from algosdk.future.transaction import LogicSig

class ContractProxy:
    """
    Прокси для обновляемых смарт-контрактов
    """
    def __init__(self, app_id: int):
        self.app_id = app_id
        self.current_version: int = 1
        self.implementations: dict = {}
        self.active_implementation: Optional[str] = None

    def register_implementation(self, version: int, logic_sig: LogicSig):
        """Регистрирует новую версию контракта"""
        self.implementations[version] = logic_sig
        
    def upgrade(self, new_version: int) -> bool:
        """Обновляет контракт до новой версии"""
        if new_version not in self.implementations:
            raise ValueError(f"Implementation version {new_version} not found")
        if new_version <= self.current_version:
            raise ValueError("New version must be greater than current version")
        
        self.current_version = new_version
        return True

    def get_current_implementation(self) -> Optional[LogicSig]:
        """Возвращает текущую имплементацию контракта"""
        return self.implementations.get(self.current_version)

    def is_upgradeable(self) -> bool:
        """Проверяет, можно ли обновить контракт"""
        return len(self.implementations) > self.current_version
