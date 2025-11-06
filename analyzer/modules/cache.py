"""
Módulo para análise de cache do DNF
"""
import subprocess
import os
from pathlib import Path
from typing import Dict, Any


def get_cache_size() -> Dict[str, Any]:
    """Obtém tamanho do cache do DNF"""
    cache_info = {
        "total_size_mb": 0,
        "packages_cache": 0,
        "metadata_cache": 0,
        "cache_dir": "/var/cache/dnf"
    }
    
    try:
        cache_dir = Path("/var/cache/dnf")
        
        if cache_dir.exists():
            # Calcular tamanho total
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(cache_dir):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except:
                        continue
            
            cache_info["total_size_mb"] = round(total_size / (1024 * 1024), 2)
            cache_info["total_size_gb"] = round(total_size / (1024 * 1024 * 1024), 2)
    
    except Exception as e:
        print(f"⚠️ Erro ao analisar cache: {e}")
    
    return cache_info


def get_cache_info_dnf() -> Dict[str, Any]:
    """Obtém informações de cache via DNF"""
    info = {}
    
    try:
        result = subprocess.run(
            ['du', '-sh', '/var/cache/dnf'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            size_str = result.stdout.split()[0]
            info["cache_size_human"] = size_str
    
    except Exception as e:
        pass
    
    return info


def collect_cache_metrics(config: Dict[str, Any]) -> Dict[str, Any]:
    """Coleta métricas de cache"""
    print("  💾 Analisando cache do DNF...")
    
    cache_size = get_cache_size()
    cache_info = get_cache_info_dnf()
    
    return {
        **cache_size,
        **cache_info,
        "can_clean": cache_size["total_size_mb"] > 100  # Se > 100MB, sugerir limpeza
    }
