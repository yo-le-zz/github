"""
Désinstallation propre de GitHub Viewer.
"""

import os
import sys
import shutil
from pathlib import Path
from typing import List
from config import Config
from token_store import TokenStore
from startup import StartupManager


class UninstallManager:
    """Gestionnaire de désinstallation pour GitHub Viewer."""
    
    def __init__(self):
        """Initialise le gestionnaire de désinstallation."""
        self.app_name = "GitHub Viewer"
        self.config = Config()
        self.startup_manager = StartupManager()
    
    def uninstall(self) -> bool:
        """
        Désinstalle complètement GitHub Viewer.
        
        Returns:
            True si la désinstallation a réussi, False sinon
        """
        print("=" * 60)
        print("Désinstallation de GitHub Viewer")
        print("=" * 60)
        print()
        
        # Confirmation
        if not self._confirm_uninstall():
            print("Désinstallation annulée.")
            return False
        
        # Étapes de désinstallation
        steps = [
            ("Retrait du démarrage Windows", self._remove_from_startup),
            ("Suppression du token GitHub", self._remove_token),
            ("Suppression du fichier de configuration", self._remove_config),
            ("Suppression des fichiers de l'application", self._remove_app_files),
        ]
        
        success = True
        for step_name, step_func in steps:
            print(f"\n{step_name}...")
            try:
                if step_func():
                    print(f"✅ {step_name} terminé")
                else:
                    print(f"⚠️ {step_name} échoué (peut-être déjà fait)")
            except Exception as e:
                print(f"❌ Erreur lors de {step_name.lower()}: {e}")
                success = False
        
        # Résumé
        print("\n" + "=" * 60)
        if success:
            print("Désinstallation terminée avec succès!")
            print("GitHub Viewer a été complètement supprimé de votre système.")
        else:
            print("Désinstallation terminée avec des erreurs.")
            print("Certains éléments n'ont pas pu être supprimés.")
        print("=" * 60)
        
        return success
    
    def _confirm_uninstall(self) -> bool:
        """
        Demande confirmation pour la désinstallation.
        
        Returns:
            True si confirmé, False sinon
        """
        print("Cette action va:")
        print("- Retirer GitHub Viewer du démarrage Windows")
        print("- Supprimer le token GitHub stocké")
        print("- Supprimer le fichier de configuration")
        print("- Supprimer tous les fichiers de l'application")
        print()
        print("Les repositories locaux clonés ne seront PAS supprimés.")
        print("Seuls les fichiers de l'application seront effacés.")
        print()
        
        while True:
            response = input("Confirmer la désinstallation? (o/n): ").strip().lower()
            
            if response in ['o', 'oui', 'yes', 'y']:
                return True
            elif response in ['n', 'non', 'no']:
                return False
            else:
                print("Réponse invalide. Répondez par 'o' ou 'n'.")
    
    def _remove_from_startup(self) -> bool:
        """
        Retire l'application du démarrage Windows.
        
        Returns:
            True si réussi, False sinon
        """
        return self.startup_manager.remove_from_startup()
    
    def _remove_token(self) -> bool:
        """
        Supprime le token GitHub stocké.
        
        Returns:
            True si réussi, False sinon
        """
        if TokenStore.has_token():
            return TokenStore.delete_token()
        else:
            # Pas de token à supprimer
            return True
    
    def _remove_config(self) -> bool:
        """
        Supprime le fichier de configuration.
        
        Returns:
            True si réussi, False sinon
        """
        try:
            config_path = self.config.config_path
            
            if config_path.exists():
                config_path.unlink()
                print(f"Fichier de configuration supprimé: {config_path}")
                return True
            else:
                # Fichier déjà supprimé
                return True
        
        except Exception as e:
            print(f"Erreur lors de la suppression du fichier de configuration: {e}")
            return False
    
    def _remove_app_files(self) -> bool:
        """
        Supprime les fichiers de l'application.
        
        Returns:
            True si réussi, False sinon
        """
        try:
            # Récupérer le chemin de l'application
            if getattr(sys, 'frozen', False):
                # Mode compilé - supprimer l'exécutable
                app_path = Path(sys.executable)
                
                if app_path.exists():
                    # Créer un script batch pour supprimer l'exécutable après la fermeture
                    self._create_self_deletion_script(app_path)
                    print("Les fichiers de l'application seront supprimés à la fermeture.")
                    return True
                else:
                    return True
            else:
                # Mode développement - supprimer le dossier src
                app_dir = Path(__file__).parent
                
                if app_dir.exists() and app_dir.name == "src":
                    # Supprimer les fichiers Python
                    python_files = list(app_dir.glob("*.py"))
                    for py_file in python_files:
                        py_file.unlink()
                        print(f"Fichier supprimé: {py_file}")
                    
                    return True
                else:
                    return True
        
        except Exception as e:
            print(f"Erreur lors de la suppression des fichiers: {e}")
            return False
    
    def _create_self_deletion_script(self, exe_path: Path) -> None:
        """
        Crée un script batch pour auto-suppression.
        
        Args:
            exe_path: Chemin de l'exécutable à supprimer
        """
        try:
            # Créer un script batch temporaire
            script_path = exe_path.parent / "uninstall.bat"
            
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write('@echo off\n')
                f.write('echo Suppression de GitHub Viewer...\n')
                f.write('timeout /t 2 /nobreak >nul\n')
                f.write(f'del "{exe_path}"\n')
                f.write(f'del "%~f0"\n')  # Auto-suppression du script
            
            # Lancer le script en arrière-plan
            import subprocess
            subprocess.Popen([str(script_path)], creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        except Exception as e:
            print(f"Erreur lors de la création du script de suppression: {e}")
    
    def get_installed_components(self) -> List[str]:
        """
        Liste les composants installés.
        
        Returns:
            Liste des composants installés
        """
        components = []
        
        # Vérifier le démarrage
        if self.startup_manager.is_in_startup():
            components.append("Démarrage Windows")
        
        # Vérifier le token
        if TokenStore.has_token():
            components.append("Token GitHub")
        
        # Vérifier la configuration
        if self.config.config_path.exists():
            components.append("Fichier de configuration")
        
        # Vérifier les fichiers de l'application
        if getattr(sys, 'frozen', False):
            components.append("Exécutable")
        else:
            src_dir = Path(__file__).parent
            if src_dir.exists():
                components.append("Fichiers source")
        
        return components


def main():
    """Point d'entrée pour la désinstallation."""
    uninstall_manager = UninstallManager()
    
    print("GitHub Viewer - Désinstallation")
    print("=" * 40)
    
    # Afficher les composants installés
    components = uninstall_manager.get_installed_components()
    if components:
        print("Composants installés détectés:")
        for component in components:
            print(f"  - {component}")
        print()
    else:
        print("Aucun composant installé détecté.")
        print("L'application semble déjà désinstallée.")
        input("Appuyez sur Entrée pour quitter...")
        return
    
    # Lancer la désinstallation
    success = uninstall_manager.uninstall()
    
    if success:
        print("\nMerci d'avoir utilisé GitHub Viewer!")
    
    input("\nAppuyez sur Entrée pour quitter...")
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
