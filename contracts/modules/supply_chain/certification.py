from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from algosdk import account, mnemonic
from algosdk.future.transaction import AssetConfigTxn

class CertificationType(Enum):
    ORGANIC = "ORGANIC"
    FAIR_TRADE = "FAIR_TRADE"
    SUSTAINABILITY = "SUSTAINABILITY"
    QUALITY = "QUALITY"
    ORIGIN = "ORIGIN"
    SAFETY = "SAFETY"

class CertificationStatus(Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    SUSPENDED = "SUSPENDED"

@dataclass
class CertificationDetails:
    cert_id: str
    type: CertificationType
    issuer: str
    holder: str
    issue_date: datetime
    expiry_date: datetime
    standards: List[str]
    audit_history: List[Dict]

class CertificationManager:
    """
    Управление сертификацией в цепочке поставок
    """
    def __init__(self, algod_client):
        self.algod_client = algod_client
        self.certifications: Dict[str, CertificationDetails] = {}
        self.issuers: Dict[str, Dict] = {}
        self.standards: Dict[str, Dict] = {}
        self.verification_history: Dict[str, List[Dict]] = {}
        
    def issue_certification(self,
                          cert_id: str,
                          cert_type: CertificationType,
                          holder: str,
                          details: Dict) -> Optional[str]:
        """
        Выпуск нового сертификата
        """
        if cert_id in self.certifications:
            return None
            
        # Проверяем авторизацию эмитента
        issuer = details.get('issuer')
        if issuer not in self.issuers:
            return None
            
        # Создаем NFT для сертификата
        params = self.algod_client.suggested_params()
        
        txn = AssetConfigTxn(
            sender=issuer,
            sp=params,
            total=1,
            default_frozen=False,
            unit_name="BLXC",
            asset_name=f"BloomexCert_{cert_id}",
            manager=issuer,
            reserve=issuer,
            freeze=issuer,
            clawback=issuer,
            url=f"https://bloomex.io/certificates/{cert_id}",
            decimals=0
        )
        
        try:
            signed_txn = txn.sign(details['issuer_key'])
            tx_id = self.algod_client.send_transaction(signed_txn)
            confirmed_txn = wait_for_confirmation(self.algod_client, tx_id, 4)
            asset_id = confirmed_txn["asset-index"]
            
            # Создаем запись о сертификате
            certification = CertificationDetails(
                cert_id=cert_id,
                type=cert_type,
                issuer=issuer,
                holder=holder,
                issue_date=datetime.now(),
                expiry_date=datetime.now() + timedelta(days=details.get('validity_days', 365)),
                standards=details.get('standards', []),
                audit_history=[{
                    'timestamp': datetime.now().isoformat(),
                    'action': 'ISSUED',
                    'auditor': issuer
                }]
            )
            
            self.certifications[cert_id] = certification
            
            # Инициализируем историю верификации
            self.verification_history[cert_id] = [{
                'timestamp': datetime.now().isoformat(),
                'status': CertificationStatus.ACTIVE.value,
                'verifier': issuer,
                'notes': 'Initial certification'
            }]
            
            return cert_id
            
        except Exception as e:
            print(f"Error issuing certification: {e}")
            return None

    def verify_certification(self,
                           cert_id: str,
                           verifier: str,
                           verification_data: Dict) -> bool:
        """
        Верификация сертификата
        """
        if cert_id not in self.certifications:
            return False
            
        cert = self.certifications[cert_id]
        
        # Проверяем срок действия
        if datetime.now() > cert.expiry_date:
            self._update_certification_status(cert_id, CertificationStatus.EXPIRED)
            return False
            
        # Записываем верификацию
        self.verification_history[cert_id].append({
            'timestamp': datetime.now().isoformat(),
            'verifier': verifier,
            'data': verification_data,
            'status': CertificationStatus.ACTIVE.value
        })
        
        return True

    def _update_certification_status(self,
                                   cert_id: str,
                                   status: CertificationStatus) -> None:
        """
        Обновление статуса сертификата
        """
        if cert_id in self.verification_history:
            self.verification_history[cert_id].append({
                'timestamp': datetime.now().isoformat(),
                'status': status.value,
                'verifier': 'SYSTEM',
                'notes': f'Status updated to {status.value}'
            })

    def register_issuer(self,
                       issuer_address: str,
                       credentials: Dict,
                       certification_types: List[CertificationType]) -> bool:
        """
        Регистрация эмитента сертификатов
        """
        if issuer_address in self.issuers:
            return False
            
        self.issuers[issuer_address] = {
            'credentials': credentials,
            'certification_types': [ct.value for ct in certification_types],
            'active': True,
            'registered_at': datetime.now().isoformat()
        }
        
        return True

    def add_certification_standard(self,
                                 standard_id: str,
                                 details: Dict) -> bool:
        """
        Добавление нового стандарта сертификации
        """
        if standard_id in self.standards:
            return False
            
        self.standards[standard_id] = {
            'name': details.get('name'),
            'description': details.get('description'),
            'requirements': details.get('requirements', []),
            'certification_type': details.get('certification_type'),
            'created_at': datetime.now().isoformat()
        }
        
        return True

    def get_certification_status(self, cert_id: str) -> Optional[Dict]:
        """
        Получение статуса сертификата
        """
        if cert_id not in self.certifications:
            return None
            
        cert = self.certifications[cert_id]
        current_status = self.verification_history[cert_id][-1]
        
        return {
            'cert_id': cert_id,
            'type': cert.type.value,
            'issuer': cert.issuer,
            'holder': cert.holder,
            'issue_date': cert.issue_date.isoformat(),
            'expiry_date': cert.expiry_date.isoformat(),
            'current_status': current_status['status'],
            'standards': cert.standards,
            'last_verified': current_status['timestamp']
        }

    def get_verification_history(self, cert_id: str) -> Optional[List[Dict]]:
        """
        Получение истории верификац��и сертификата
        """
        if cert_id not in self.verification_history:
            return None
            
        return self.verification_history[cert_id]

    def revoke_certification(self,
                           cert_id: str,
                           issuer: str,
                           reason: str) -> bool:
        """
        Отзыв сертификата
        """
        if cert_id not in self.certifications:
            return False
            
        cert = self.certifications[cert_id]
        
        if cert.issuer != issuer:
            return False
            
        self._update_certification_status(cert_id, CertificationStatus.REVOKED)
        
        # Добавляем запись в историю аудита
        cert.audit_history.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'REVOKED',
            'auditor': issuer,
            'reason': reason
        })
        
        return True

    def extend_certification(self,
                           cert_id: str,
                           issuer: str,
                           extension_days: int) -> bool:
        """
        Продление срока действия сертификата
        """
        if cert_id not in self.certifications:
            return False
            
        cert = self.certifications[cert_id]
        
        if cert.issuer != issuer:
            return False
            
        cert.expiry_date += timedelta(days=extension_days)
        
        # Добавляем запись в историю аудита
        cert.audit_history.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'EXTENDED',
            'auditor': issuer,
            'extension_days': extension_days
        })
        
        return True
