"""
Gestion de la configuration de GitHub Viewer.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Gestionnaire de configuration pour GitHub Viewer."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialise le gestionnaire de configuration.
        
        Args:
            config_path: Chemin vers le fichier config.json
        """
        if config_path is None:
            # Chemin par défaut dans le dossier de l'exécutable
            if getattr(sys, 'frozen', False):
                # Mode compilé avec Nuitka
                base_dir = Path(sys.executable).parent
            else:
                # Mode développement
                base_dir = Path(__file__).parent.parent
            
            config_path = base_dir / "config" / "config.json"
        
        self.config_path = Path(config_path)
        self._config_data = {}
    
    def load(self) -> bool:
        """
        Charge la configuration depuis le fichier.
        
        Returns:
            True si le chargement a réussi, False sinon
        """
        try:
            if not self.config_path.exists():
                print(f"Fichier de configuration non trouvé: {self.config_path}")
                return False
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config_data = json.load(f)
            
            return True
        except json.JSONDecodeError as e:
            print(f"Erreur de format JSON dans le fichier de configuration: {e}")
            return False
        except Exception as e:
            print(f"Erreur lors du chargement de la configuration: {e}")
            return False
    
    def save(self, config_data: Dict[str, Any]) -> bool:
        """
        Sauvegarde la configuration dans le fichier.
        
        Args:
            config_data: Données de configuration à sauvegarder
            
        Returns:
            True si la sauvegarde a réussi, False sinon
        """
        try:
            # Créer le dossier config si nécessaire
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            self._config_data = config_data
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la configuration: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Récupère une valeur de configuration.
        
        Args:
            key: Clé de configuration
            default: Valeur par défaut si la clé n'existe pas
            
        Returns:
            Valeur de configuration ou valeur par défaut
        """
        return self._config_data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Définit une valeur de configuration.
        
        Args:
            key: Clé de configuration
            value: Valeur à définir
        """
        self._config_data[key] = value
    
    def is_valid(self) -> bool:
        """
        Vérifie si la configuration est valide.
        
        Returns:
            True si la configuration est valide, False sinon
        """
        required_keys = ['project_path', 'repo_url', 'branch', 'check_interval']
        
        for key in required_keys:
            if key not in self._config_data:
                print(f"Clé de configuration manquante: {key}")
                return False
        
        # Validation des valeurs
        if not self._config_data['project_path']:
            print("Le chemin du projet ne peut pas être vide")
            return False
        
        if not self._config_data['repo_url']:
            print("L'URL du repository ne peut pas être vide")
            return False
        
        if not self._config_data['branch']:
            print("Le nom de la branche ne peut pas être vide")
            return False
        
        try:
            interval = int(self._config_data['check_interval'])
            if interval <= 0:
                print("L'intervalle de vérification doit être positif")
                return False
        except ValueError:
            print("L'intervalle de vérification doit être un nombre entier")
            return False
        
        return True
    
    def get_project_path(self) -> Path:
        """Récupère le chemin du projet."""
        return Path(self.get('project_path', ''))
    
    def get_repo_url(self) -> str:
        """Récupère l'URL du repository."""
        return self.get('repo_url', '')
    
    def get_branch(self) -> str:
        """Récupère le nom de la branche."""
        return self.get('branch', 'main')
    
    def get_check_interval(self) -> int:
        """Récupère l'intervalle de vérification en secondes."""
        return int(self.get('check_interval', 300))
    
    def is_auto_push_enabled(self) -> bool:
        """Vérifie si le push automatique est activé."""
        return self.get('auto_push', False)
    
    def is_confirm_push_enabled(self) -> bool:
        """Vérifie si la confirmation avant push est activée."""
        return self.get('confirm_push', True)
    
    def is_private_repo(self) -> bool:
        """Vérifie si le repository est privé."""
        return self.get('is_private', False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Retourne la configuration sous forme de dictionnaire."""
        return self._config_data.copy()
