"""
Gestion sécurisée des tokens GitHub via keyring Windows.
"""

import keyring
import sys
from typing import Optional


class TokenStore:
    """Gestionnaire de token GitHub sécurisé via keyring."""
    
    SERVICE_NAME = "github_viewer"
    TOKEN_KEY = "github_token"
    
    @staticmethod
    def store_token(token: str) -> bool:
        """
        Stocke le token GitHub de manière sécurisée.
        
        Args:
            token: Token GitHub à stocker
            
        Returns:
            True si le stockage a réussi, False sinon
        """
        try:
            keyring.set_password(TokenStore.SERVICE_NAME, TokenStore.TOKEN_KEY, token)
            return True
        except Exception as e:
            print(f"Erreur lors du stockage du token: {e}")
            return False
    
    @staticmethod
    def get_token() -> Optional[str]:
        """
        Récupère le token GitHub stocké.
        
        Returns:
            Token GitHub ou None si non trouvé/erreur
        """
        try:
            return keyring.get_password(TokenStore.SERVICE_NAME, TokenStore.TOKEN_KEY)
        except Exception as e:
            print(f"Erreur lors de la récupération du token: {e}")
            return None
    
    @staticmethod
    def delete_token() -> bool:
        """
        Supprime le token GitHub stocké.
        
        Returns:
            True si la suppression a réussi, False sinon
        """
        try:
            keyring.delete_password(TokenStore.SERVICE_NAME, TokenStore.TOKEN_KEY)
            return True
        except Exception as e:
            print(f"Erreur lors de la suppression du token: {e}")
            return False
    
    @staticmethod
    def has_token() -> bool:
        """
        Vérifie si un token est stocké.
        
        Returns:
            True si un token est stocké, False sinon
        """
        return TokenStore.get_token() is not None
