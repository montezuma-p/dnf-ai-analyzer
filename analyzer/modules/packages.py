"""
Módulo para listar e analisar pacotes instalados
"""
import subprocess
import json
from datetime import datetime
from typing import Dict, List, Any


def get_all_packages() -> List[Dict[str, Any]]:
    """Obtém lista completa de pacotes instalados via DNF"""
    packages = []
    
    try:
        # Listar todos os pacotes instalados com informações detalhadas
        result = subprocess.run(
            ['dnf', 'list', 'installed'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            
            # Pular cabeçalho
            for line in lines[1:]:
                if not line.strip() or line.startswith('Installed'):
                    continue
                
                parts = line.split()
                if len(parts) >= 3:
                    pkg_name = parts[0].rsplit('.', 1)[0]  # Remover arquitetura
                    version = parts[1]
                    repo = parts[2] if len(parts) > 2 else 'unknown'
                    
                    packages.append({
                        "name": pkg_name,
                        "version": version,
                        "repository": repo
                    })
    except Exception as e:
        print(f"⚠️ Erro ao listar pacotes: {e}")
    
    return packages


def get_package_details(package_name: str) -> Dict[str, Any]:
    """Obtém detalhes específicos de um pacote"""
    details = {
        "name": package_name,
        "size_bytes": 0,
        "install_date": None,
        "install_reason": "unknown",
        "description": "",
        "url": ""
    }
    
    try:
        # Info do pacote
        result = subprocess.run(
            ['dnf', 'info', package_name],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == 'Size':
                        # Converter para bytes
                        size_str = value.lower()
                        if 'k' in size_str:
                            details["size_bytes"] = int(float(size_str.replace('k', '').strip()) * 1024)
                        elif 'm' in size_str:
                            details["size_bytes"] = int(float(size_str.replace('m', '').strip()) * 1024 * 1024)
                        elif 'g' in size_str:
                            details["size_bytes"] = int(float(size_str.replace('g', '').strip()) * 1024 * 1024 * 1024)
                    
                    elif key == 'Summary':
                        details["description"] = value
                    
                    elif key == 'URL':
                        details["url"] = value
        
        # Data de instalação via RPM
        rpm_result = subprocess.run(
            ['rpm', '-q', '--queryformat', '%{INSTALLTIME}', package_name],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if rpm_result.returncode == 0 and rpm_result.stdout.strip():
            try:
                timestamp = int(rpm_result.stdout.strip())
                details["install_date"] = datetime.fromtimestamp(timestamp).isoformat()
            except:
                pass
        
        # Razão da instalação (user ou dependency)
        reason_result = subprocess.run(
            ['dnf', 'repoquery', '--userinstalled', package_name],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if reason_result.returncode == 0 and reason_result.stdout.strip():
            details["install_reason"] = "user"
        else:
            details["install_reason"] = "dependency"
        
    except Exception as e:
        pass
    
    return details


def get_packages_by_size() -> List[Dict[str, Any]]:
    """Obtém pacotes ordenados por tamanho"""
    packages = []
    
    try:
        result = subprocess.run(
            ['rpm', '-qa', '--queryformat', '%{NAME}|%{SIZE}|%{VERSION}\n'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 3:
                        try:
                            packages.append({
                                "name": parts[0],
                                "size_bytes": int(parts[1]),
                                "size_mb": round(int(parts[1]) / (1024 * 1024), 2),
                                "version": parts[2]
                            })
                        except:
                            continue
            
            # Ordenar por tamanho (maior primeiro)
            packages.sort(key=lambda x: x['size_bytes'], reverse=True)
    
    except Exception as e:
        print(f"⚠️ Erro ao listar pacotes por tamanho: {e}")
    
    return packages


def get_package_count() -> Dict[str, int]:
    """Obtém contagem de pacotes"""
    count = {
        "total": 0,
        "user_installed": 0,
        "dependencies": 0
    }
    
    try:
        # Total de pacotes
        total_result = subprocess.run(
            ['rpm', '-qa'],
            capture_output=True,
            text=True,
            timeout=20
        )
        
        if total_result.returncode == 0:
            count["total"] = len(total_result.stdout.strip().split('\n'))
        
        # Pacotes instalados pelo usuário
        user_result = subprocess.run(
            ['dnf', 'repoquery', '--userinstalled'],
            capture_output=True,
            text=True,
            timeout=20
        )
        
        if user_result.returncode == 0:
            count["user_installed"] = len([l for l in user_result.stdout.strip().split('\n') if l.strip()])
        
        count["dependencies"] = count["total"] - count["user_installed"]
    
    except Exception as e:
        print(f"⚠️ Erro ao contar pacotes: {e}")
    
    return count


def collect_package_metrics(config: Dict[str, Any]) -> Dict[str, Any]:
    """Coleta todas as métricas de pacotes"""
    print("  📦 Coletando lista de pacotes...")
    
    # Contagem
    counts = get_package_count()
    
    # Top pacotes por tamanho (limitar a 50)
    packages_by_size = get_packages_by_size()[:50]
    
    # Tamanho total
    total_size_bytes = sum(p['size_bytes'] for p in packages_by_size)
    
    return {
        "summary": {
            "total_packages": counts["total"],
            "user_installed": counts["user_installed"],
            "dependencies": counts["dependencies"],
            "total_size_gb": round(total_size_bytes / (1024**3), 2)
        },
        "largest_packages": packages_by_size[:20],  # Top 20
        "all_packages_sample": packages_by_size[:100]  # Amostra de 100
    }
