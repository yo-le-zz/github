"""
Point d'entrée principal pour GitHub Viewer.
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

# Ajouter le répertoire src au chemin Python pour les imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from config import Config
from setup_wizard import SetupWizard
from scheduler import Scheduler
from startup import StartupManager
from uninstall import UninstallManager


class GitHubViewer:
    """Application principale GitHub Viewer."""
    
    def __init__(self):
        """Initialise l'application."""
        self.config = Config()
        self.setup_wizard = SetupWizard()
        self.scheduler = Scheduler()
        self.startup_manager = StartupManager()
        self.uninstall_manager = UninstallManager()
    
    def run(self, args: Optional[argparse.Namespace] = None) -> int:
        """
        Lance l'application avec les arguments fournis.
        
        Args:
            args: Arguments de ligne de commande
            
        Returns:
            Code de sortie (0 pour succès, 1 pour erreur)
        """
        if args is None:
            args = self._parse_args()
        
        try:
            # Route vers la fonction appropriée
            if args.command == "setup":
                return self._run_setup()
            elif args.command == "start":
                return self._run_scheduler()
            elif args.command == "startup":
                return self._run_startup_manager()
            elif args.command == "uninstall":
                return self._run_uninstall()
            elif args.command == "status":
                return self._show_status()
            else:
                # Mode par défaut: vérifier la config et lancer
                return self._run_default()
        
        except KeyboardInterrupt:
            print("\nOpération annulée par l'utilisateur.")
            return 0
        except Exception as e:
            print(f"Erreur: {e}")
            return 1
    
    def _parse_args(self) -> argparse.Namespace:
        """
        Parse les arguments de ligne de commande.
        
        Returns:
            Arguments parsés
        """
        parser = argparse.ArgumentParser(
            prog="github_viewer",
            description="Agent Windows pour la surveillance de repositories GitHub"
        )
        
        subparsers = parser.add_subparsers(dest="command", help="Commandes disponibles")
        
        # Setup
        setup_parser = subparsers.add_parser("setup", help="Lancer l'assistant de configuration")
        
        # Start
        start_parser = subparsers.add_parser("start", help="Démarrer la surveillance")
        
        # Startup
        startup_parser = subparsers.add_parser("startup", help="Gérer le démarrage Windows")
        
        # Uninstall
        uninstall_parser = subparsers.add_parser("uninstall", help="Désinstaller l'application")
        
        # Status
        status_parser = subparsers.add_parser("status", help="Afficher le statut")
        
        return parser.parse_args()
    
    def _run_setup(self) -> int:
        """
        Lance l'assistant de configuration.
        
        Returns:
            Code de sortie
        """
        success = self.setup_wizard.run()
        return 0 if success else 1
    
    def _run_scheduler(self) -> int:
        """
        Lance l'ordonnanceur de surveillance.
        
        Returns:
            Code de sortie
        """
        success = self.scheduler.start()
        return 0 if success else 1
    
    def _run_startup_manager(self) -> int:
        """
        Lance le gestionnaire de démarrage.
        
        Returns:
            Code de sortie
        """
        from startup import main as startup_main
        startup_main()
        return 0
    
    def _run_uninstall(self) -> int:
        """
        Lance la désinstallation.
        
        Returns:
            Code de sortie
        """
        from uninstall import main as uninstall_main
        uninstall_main()
        return 0
    
    def _show_status(self) -> int:
        """
        Affiche le statut de l'application.
        
        Returns:
            Code de sortie
        """
        print("GitHub Viewer - Statut")
        print("=" * 40)
        
        # Configuration
        if self.config.load():
            print("✅ Configuration chargée")
            print(f"Repository: {self.config.get_repo_url()}")
            print(f"Branche: {self.config.get_branch()}")
            print(f"Chemin local: {self.config.get_project_path()}")
            print(f"Intervalle: {self.config.get_check_interval()}s")
            print(f"Push auto: {'Oui' if self.config.is_auto_push_enabled() else 'Non'}")
            print(f"Repository privé: {'Oui' if self.config.is_private_repo() else 'Non'}")
        else:
            print("❌ Configuration non trouvée ou invalide")
        
        print()
        
        # Token
        from token_store import TokenStore
        if TokenStore.has_token():
            print("✅ Token GitHub configuré")
        else:
            print("❌ Token GitHub non configuré")
        
        print()
        
        # Démarrage Windows
        print(self.startup_manager.get_startup_status())
        
        print()
        
        # Repository local
        if self.config.load():
            from git_manager import GitManager
            git_manager = GitManager(str(self.config.get_project_path()))
            if git_manager.is_repo():
                print("✅ Repository local trouvé")
                if git_manager.has_local_changes():
                    print("📝 Changements locaux détectés")
                else:
                    print("✅ Aucun changement local")
            else:
                print("❌ Repository local non trouvé")
        
        return 0
    
    def _run_default(self) -> int:
        """
        Comportement par défaut: vérifier la config et propose des options.
        
        Returns:
            Code de sortie
        """
        print("GitHub Viewer")
        print("=" * 40)
        
        # Vérifier si la configuration existe
        if not self.config.load():
            print("Aucune configuration trouvée.")
            print("Lancement de l'assistant de configuration...")
            return self._run_setup()
        
        # Valider la configuration
        if not self.config.is_valid():
            print("Configuration invalide.")
            print("Lancement de l'assistant de configuration...")
            return self._run_setup()
        
        # Configuration trouvée - afficher le menu
        print("Configuration trouvée:")
        print(f"Repository: {self.config.get_repo_url()}")
        print(f"Branche: {self.config.get_branch()}")
        print(f"Chemin local: {self.config.get_project_path()}")
        print()
        
        # Menu interactif
        while True:
            print("Que souhaitez-vous faire?")
            print("1. Démarrer la surveillance")
            print("2. Quitter")
            print("3. Désinstaller l'application")
            print("4. Afficher le statut détaillé")
            print("5. Relancer la configuration")
            
            try:
                choice = input("\nVotre choix (1-5): ").strip()
                
                if choice == "1":
                    print("\nDémarrage de la surveillance...")
                    return self._run_scheduler()
                elif choice == "2":
                    print("\nAu revoir!")
                    return 0
                elif choice == "3":
                    return self._run_uninstall()
                elif choice == "4":
                    print()
                    self._show_status()
                    print()
                    input("Appuyez sur Entrée pour continuer...")
                    print()
                elif choice == "5":
                    print("\nRelancement de la configuration...")
                    return self._run_setup()
                else:
                    print("Choix invalide. Réessayez.")
                    
            except KeyboardInterrupt:
                print("\n\nAu revoir!")
                return 0
            except EOFError:
                print("\n\nAu revoir!")
                return 0


def main():
    """Point d'entrée principal."""
    # Vérifier la version Python
    if sys.version_info < (3, 11):
        print("Erreur: Python 3.11 ou supérieur est requis.")
        print(f"Version actuelle: {sys.version}")
        input("Appuyez sur Entrée pour quitter...")
        sys.exit(1)
    
    # Lancer l'application
    app = GitHubViewer()
    exit_code = app.run()
    
    # Si en mode interactif, attendre avant de quitter
    if not getattr(sys, 'frozen', False) and len(sys.argv) <= 1:
        input("\nAppuyez sur Entrée pour quitter...")
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
