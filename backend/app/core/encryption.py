"""
API Key 加密/解密工具
使用 AES 对称加密保护敏感信息
"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import os
from .config import settings


class EncryptionService:
    """加密服务"""
    
    def __init__(self):
        # 从环境变量获取加密密钥，如果不存在则生成一个
        encryption_key = getattr(settings, 'encryption_key', None)
        if not encryption_key:
            # 生产环境应该从环境变量读取
            encryption_key = os.getenv('ENCRYPTION_KEY', 'default-encryption-key-change-in-production')
        
        # 使用 PBKDF2HMAC 从密钥派生出 Fernet 需要的格式
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'chattalk_salt',  # 生产环境应该使用随机 salt
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(encryption_key.encode()))
        self.cipher = Fernet(key)
    
    def encrypt(self, plain_text: str) -> str:
        """
        加密文本
        
        Args:
            plain_text: 明文
            
        Returns:
            加密后的文本（Base64编码）
        """
        if not plain_text:
            return ""
        
        encrypted = self.cipher.encrypt(plain_text.encode())
        return encrypted.decode()
    
    def decrypt(self, encrypted_text: str) -> str:
        """
        解密文本
        
        Args:
            encrypted_text: 加密的文本
            
        Returns:
            解密后的明文
        """
        if not encrypted_text:
            return ""
        
        try:
            decrypted = self.cipher.decrypt(encrypted_text.encode())
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"解密失败: {str(e)}")
    
    @staticmethod
    def mask_api_key(api_key: str, show_chars: int = 4) -> str:
        """
        遮蔽 API Key，只显示前几位
        
        Args:
            api_key: API Key
            show_chars: 显示的字符数
            
        Returns:
            遮蔽后的字符串，例如 "sk-1234****"
        """
        if not api_key or len(api_key) <= show_chars:
            return api_key
        
        return api_key[:show_chars] + '*' * (len(api_key) - show_chars)


# 全局加密服务实例
encryption_service = EncryptionService()


# 辅助函数（向后兼容）
def encrypt_api_key(api_key: str) -> str:
    """加密 API Key"""
    return encryption_service.encrypt(api_key)


def decrypt_api_key(encrypted_key: str) -> str:
    """解密 API Key"""
    return encryption_service.decrypt(encrypted_key)


def mask_api_key(api_key: str, show_chars: int = 4) -> str:
    """遮蔽 API Key"""
    return EncryptionService.mask_api_key(api_key, show_chars)
