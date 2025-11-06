"""
Módulo para detectar pacotes órfãos (sem dependências)
"""
import subprocess
from typing import Dict, List, Any


def get_orphaned_packages() -> List[Dict[str, Any]]:
    """Obtém lista de pacotes órfãos (folhas - leaf packages)"""
    orphans = []
    
    try:
        # Pacotes que não são dependências de nenhum outro
        result = subprocess.run(
            ['dnf', 'repoquery', '--unneeded'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    pkg_name = line.strip().rsplit('.', 1)[0]
                    orphans.append({"name": pkg_name})
    
    except Exception as e:
        print(f"⚠️ Erro ao detectar pacotes órfãos: {e}")
    
    return orphans


def get_autoremovable_packages() -> List[Dict[str, Any]]:
    """Obtém pacotes que podem ser removidos automaticamente"""
    autoremove = []
    
    try:
        result = subprocess.run(
            ['dnf', 'autoremove', '--assumeno'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Parsear saída para encontrar pacotes que seriam removidos
        in_remove_section = False
        for line in result.stdout.split('\n'):
            if 'Removing:' in line or 'Removing' in line:
                in_remove_section = True
                continue
            
            if in_remove_section:
                if line.strip() and not line.startswith('Transaction'):
                    parts = line.split()
                    if len(parts) >= 1 and not parts[0] in ['Installing', 'Upgrading', 'Removing']:
                        pkg_name = parts[0]
                        autoremove.append({"name": pkg_name})
    
    except Exception as e:
        print(f"⚠️ Erro ao verificar autoremove: {e}")
    
    return autoremove


def collect_orphan_metrics(config: Dict[str, Any]) -> Dict[str, Any]:
    """Coleta métricas de pacotes órfãos"""
    print("  🗑️  Detectando pacotes órfãos...")
    
    orphaned = get_orphaned_packages()
    autoremove = get_autoremovable_packages()
    
    return {
        "orphaned_count": len(orphaned),
        "orphaned_packages": orphaned[:50],  # Limitar a 50
        "autoremovable_count": len(autoremove),
        "autoremovable_packages": autoremove[:30]
    }
