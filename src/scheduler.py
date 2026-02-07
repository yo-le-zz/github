"""
Ordonnanceur pour la vérification périodique des changements Git.
"""

import time
import sys
from typing import Optional
from config import Config
from git_manager import GitManager
from token_store import TokenStore


class Scheduler:
    """Ordonnanceur pour la vérification périodique des changements."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialise l'ordonnanceur.
        
        Args:
            config_path: Chemin vers le fichier de configuration
        """
        self.config = Config(config_path)
        self.git_manager = None
        self.running = False
    
    def start(self) -> bool:
        """
        Démarre l'ordonnanceur.
        
        Returns:
            True si le démarrage a réussi, False sinon
        """
        # Charger la configuration
        if not self.config.load():
            print("Erreur: Impossible de charger la configuration.")
            print("Veuillez lancer l'assistant de configuration d'abord.")
            return False
        
        # Valider la configuration
        if not self.config.is_valid():
            print("Erreur: Configuration invalide.")
            return False
        
        # Initialiser le gestionnaire Git
        project_path = self.config.get_project_path()
        self.git_manager = GitManager(str(project_path))
        
        # Vérifier que le repository existe
        if not self.git_manager.is_repo():
            print(f"Erreur: {project_path} n'est pas un repository Git.")
            return False
        
        print(f"Démarrage de la surveillance du repository: {project_path}")
        print(f"Branche surveillée: {self.config.get_branch()}")
        print(f"Intervalle de vérification: {self.config.get_check_interval()} secondes")
        print("Appuyez sur Ctrl+C pour arrêter.")
        print("-" * 60)
        
        self.running = True
        self._main_loop()
        
        return True
    
    def stop(self) -> None:
        """Arrête l'ordonnanceur."""
        self.running = False
        print("\nArrêt de la surveillance...")
    
    def _main_loop(self) -> None:
        """Boucle principale de vérification."""
        last_check_time = 0
        check_interval = self.config.get_check_interval()
        
        try:
            while self.running:
                current_time = time.time()
                
                # Vérifier si l'intervalle est écoulé
                if current_time - last_check_time >= check_interval:
                    self._check_for_changes()
                    last_check_time = current_time
                
                # Attendre un peu avant la prochaine vérification
                time.sleep(1)
        
        except KeyboardInterrupt:
            self.stop()
    
    def _check_for_changes(self) -> None:
        """Vérifie les changements distants et locaux."""
        try:
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] Vérification des changements...")
            
            # Récupérer le token si nécessaire
            token = None
            if self.config.is_private_repo():
                token = TokenStore.get_token()
                if not token:
                    print("⚠️ Token GitHub non trouvé. Vérification des changements distants impossible.")
                    return
            
            # Fetch des changements distants
            if not self.git_manager.fetch(token):
                print("❌ Erreur lors du fetch des changements distants")
                return
            
            # Vérifier les changements distants
            branch = self.config.get_branch()
            if self.git_manager.has_changes(branch):
                print("🔄 Changements distants détectés!")
                self._handle_remote_changes(branch)
            else:
                print("✓ Aucun changement distant")
            
            # Vérifier les changements locaux
            if self.git_manager.has_local_changes():
                print("📝 Changements locaux détectés")
                self._handle_local_changes(branch)
            else:
                print("✓ Aucun changement local")
        
        except Exception as e:
            print(f"❌ Erreur lors de la vérification: {e}")
    
    def _handle_remote_changes(self, branch: str) -> None:
        """
        Gère les changements distants.
        
        Args:
            branch: Nom de la branche
        """
        try:
            # Afficher un résumé des changements
            diff_summary = self.git_manager.get_diff_summary(branch)
            print("\nRésumé des changements distants:")
            print("-" * 40)
            print(diff_summary)
            print("-" * 40)
            
            # Demander confirmation pour fusionner
            response = input("\nFusionner les changements distants? (o/n): ").strip().lower()
            
            if response in ['o', 'oui', 'yes', 'y']:
                if self.git_manager.merge_remote_changes(branch):
                    print("✅ Fusion réussie")
                else:
                    print("❌ Erreur lors de la fusion")
            else:
                print("⏸️ Fusion annulée")
        
        except Exception as e:
            print(f"❌ Erreur lors de la gestion des changements distants: {e}")
    
    def _handle_local_changes(self, branch: str) -> None:
        """
        Gère les changements locaux.
        
        Args:
            branch: Nom de la branche
        """
        try:
            # Vérifier si le push automatique est activé
            if not self.config.is_auto_push_enabled():
                print("📝 Changements locaux détectés (push automatique désactivé)")
                return
            
            # Afficher le status
            status = self.git_manager.get_status()
            print("\nStatus local:")
            print("-" * 40)
            print(status)
            print("-" * 40)
            
            # Demander confirmation si nécessaire
            should_push = True
            if self.config.is_confirm_push_enabled():
                response = input("\nPusher les changements locaux? (o/n): ").strip().lower()
                should_push = response in ['o', 'oui', 'yes', 'y']
            
            if should_push:
                self._push_local_changes(branch)
            else:
                print("⏸️ Push annulé")
        
        except Exception as e:
            print(f"❌ Erreur lors de la gestion des changements locaux: {e}")
    
    def _push_local_changes(self, branch: str) -> None:
        """
        Pousse les changements locaux vers le repository distant.
        
        Args:
            branch: Nom de la branche
        """
        try:
            # Ajouter tous les fichiers
            if not self.git_manager.add_all():
                print("❌ Erreur lors de l'ajout des fichiers")
                return
            
            # Créer un commit
            commit_message = f"Auto-commit - {time.strftime('%Y-%m-%d %H:%M:%S')}"
            if not self.git_manager.commit(commit_message):
                print("❌ Erreur lors du commit")
                return
            
            print("✅ Commit créé")
            
            # Récupérer le token si nécessaire
            token = None
            if self.config.is_private_repo():
                token = TokenStore.get_token()
                if not token:
                    print("⚠️ Token GitHub non trouvé. Push impossible.")
                    return
            
            # Pusher les changements
            if self.git_manager.push(branch, token):
                print("✅ Push réussi")
            else:
                print("❌ Erreur lors du push")
        
        except Exception as e:
            print(f"❌ Erreur lors du push: {e}")


def main():
    """Point d'entrée pour l'ordonnanceur."""
    scheduler = Scheduler()
    
    try:
        success = scheduler.start()
        if not success:
            input("Appuyez sur Entrée pour quitter...")
            sys.exit(1)
    except KeyboardInterrupt:
        scheduler.stop()
        print("\nAu revoir!")
        sys.exit(0)


if __name__ == "__main__":
    main()
