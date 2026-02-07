"""
Gestion du démarrage Windows pour GitHub Viewer.
"""

import os
import sys
from pathlib import Path
import ctypes
from ctypes import wintypes


class StartupManager:
    """Gestionnaire du démarrage Windows."""
    
    def __init__(self):
        """Initialise le gestionnaire de démarrage."""
        self.app_name = "GitHub Viewer"
        self.startup_folder = self._get_startup_folder()
    
    def _get_startup_folder(self) -> Path:
        """
        Récupère le chemin du dossier de démarrage Windows.
        
        Returns:
            Chemin du dossier de démarrage
        """
        try:
            # Utiliser l'API Windows pour obtenir le dossier de démarrage
            CSIDL_STARTUP = 7
            SHGFP_TYPE_CURRENT = 0
            
            buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
            shell32 = ctypes.windll.shell32
            
            result = shell32.SHGetFolderPathW(
                0, CSIDL_STARTUP, 0, SHGFP_TYPE_CURRENT, buf
            )
            
            if result == 0:  # S_OK
                return Path(buf.value)
            else:
                # Fallback vers le chemin par défaut
                return Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        
        except Exception:
            # Fallback vers le chemin par défaut
            return Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    
    def get_executable_path(self) -> Path:
        """
        Récupère le chemin de l'exécutable GitHub Viewer.
        
        Returns:
            Chemin de l'exécutable
        """
        if getattr(sys, 'frozen', False):
            # Mode compilé avec Nuitka
            return Path(sys.executable)
        else:
            # Mode développement
            return Path(__file__).parent / "main.py"
    
    def add_to_startup(self) -> bool:
        """
        Ajoute GitHub Viewer au démarrage Windows.
        
        Returns:
            True si l'ajout a réussi, False sinon
        """
        try:
            # Vérifier si déjà présent
            if self.is_in_startup():
                print("GitHub Viewer est déjà dans le démarrage Windows.")
                return True
            
            # Créer le raccourci
            exe_path = self.get_executable_path()
            shortcut_path = self.startup_folder / f"{self.app_name}.lnk"
            
            if self._create_shortcut(exe_path, shortcut_path):
                print(f"Raccourci créé: {shortcut_path}")
                return True
            else:
                print("Erreur lors de la création du raccourci.")
                return False
        
        except Exception as e:
            print(f"Erreur lors de l'ajout au démarrage: {e}")
            return False
    
    def remove_from_startup(self) -> bool:
        """
        Retire GitHub Viewer du démarrage Windows.
        
        Returns:
            True si le retrait a réussi, False sinon
        """
        try:
            shortcut_path = self.startup_folder / f"{self.app_name}.lnk"
            
            if shortcut_path.exists():
                shortcut_path.unlink()
                print("GitHub Viewer retiré du démarrage Windows.")
                return True
            else:
                print("GitHub Viewer n'est pas dans le démarrage Windows.")
                return True
        
        except Exception as e:
            print(f"Erreur lors du retrait du démarrage: {e}")
            return False
    
    def is_in_startup(self) -> bool:
        """
        Vérifie si GitHub Viewer est dans le démarrage Windows.
        
        Returns:
            True si présent, False sinon
        """
        shortcut_path = self.startup_folder / f"{self.app_name}.lnk"
        return shortcut_path.exists()
    
    def _create_shortcut(self, target: Path, shortcut: Path) -> bool:
        """
        Crée un raccourci Windows.
        
        Args:
            target: Cible du raccourci
            shortcut: Chemin du raccourci à créer
            
        Returns:
            True si la création a réussi, False sinon
        """
        try:
            import win32com.client
            
            # Créer l'objet Shell
            shell = win32com.client.Dispatch("WScript.Shell")
            
            # Créer le raccourci
            shortcut_obj = shell.CreateShortCut(str(shortcut))
            shortcut_obj.Targetpath = str(target)
            shortcut_obj.WorkingDirectory = str(target.parent)
            shortcut_obj.Description = f"Lancer {self.app_name}"
            shortcut_obj.Save()
            
            return True
        
        except ImportError:
            # Si win32com n'est pas disponible, utiliser une méthode alternative
            return self._create_shortcut_alternative(target, shortcut)
        
        except Exception as e:
            print(f"Erreur lors de la création du raccourci: {e}")
            return False
    
    def _create_shortcut_alternative(self, target: Path, shortcut: Path) -> bool:
        """
        Méthode alternative pour créer un raccourci sans win32com.
        
        Args:
            target: Cible du raccourci
            shortcut: Chemin du raccourci à créer
            
        Returns:
            True si la création a réussi, False sinon
        """
        try:
            # Créer un fichier .bat qui lance l'application
            bat_path = shortcut.with_suffix('.bat')
            
            with open(bat_path, 'w', encoding='utf-8') as f:
                if target.suffix == '.py':
                    # Fichier Python
                    f.write(f'@echo off\n')
                    f.write(f'cd /d "{target.parent}"\n')
                    f.write(f'python "{target}"\n')
                else:
                    # Exécutable
                    f.write(f'@echo off\n')
                    f(f'"{target}"\n')
            
            # Masquer le fichier .bat
            import ctypes
            FILE_ATTRIBUTE_HIDDEN = 0x02
            ctypes.windll.kernel32.SetFileAttributesW(str(bat_path), FILE_ATTRIBUTE_HIDDEN)
            
            print(f"Fichier batch créé: {bat_path}")
            return True
        
        except Exception as e:
            print(f"Erreur lors de la création du fichier batch: {e}")
            return False
    
    def get_startup_status(self) -> str:
        """
        Récupère le statut du démarrage.
        
        Returns:
            Message de statut
        """
        if self.is_in_startup():
            return f"✅ {self.app_name} est dans le démarrage Windows"
        else:
            return f"❌ {self.app_name} n'est pas dans le démarrage Windows"


def main():
    """Point d'entrée pour la gestion du démarrage."""
    startup_manager = StartupManager()
    
    print("Gestion du démarrage Windows pour GitHub Viewer")
    print("=" * 50)
    print(startup_manager.get_startup_status())
    print()
    
    print("Options:")
    print("1. Ajouter au démarrage")
    print("2. Retirer du démarrage")
    print("3. Quitter")
    
    while True:
        choice = input("\nVotre choix (1-3): ").strip()
        
        if choice == "1":
            if startup_manager.add_to_startup():
                print(startup_manager.get_startup_status())
            break
        elif choice == "2":
            if startup_manager.remove_from_startup():
                print(startup_manager.get_startup_status())
            break
        elif choice == "3":
            break
        else:
            print("Choix invalide. Réessayez.")
    
    input("\nAppuyez sur Entrée pour quitter...")


if __name__ == "__main__":
    main()
