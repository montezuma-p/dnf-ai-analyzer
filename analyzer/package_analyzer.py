#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Package Analyzer - Sistema de Análise de Pacotes para Fedora
Coleta informações sobre pacotes instalados e gera relatório em JSON
"""

import json
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

# Adicionar módulos ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules import packages, updates, orphans, cache, dependencies


def load_config(config_path: str = "config.json") -> dict:
    """Carrega arquivo de configuração"""
    script_dir = Path(__file__).parent
    config_file = script_dir / config_path
    
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️  Arquivo de configuração não encontrado: {config_file}")
        print("Usando configuração padrão...")
        return {
            "output_dir": "/home/montezuma/.bin/data/scripts-data/reports/packages/raw"
        }
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao ler arquivo de configuração: {e}")
        sys.exit(1)


def collect_all_metrics(config: dict) -> dict:
    """Coleta todas as métricas de pacotes"""
    print("📊 Coletando informações de pacotes...")
    
    metrics = {}
    
    # Coletar métricas de pacotes
    try:
        metrics["packages"] = packages.collect_package_metrics(config)
    except Exception as e:
        print(f"    ⚠️  Erro: {e}")
        metrics["packages"] = {"error": str(e)}
    
    # Coletar métricas de atualizações
    try:
        metrics["updates"] = updates.collect_update_metrics(config)
    except Exception as e:
        print(f"    ⚠️  Erro: {e}")
        metrics["updates"] = {"error": str(e)}
    
    # Coletar métricas de órfãos
    try:
        metrics["orphans"] = orphans.collect_orphan_metrics(config)
    except Exception as e:
        print(f"    ⚠️  Erro: {e}")
        metrics["orphans"] = {"error": str(e)}
    
    # Coletar métricas de cache
    try:
        metrics["cache"] = cache.collect_cache_metrics(config)
    except Exception as e:
        print(f"    ⚠️  Erro: {e}")
        metrics["cache"] = {"error": str(e)}
    
    # Coletar métricas de dependências
    try:
        metrics["dependencies"] = dependencies.collect_dependency_metrics(config)
    except Exception as e:
        print(f"    ⚠️  Erro: {e}")
        metrics["dependencies"] = {"error": str(e)}
    
    return metrics


def generate_report(config: dict) -> dict:
    """Gera relatório completo"""
    timestamp = datetime.now()
    
    # Coletar métricas
    metrics = collect_all_metrics(config)
    
    # Gerar alertas/problemas
    issues = []
    
    # Verificar atualizações pendentes
    if metrics.get("updates", {}).get("total_updates", 0) > 0:
        issues.append({
            "type": "updates",
            "severity": "info",
            "message": f"{metrics['updates']['total_updates']} atualizações disponíveis"
        })
    
    # Verificar atualizações de segurança
    if metrics.get("updates", {}).get("security_updates", 0) > 0:
        issues.append({
            "type": "security",
            "severity": "warning",
            "message": f"{metrics['updates']['security_updates']} atualizações de segurança disponíveis"
        })
    
    # Verificar órfãos
    if metrics.get("orphans", {}).get("orphaned_count", 0) > 10:
        issues.append({
            "type": "orphans",
            "severity": "info",
            "message": f"{metrics['orphans']['orphaned_count']} pacotes órfãos detectados"
        })
    
    # Verificar cache grande
    if metrics.get("cache", {}).get("can_clean", False):
        issues.append({
            "type": "cache",
            "severity": "info",
            "message": f"Cache do DNF ocupando {metrics['cache']['total_size_mb']}MB"
        })
    
    # Verificar dependências quebradas
    if metrics.get("dependencies", {}).get("has_issues", False):
        issues.append({
            "type": "dependencies",
            "severity": "warning",
            "message": "Problemas de dependências detectados"
        })
    
    # Montar relatório
    report = {
        "timestamp": timestamp.isoformat(),
        "timestamp_unix": int(timestamp.timestamp()),
        "metrics": metrics,
        "issues": issues,
        "summary": {
            "total_packages": metrics.get("packages", {}).get("summary", {}).get("total_packages", 0),
            "total_updates": metrics.get("updates", {}).get("total_updates", 0),
            "total_issues": len(issues),
            "cache_size_mb": metrics.get("cache", {}).get("total_size_mb", 0)
        }
    }
    
    return report


def save_report(report: dict, config: dict) -> str:
    """Salva relatório em arquivo JSON"""
    output_dir = Path(config.get("output_dir", "/home/montezuma/.bin/data/scripts-data/reports/raw"))
    
    # Criar diretório se não existir
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Nome do arquivo com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"packages_{timestamp}.json"
    filepath = output_dir / filename
    
    # Salvar JSON
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return str(filepath)


def print_summary(report: dict):
    """Imprime resumo do relatório"""
    print("\n" + "="*60)
    print("📦 RESUMO DA ANÁLISE DE PACOTES")
    print("="*60)
    
    summary = report.get("summary", {})
    
    print(f"\n📊 Estatísticas:")
    print(f"   Total de pacotes: {summary.get('total_packages', 0)}")
    print(f"   Atualizações disponíveis: {summary.get('total_updates', 0)}")
    print(f"   Cache do DNF: {summary.get('cache_size_mb', 0):.1f} MB")
    
    # Mostrar problemas
    issues = report.get("issues", [])
    if issues:
        print(f"\n⚠️  Problemas detectados ({len(issues)}):")
        for issue in issues[:5]:
            severity_icon = "🔴" if issue['severity'] == 'warning' else "🔵"
            print(f"   {severity_icon} {issue['message']}")
    else:
        print(f"\n✅ Nenhum problema detectado!")
    
    print("\n" + "="*60)


def main():
    """Função principal"""
    # Parser de argumentos
    parser = argparse.ArgumentParser(
        description='Package Analyzer - Análise de pacotes do sistema'
    )
    parser.add_argument(
        '--session',
        type=str,
        help='Session ID para integração com orchestrator (habilita modo sessão)',
        default=None
    )
    
    args = parser.parse_args()
    
    print("📦 Package Analyzer - Iniciando análise...")
    if args.session:
        print(f"   🔗 Modo sessão: {args.session}")
    print()
    
    # Carregar configuração
    config = load_config()
    
    try:
        # Gerar relatório
        report = generate_report(config)
        
        # Adicionar session_id ao relatório se fornecido
        if args.session:
            report['session_id'] = args.session
        
        # Salvar relatório
        print("\n💾 Salvando relatório...")
        filepath = save_report(report, config)
        print(f"✅ Relatório salvo em: {filepath}")
        
        # Se modo sessão, integrar com database
        if args.session:
            try:
                # Importa database_manager (apenas em modo sessão)
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'orchestrador'))
                from database_manager.db_manager import DatabaseManager
                
                db = DatabaseManager()
                db.insert_package_metrics(args.session, report)
                print(f"   ✅ Métricas gravadas no histórico (sessão: {args.session})")
            except Exception as e:
                print(f"   ⚠️  Erro ao gravar no banco: {e}")
        
        # Imprimir resumo
        print_summary(report)
        
        sys.exit(0)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Análise interrompida pelo usuário")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
