import os

KIT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(KIT_DIR)
PROJECTS_DIR = os.path.join(REPO_ROOT, "projetos")
AGENT_GUIDE_PATH = os.path.join(KIT_DIR, "AGENTE.md")
INSTALLER_PATH = os.path.join(KIT_DIR, "installer", "installer.py")
LINUX_INSTALLER_PATH = os.path.join(KIT_DIR, "installer", "linux_installer.sh")
ENGINES_DIR = os.path.join(KIT_DIR, "engines")
STEAM_COMMON_DIR = r"C:\Program Files (x86)\Steam\steamapps\common"
