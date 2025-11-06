"""
Módulo para verificar atualizações disponíveis
"""
import subprocess
from typing import Dict, List, Any


def get_updates_available() -> List[Dict[str, Any]]:
    """Obtém lista de atualizações disponíveis"""
    updates = []
    
    try:
        result = subprocess.run(
            ['dnf', 'check-update', '--quiet'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # check-update retorna código 100 quando há atualizações
        if result.returncode in [0, 100]:
            lines = result.stdout.strip().split('\n')
            
            for line in lines:
                if not line.strip() or line.startswith('Last') or line.startswith('Security'):
                    continue
                
                parts = line.split()
                if len(parts) >= 3:
                    pkg_name = parts[0].rsplit('.', 1)[0]
                    new_version = parts[1]
                    repo = parts[2]
                    
                    updates.append({
                        "package": pkg_name,
                        "new_version": new_version,
                        "repository": repo
                    })
    
    except Exception as e:
        print(f"⚠️ Erro ao verificar atualizações: {e}")
    
    return updates


def get_security_updates() -> List[Dict[str, Any]]:
    """Obtém atualizações de segurança disponíveis"""
    security_updates = []
    
    try:
        result = subprocess.run(
            ['dnf', 'updateinfo', 'list', 'security', '--available'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if 'FEDORA' in line or 'security' in line.lower():
                    parts = line.split()
                    if len(parts) >= 2:
                        security_updates.append({
                            "advisory": parts[0],
                            "type": "security",
                            "severity": parts[1] if len(parts) > 1 else "unknown"
                        })
    
    except Exception as e:
        print(f"⚠️ Erro ao verificar updates de segurança: {e}")
    
    return security_updates


def get_update_summary() -> Dict[str, Any]:
    """Obtém resumo de atualizações"""
    updates = get_updates_available()
    security = get_security_updates()
    
    return {
        "total_updates": len(updates),
        "security_updates": len(security),
        "updates_list": updates[:30],  # Limitar a 30 para JSON
        "security_list": security[:10]
    }


def collect_update_metrics(config: Dict[str, Any]) -> Dict[str, Any]:
    """Coleta todas as métricas de atualizações"""
    print("  🔄 Verificando atualizações disponíveis...")
    return get_update_summary()
