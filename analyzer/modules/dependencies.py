"""
Módulo para verificar dependências e problemas
"""
import subprocess
from typing import Dict, List, Any


def check_broken_dependencies() -> List[Dict[str, Any]]:
    """Verifica dependências quebradas"""
    broken = []
    
    try:
        result = subprocess.run(
            ['dnf', 'check'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Se há problemas, o dnf check retorna != 0
        if result.returncode != 0:
            for line in result.stdout.split('\n'):
                if 'missing' in line.lower() or 'broken' in line.lower():
                    broken.append({"issue": line.strip()})
        
        # Verificar também via RPM
        rpm_result = subprocess.run(
            ['rpm', '-Va', '--nofiles', '--nodigest'],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if rpm_result.stdout.strip():
            for line in rpm_result.stdout.strip().split('\n')[:10]:  # Limitar a 10
                if line.strip():
                    broken.append({"rpm_issue": line.strip()})
    
    except Exception as e:
        print(f"⚠️ Erro ao verificar dependências: {e}")
    
    return broken


def get_duplicate_packages() -> List[Dict[str, Any]]:
    """Detecta pacotes duplicados (múltiplas versões)"""
    duplicates = []
    
    try:
        result = subprocess.run(
            ['dnf', 'repoquery', '--duplicates'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    duplicates.append({"package": line.strip()})
    
    except Exception as e:
        print(f"⚠️ Erro ao detectar duplicados: {e}")
    
    return duplicates


def get_dependency_count(package: str) -> int:
    """Conta dependências de um pacote"""
    count = 0
    
    try:
        result = subprocess.run(
            ['dnf', 'repoquery', '--requires', package],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            count = len([l for l in result.stdout.strip().split('\n') if l.strip()])
    
    except:
        pass
    
    return count


def collect_dependency_metrics(config: Dict[str, Any]) -> Dict[str, Any]:
    """Coleta métricas de dependências"""
    print("  🔗 Verificando dependências...")
    
    broken = check_broken_dependencies()
    duplicates = get_duplicate_packages()
    
    return {
        "broken_dependencies": len(broken),
        "broken_list": broken[:20],
        "duplicate_packages": len(duplicates),
        "duplicate_list": duplicates[:20],
        "has_issues": len(broken) > 0 or len(duplicates) > 0
    }
