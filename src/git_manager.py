"""
Gestionnaire des opérations Git pour GitHub Viewer.
"""

import subprocess
import os
import sys
from pathlib import Path
from typing import List, Tuple, Optional, Dict
import difflib


class GitManager:
    """Gestionnaire des opérations Git."""
    
    def __init__(self, repo_path: str):
        """
        Initialise le gestionnaire Git.
        
        Args:
            repo_path: Chemin vers le repository local
        """
        self.repo_path = Path(repo_path)
    
    def _run_git_command(self, args: List[str], capture_output: bool = True) -> Tuple[bool, str, str]:
        """
        Exécute une commande Git.
        
        Args:
            args: Arguments de la commande Git
            capture_output: Si True, capture la sortie
            
        Returns:
            Tuple (succès, stdout, stderr)
        """
        try:
            cmd = ['git'] + args
            env = os.environ.copy()
            
            # Désactiver les prompts interactifs
            env['GIT_TERMINAL_PROMPT'] = '0'
            
            if capture_output:
                result = subprocess.run(
                    cmd,
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    env=env
                )
                return result.returncode == 0, result.stdout, result.stderr
            else:
                result = subprocess.run(
                    cmd,
                    cwd=self.repo_path,
                    env=env
                )
                return result.returncode == 0, "", ""
        
        except Exception as e:
            return False, "", f"Erreur lors de l'exécution de la commande Git: {e}"
    
    def is_git_installed(self) -> bool:
        """
        Vérifie si Git est installé.
        
        Returns:
            True si Git est installé, False sinon
        """
        success, _, _ = self._run_git_command(['--version'])
        return success
    
    def is_repo(self) -> bool:
        """
        Vérifie si le chemin est un repository Git.
        
        Returns:
            True si c'est un repository Git, False sinon
        """
        git_dir = self.repo_path / '.git'
        return git_dir.exists() or git_dir.is_file()
    
    def clone(self, url: str, branch: str = None, token: str = None) -> bool:
        """
        Clone un repository.
        
        Args:
            url: URL du repository
            branch: Branche à cloner (optionnel)
            token: Token pour les repositories privés (optionnel)
            
        Returns:
            True si le clone a réussi, False sinon
        """
        try:
            # Créer le dossier parent si nécessaire
            self.repo_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Construire l'URL avec token si nécessaire
            clone_url = url
            if token and 'github.com' in url:
                # Remplacer l'URL pour inclure le token
                if url.startswith('https://'):
                    clone_url = url.replace('https://', f'https://{token}@')
            
            # Préparer la commande de clone
            args = ['clone', clone_url, str(self.repo_path)]
            if branch:
                args.extend(['--branch', branch])
            
            success, stdout, stderr = self._run_git_command(args, capture_output=False)
            
            if success:
                print(f"Repository cloné avec succès dans {self.repo_path}")
                return True
            else:
                print(f"Erreur lors du clone: {stderr}")
                return False
        
        except Exception as e:
            print(f"Erreur lors du clone: {e}")
            return False
    
    def fetch(self, token: str = None) -> bool:
        """
        Récupère les changements distants.
        
        Args:
            token: Token pour les repositories privés (optionnel)
            
        Returns:
            True si le fetch a réussi, False sinon
        """
        try:
            # Configurer le token si nécessaire
            if token:
                self._run_git_command(['config', 'remote.origin.url', 
                                     f"https://{token}@github.com/" + self._get_repo_path()])
            
            success, stdout, stderr = self._run_git_command(['fetch', 'origin'])
            
            if success:
                return True
            else:
                print(f"Erreur lors du fetch: {stderr}")
                return False
        
        except Exception as e:
            print(f"Erreur lors du fetch: {e}")
            return False
    
    def get_local_head(self) -> Optional[str]:
        """
        Récupère le hash du HEAD local.
        
        Returns:
            Hash du HEAD local ou None si erreur
        """
        success, stdout, _ = self._run_git_command(['rev-parse', 'HEAD'])
        if success:
            return stdout.strip()
        return None
    
    def get_remote_head(self, branch: str) -> Optional[str]:
        """
        Récupère le hash du HEAD distant.
        
        Args:
            branch: Nom de la branche
            
        Returns:
            Hash du HEAD distant ou None si erreur
        """
        success, stdout, _ = self._run_git_command(['rev-parse', f'origin/{branch}'])
        if success:
            return stdout.strip()
        return None
    
    def has_changes(self, branch: str) -> bool:
        """
        Vérifie s'il y a des changements entre local et distant.
        
        Args:
            branch: Nom de la branche
            
        Returns:
            True s'il y a des changements, False sinon
        """
        local_head = self.get_local_head()
        remote_head = self.get_remote_head(branch)
        
        if local_head is None or remote_head is None:
            return False
        
        return local_head != remote_head
    
    def get_diff_summary(self, branch: str) -> str:
        """
        Récupère un résumé des différences entre local et distant.
        
        Args:
            branch: Nom de la branche
            
        Returns:
            Résumé des différences
        """
        try:
            # Récupérer les logs des changements
            success, stdout, _ = self._run_git_command([
                'log', '--oneline', '--graph', 
                f'HEAD..origin/{branch}'
            ])
            
            if success and stdout.strip():
                return stdout.strip()
            else:
                return "Aucun changement distant trouvé."
        
        except Exception as e:
            return f"Erreur lors de la récupération des différences: {e}"
    
    def get_file_diff(self, file_path: str, branch: str) -> str:
        """
        Récupère les différences pour un fichier spécifique.
        
        Args:
            file_path: Chemin du fichier
            branch: Nom de la branche
            
        Returns:
            Différences formatées
        """
        try:
            success, stdout, _ = self._run_git_command([
                'diff', f'HEAD..origin/{branch}', '--', file_path
            ])
            
            if success:
                return stdout
            else:
                return f"Impossible de récupérer les différences pour {file_path}"
        
        except Exception as e:
            return f"Erreur lors de la récupération des différences: {e}"
    
    def merge_remote_changes(self, branch: str) -> bool:
        """
        Fusionne les changements distants.
        
        Args:
            branch: Nom de la branche
            
        Returns:
            True si la fusion a réussi, False sinon
        """
        try:
            success, stdout, stderr = self._run_git_command([
                'merge', f'origin/{branch}'
            ])
            
            if success:
                print("Fusion des changements distants réussie")
                return True
            else:
                print(f"Erreur lors de la fusion: {stderr}")
                return False
        
        except Exception as e:
            print(f"Erreur lors de la fusion: {e}")
            return False
    
    def has_local_changes(self) -> bool:
        """
        Vérifie s'il y a des changements locaux non commités.
        
        Returns:
            True s'il y a des changements locaux, False sinon
        """
        success, stdout, _ = self._run_git_command(['status', '--porcelain'])
        if success:
            return stdout.strip() != ""
        return False
    
    def add_all(self) -> bool:
        """
        Ajoute tous les fichiers au staging.
        
        Returns:
            True si l'ajout a réussi, False sinon
        """
        success, _, stderr = self._run_git_command(['add', '.'])
        if success:
            return True
        else:
            print(f"Erreur lors de l'ajout des fichiers: {stderr}")
            return False
    
    def commit(self, message: str) -> bool:
        """
        Crée un commit.
        
        Args:
            message: Message du commit
            
        Returns:
            True si le commit a réussi, False sinon
        """
        success, _, stderr = self._run_git_command(['commit', '-m', message])
        if success:
            return True
        else:
            print(f"Erreur lors du commit: {stderr}")
            return False
    
    def push(self, branch: str, token: str = None) -> bool:
        """
        Pousse les changements vers le repository distant.
        
        Args:
            branch: Nom de la branche
            token: Token pour les repositories privés (optionnel)
            
        Returns:
            True si le push a réussi, False sinon
        """
        try:
            # Configurer l'URL avec token si nécessaire
            if token:
                self._run_git_command(['config', 'remote.origin.url', 
                                     f"https://{token}@github.com/" + self._get_repo_path()])
            
            success, stdout, stderr = self._run_git_command(['push', 'origin', branch])
            
            if success:
                print("Push réussi")
                return True
            else:
                print(f"Erreur lors du push: {stderr}")
                return False
        
        except Exception as e:
            print(f"Erreur lors du push: {e}")
            return False
    
    def get_status(self) -> str:
        """
        Récupère le status du repository.
        
        Returns:
            Status du repository
        """
        success, stdout, _ = self._run_git_command(['status'])
        if success:
            return stdout
        return "Impossible de récupérer le status"
    
    def _get_repo_path(self) -> str:
        """
        Extrait le chemin du repository depuis l'URL distante.
        
        Returns:
            Chemin du repository (ex: utilisateur/repo)
        """
        success, stdout, _ = self._run_git_command(['remote', 'get-url', 'origin'])
        if success:
            url = stdout.strip()
            # Extraire le chemin depuis l'URL
            if 'github.com' in url:
                path = url.split('github.com/')[-1]
                # Supprimer le token et le .git
                if '@' in path:
                    path = path.split('@', 1)[1]
                if path.endswith('.git'):
                    path = path[:-4]
                return path
        return ""
