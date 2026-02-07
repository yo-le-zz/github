"""
Assistant de configuration initiale pour GitHub Viewer.
"""

import os
import sys
from pathlib import Path
from typing import Optional
from config import Config
from git_manager import GitManager
from token_store import TokenStore


class SetupWizard:
    """Assistant de configuration pour GitHub Viewer."""
    
    def __init__(self):
        """Initialise l'assistant de configuration."""
        self.config = Config()
    
    def run(self) -> bool:
        """
        Lance l'assistant de configuration.
        
        Returns:
            True si la configuration a réussi, False sinon
        """
        print("=" * 60)
        print("GitHub Viewer - Assistant de configuration")
        print("=" * 60)
        print()
        
        # Vérifier si Git est installé
        if not self._check_git_installation():
            return False
        
        # Collecter les informations de configuration
        config_data = {}
        
        # Chemin du projet
        config_data['project_path'] = self._get_project_path()
        
        # URL du repository
        config_data['repo_url'] = self._get_repo_url()
        
        # Déterminer si le repository est privé
        config_data['is_private'] = self._is_private_repo(config_data['repo_url'])
        
        # Token GitHub si nécessaire
        if config_data['is_private']:
            if not self._setup_github_token():
                print("Configuration annulée.")
                return False
        
        # Branche cible
        config_data['branch'] = self._get_target_branch()
        
        # Intervalle de vérification
        config_data['check_interval'] = self._get_check_interval()
        
        # Options de push
        config_data['auto_push'] = self._get_auto_push_option()
        config_data['confirm_push'] = self._get_confirm_push_option()
        
        # Sauvegarder la configuration
        if not self.config.save(config_data):
            print("Erreur lors de la sauvegarde de la configuration.")
            return False
        
        # Cloner le repository
        if not self._setup_repository(config_data):
            print("Erreur lors de la configuration du repository.")
            return False
        
        print("\n" + "=" * 60)
        print("Configuration terminée avec succès!")
        print(f"Repository: {config_data['repo_url']}")
        print(f"Branche: {config_data['branch']}")
        print(f"Chemin local: {config_data['project_path']}")
        print(f"Intervalle de vérification: {config_data['check_interval']} secondes")
        print("=" * 60)
        
        # Proposer l'ajout au démarrage Windows
        self._propose_startup_addition()
        
        return True
    
    def _check_git_installation(self) -> bool:
        """
        Vérifie si Git est installé.
        
        Returns:
            True si Git est installé, False sinon
        """
        print("Vérification de l'installation de Git...")
        
        git_manager = GitManager(".")
        if git_manager.is_git_installed():
            print("✓ Git est installé")
            return True
        else:
            print("✗ Git n'est pas installé")
            print("\nGit est requis pour utiliser GitHub Viewer.")
            print("Veuillez installer Git depuis: https://git-scm.com/download/win")
            print("Après installation, relancez cet assistant.")
            return False
    
    def _get_project_path(self) -> str:
        """
        Demande le chemin du projet.
        
        Returns:
            Chemin du projet
        """
        while True:
            print("\nChemin du dossier local:")
            print("Exemples:")
            print("  C:\\Users\\Nom\\Documents\\mon-projet")
            print("  D:\\Projects\\github-viewer")
            path = input("Entrez le chemin complet: ").strip()
            
            if not path:
                print("Le chemin ne peut pas être vide.")
                continue
            
            # Convertir en chemin absolu
            project_path = Path(path).resolve()
            
            # Créer le dossier s'il n'existe pas
            try:
                project_path.mkdir(parents=True, exist_ok=True)
                print(f"✓ Dossier prêt: {project_path}")
                return str(project_path)
            except Exception as e:
                print(f"Erreur lors de la création du dossier: {e}")
                continue
    
    def _get_repo_url(self) -> str:
        """
        Demande l'URL du repository.
        
        Returns:
            URL du repository
        """
        while True:
            print("\nURL du repository GitHub:")
            print("Exemples:")
            print("  https://github.com/utilisateur/repo.git")
            print("  git@github.com:utilisateur/repo.git")
            url = input("Entrez l'URL du repository: ").strip()
            
            if not url:
                print("L'URL ne peut pas être vide.")
                continue
            
            # Normaliser l'URL en HTTPS
            if url.startswith('git@'):
                url = url.replace('git@github.com:', 'https://github.com/')
                url += '.git' if not url.endswith('.git') else ''
            elif not url.startswith('https://'):
                print("Veuillez utiliser une URL HTTPS (https://github.com/...)")
                continue
            
            return url
    
    def _is_private_repo(self, repo_url: str) -> bool:
        """
        Détermine si le repository est privé.
        
        Args:
            repo_url: URL du repository
            
        Returns:
            True si le repository est privé, False sinon
        """
        while True:
            print(f"\nRepository: {repo_url}")
            response = input("Ce repository est-il privé? (o/n): ").strip().lower()
            
            if response in ['o', 'oui', 'yes', 'y']:
                return True
            elif response in ['n', 'non', 'no']:
                return False
            else:
                print("Réponse invalide. Répondez par 'o' ou 'n'.")
    
    def _setup_github_token(self) -> bool:
        """
        Configure le token GitHub.
        
        Returns:
            True si la configuration a réussi, False sinon
        """
        print("\nConfiguration du token GitHub:")
        print("Pour accéder à un repository privé, vous avez besoin d'un Personal Access Token.")
        print("1. Allez sur https://github.com/settings/tokens")
        print("2. Cliquez sur 'Generate new token (classic)'")
        print("3. Donnez un nom au token et cochez 'repo'")
        print("4. Copiez le token généré")
        
        token = input("\nEntrez votre token GitHub: ").strip()
        
        if not token:
            print("Aucun token fourni.")
            return False
        
        # Tester le token
        print("Test du token...")
        if TokenStore.store_token(token):
            print("✓ Token stocké avec succès")
            return True
        else:
            print("✗ Erreur lors du stockage du token")
            return False
    
    def _get_target_branch(self) -> str:
        """
        Demande la branche cible.
        
        Returns:
            Nom de la branche
        """
        print("\nBranche cible:")
        print("Exemples: main, master, develop, feature/nouvelle-fonctionnalite")
        
        while True:
            branch = input("Entrez le nom de la branche: ").strip()
            
            if not branch:
                print("Le nom de la branche ne peut pas être vide.")
                continue
            
            return branch
    
    def _get_check_interval(self) -> int:
        """
        Demande l'intervalle de vérification.
        
        Returns:
            Intervalle en secondes
        """
        print("\nIntervalle de vérification des changements:")
        print("Entrez la durée en secondes entre chaque vérification.")
        print("Exemples: 300 (5 minutes), 600 (10 minutes), 1800 (30 minutes)")
        
        while True:
            interval_str = input("Entrez l'intervalle (en secondes): ").strip()
            
            try:
                interval = int(interval_str)
                if interval <= 0:
                    print("L'intervalle doit être positif.")
                    continue
                
                minutes = interval // 60
                seconds = interval % 60
                
                if minutes > 0:
                    print(f"Vérification toutes les {minutes} minute(s)" + 
                          (f" {seconds} seconde(s)" if seconds > 0 else ""))
                else:
                    print(f"Vérification toutes les {seconds} secondes")
                
                return interval
            
            except ValueError:
                print("Veuillez entrer un nombre entier valide.")
    
    def _get_auto_push_option(self) -> bool:
        """
        Demande si le push automatique est activé.
        
        Returns:
            True si le push automatique est activé, False sinon
        """
        while True:
            response = input("\nActiver le push automatique des changements locaux? (o/n): ").strip().lower()
            
            if response in ['o', 'oui', 'yes', 'y']:
                return True
            elif response in ['n', 'non', 'no']:
                return False
            else:
                print("Réponse invalide. Répondez par 'o' ou 'n'.")
    
    def _get_confirm_push_option(self) -> bool:
        """
        Demande si la confirmation avant push est activée.
        
        Returns:
            True si la confirmation est activée, False sinon
        """
        while True:
            response = input("\nDemander confirmation avant chaque push? (o/n): ").strip().lower()
            
            if response in ['o', 'oui', 'yes', 'y']:
                return True
            elif response in ['n', 'non', 'no']:
                return False
            else:
                print("Réponse invalide. Répondez par 'o' ou 'n'.")
    
    def _setup_repository(self, config_data: dict) -> bool:
        """
        Configure le repository local.
        
        Args:
            config_data: Données de configuration
            
        Returns:
            True si la configuration a réussi, False sinon
        """
        print("\nConfiguration du repository local...")
        
        project_path = config_data['project_path']
        repo_url = config_data['repo_url']
        branch = config_data['branch']
        
        git_manager = GitManager(project_path)
        
        # Vérifier si le repository existe déjà
        if git_manager.is_repo():
            print("✓ Repository Git déjà présent")
            return True
        
        # Cloner le repository
        print("Clonage du repository...")
        token = TokenStore.get_token() if config_data['is_private'] else None
        
        if git_manager.clone(repo_url, branch, token):
            print("✓ Repository cloné avec succès")
            return True
        else:
            print("✗ Erreur lors du clonage")
            return False
    
    def _propose_startup_addition(self) -> None:
        """Propose l'ajout au démarrage Windows."""
        from .startup import StartupManager
        
        print("\nAjout au démarrage Windows:")
        response = input("Ajouter GitHub Viewer au démarrage de Windows? (o/n): ").strip().lower()
        
        if response in ['o', 'oui', 'yes', 'y']:
            startup_manager = StartupManager()
            if startup_manager.add_to_startup():
                print("✓ GitHub Viewer sera lancé au démarrage de Windows")
            else:
                print("✗ Erreur lors de l'ajout au démarrage")
        else:
            print("GitHub Viewer ne sera pas ajouté au démarrage")


def main():
    """Point d'entrée pour l'assistant de configuration."""
    wizard = SetupWizard()
    success = wizard.run()
    
    if success:
        print("\nConfiguration terminée. Vous pouvez maintenant lancer GitHub Viewer.")
        input("Appuyez sur Entrée pour quitter...")
    else:
        print("\nÉchec de la configuration.")
        input("Appuyez sur Entrée pour quitter...")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
