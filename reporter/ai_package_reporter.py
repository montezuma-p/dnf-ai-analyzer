#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI Package Reporter - Gerador de Relatórios de Pacotes usando Gemini
Analisa JSONs do package_analyzer e gera relatórios HTML humanizados
"""

import os
import sys
import json
import glob
from pathlib import Path
from datetime import datetime
from google import genai
from google.genai import types

# Verificar API key
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("❌ ERRO: Variável GEMINI_API_KEY não encontrada!")
    print("Configure com: export GEMINI_API_KEY='sua_chave_aqui'")
    sys.exit(1)

# Configurar cliente
client = genai.Client(api_key=api_key)
model = "gemini-2.5-flash"

# Caminhos
REPORTS_DIR = Path("/home/montezuma/.bin/data/scripts-data/reports/packages/raw")
OUTPUT_DIR = Path("/home/montezuma/.bin/data/scripts-data/reports/packages/html")


def obter_ultimo_json():
    """Obtém o arquivo JSON mais recente"""
    json_files = glob.glob(str(REPORTS_DIR / "packages_*.json"))
    
    if not json_files:
        print(f"❌ Nenhum relatório encontrado em {REPORTS_DIR}")
        return None
    
    latest_file = max(json_files, key=os.path.getctime)
    return Path(latest_file)


def ler_json(filepath):
    """Lê arquivo JSON"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Erro ao ler {filepath}: {e}")
        return None


def criar_prompt_analise(dados_json):
    """Cria prompt para IA analisar pacotes"""
    
    prompt = f"""Você é um especialista em gerenciamento de sistemas Linux Fedora com foco em pacotes DNF/RPM.

Analise este relatório de pacotes e crie uma análise INTERPRETATIVA e HUMANIZADA em formato JSON.

DADOS DO SISTEMA:
```json
{json.dumps(dados_json, indent=2, ensure_ascii=False)}
```

Retorne um JSON estruturado para preencher um template HTML.

ESTRUTURA DO JSON:

{{
    "resumo_executivo": "2-3 parágrafos explicando o estado geral dos pacotes. Quantos pacotes? Sistema limpo ou bagunçado? Atualizações pendentes? Use linguagem clara.",
    
    "metricas_cards": [
        {{
            "icon": "emoji",
            "label": "Nome da métrica",
            "value": "Valor",
            "subtext": "Texto complementar"
        }}
    ],
    
    "analise_pacotes": "Análise INTERPRETADA dos pacotes instalados. Explique quantidade, tamanho total, pacotes grandes. É normal? É muito? Dê contexto.",
    
    "analise_updates": "Análise de atualizações disponíveis. Quantas? Atualizações de segurança são urgentes? O que fazer?",
    
    "analise_orphans": "Análise de pacotes órfãos. O que são? Vale a pena remover? Como fazer?",
    
    "analise_cache": "Análise do cache do DNF. Tamanho ok? Precisa limpar? Quando limpar cache?",
    
    "analise_dependencies": "Análise de dependências. Há problemas? Pacotes duplicados? Como resolver?",
    
    "recomendacoes": [
        {{
            "prioridade": "alta, media ou baixa",
            "titulo": "Título da recomendação",
            "descricao": "Explicação",
            "comandos": ["comando1"] ou null
        }}
    ],
    
    "conclusao": "1-2 parágrafos resumindo o estado do sistema de pacotes e próximos passos"
}}

REGRAS:

✅ INTERPRETE - não apenas liste números
✅ EXPLIQUE - contextualize cada métrica
✅ HUMANIZE - linguagem acessível
✅ SEJA PRÁTICO - comandos reais DNF
✅ USE ANALOGIAS quando útil

EXEMPLOS:

❌ ERRADO: "2450 pacotes instalados"
✅ CORRETO: "Você tem 2.450 pacotes instalados, ocupando 15GB. Isso é normal para um Fedora Workstation com desenvolvimento e desktop completo."

❌ ERRADO: "23 updates disponíveis"
✅ CORRETO: "Existem 23 atualizações disponíveis, incluindo 5 de segurança. Recomendo atualizar logo com 'sudo dnf update'."

❌ ERRADO: "150 pacotes órfãos"
✅ CORRETO: "Detectei 150 pacotes órfãos (instalados como dependências mas não mais necessários). Você pode recuperar ~500MB removendo-os com 'sudo dnf autoremove'."

Retorne APENAS o JSON válido, sem markdown."""

    return prompt


def chamar_gemini(prompt):
    """Chama API Gemini"""
    try:
        print("⏳ Analisando com Gemini...")
        
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                top_p=0.95,
                max_output_tokens=8192
            )
        )
        
        resultado = response.text.strip()
        
        # Limpar markdown
        json_text = resultado
        if "```json" in resultado:
            json_start = resultado.find("```json") + 7
            json_end = resultado.find("```", json_start)
            if json_end > json_start:
                json_text = resultado[json_start:json_end].strip()
        elif "```" in resultado:
            json_start = resultado.find("```") + 3
            json_end = resultado.rfind("```")
            if json_end > json_start:
                json_text = resultado[json_start:json_end].strip()
        
        # Extrair JSON
        first_brace = json_text.find('{')
        last_brace = json_text.rfind('}')
        if first_brace != -1 and last_brace != -1:
            json_text = json_text[first_brace:last_brace+1]
        
        return json.loads(json_text)
        
    except json.JSONDecodeError as e:
        print(f"⚠️ Erro ao parsear JSON: {e}")
        print("Resposta:", resultado[:500])
        return None
    except Exception as e:
        print(f"❌ Erro ao chamar Gemini: {e}")
        return None


def gerar_metrics_cards(metricas):
    """Gera HTML dos cards de métricas"""
    cards_html = ""
    for m in metricas:
        cards_html += f"""
                    <div class="metric-card">
                        <div class="icon">{m.get('icon', '📊')}</div>
                        <div class="label">{m.get('label', 'Métrica')}</div>
                        <div class="value">{m.get('value', 'N/A')}</div>
                        <div class="subtext">{m.get('subtext', '')}</div>
                    </div>
"""
    return cards_html


def gerar_recomendacoes(recomendacoes):
    """Gera HTML das recomendações"""
    html = '<ul class="recommendation-list">\n'
    
    for rec in recomendacoes:
        prioridade = rec.get('prioridade', 'media')
        priority_class = f"priority-{prioridade}"
        
        html += f'<li class="{priority_class}">\n'
        html += f'<strong>{rec.get("titulo", "Recomendação")}</strong><br>\n'
        html += f'{rec.get("descricao", "")}<br>\n'
        
        if rec.get('comandos'):
            html += '<pre><code>'
            for cmd in rec['comandos']:
                html += f'{cmd}\n'
            html += '</code></pre>\n'
        
        html += '</li>\n'
    
    html += '</ul>'
    return html


def preencher_template(analise_json, dados_originais):
    """Preenche template HTML"""
    template_path = Path(__file__).parent / "template.html"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
    except Exception as e:
        print(f"❌ Erro ao ler template: {e}")
        return None
    
    # Substituir placeholders
    template = template.replace('{{TIMESTAMP}}', dados_originais.get('timestamp', 'N/A'))
    
    # Métricas
    metrics_html = gerar_metrics_cards(analise_json.get('metricas_cards', []))
    template = template.replace('{{METRICS_CARDS}}', metrics_html)
    
    # Análises
    template = template.replace('{{RESUMO_EXECUTIVO}}', analise_json.get('resumo_executivo', '<p>N/A</p>'))
    template = template.replace('{{ANALISE_PACOTES}}', analise_json.get('analise_pacotes', '<p>N/A</p>'))
    template = template.replace('{{ANALISE_UPDATES}}', analise_json.get('analise_updates', '<p>N/A</p>'))
    template = template.replace('{{ANALISE_ORPHANS}}', analise_json.get('analise_orphans', '<p>N/A</p>'))
    template = template.replace('{{ANALISE_CACHE}}', analise_json.get('analise_cache', '<p>N/A</p>'))
    template = template.replace('{{ANALISE_DEPENDENCIES}}', analise_json.get('analise_dependencies', '<p>N/A</p>'))
    
    # Recomendações
    recomendacoes_html = gerar_recomendacoes(analise_json.get('recomendacoes', []))
    template = template.replace('{{RECOMENDACOES}}', recomendacoes_html)
    
    # Conclusão
    template = template.replace('{{CONCLUSAO}}', analise_json.get('conclusao', '<p>N/A</p>'))
    
    return template


def salvar_html(html_content, json_filepath):
    """Salva HTML"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    json_filename = json_filepath.stem
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_filename = f"{json_filename}_report_{timestamp}.html"
    html_filepath = OUTPUT_DIR / html_filename
    
    try:
        with open(html_filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        return html_filepath
    except Exception as e:
        print(f"❌ Erro ao salvar HTML: {e}")
        return None


def abrir_no_navegador(filepath):
    """Abre HTML no navegador"""
    try:
        os.system(f"xdg-open '{filepath}'")
        return True
    except:
        return False


def main():
    """Função principal"""
    print("📦 AI Package Reporter - Análise Inteligente de Pacotes")
    print("🤖 Powered by Google Gemini")
    print()
    
    try:
        # Obter JSON
        print("📂 Procurando relatórios...")
        json_file = obter_ultimo_json()
        
        if not json_file:
            print("💡 Execute package_analyzer.py primeiro!")
            sys.exit(1)
        
        print(f"✅ Encontrado: {json_file.name}")
        
        # Ler JSON
        print("📖 Lendo dados...")
        dados = ler_json(json_file)
        
        if not dados:
            sys.exit(1)
        
        # Info básica
        summary = dados.get('summary', {})
        print(f"\n📊 Resumo:")
        print(f"   Pacotes: {summary.get('total_packages', 0)}")
        print(f"   Atualizações: {summary.get('total_updates', 0)}")
        print(f"   Problemas: {summary.get('total_issues', 0)}")
        
        # Criar prompt
        print("\n🧠 Preparando análise...")
        prompt = criar_prompt_analise(dados)
        
        # Chamar IA
        analise_json = chamar_gemini(prompt)
        
        if not analise_json:
            print("❌ Falha na análise")
            sys.exit(1)
        
        print("✅ Análise concluída!")
        
        # Preencher template
        print("🎨 Gerando HTML...")
        html_content = preencher_template(analise_json, dados)
        
        if not html_content:
            sys.exit(1)
        
        # Salvar
        print("💾 Salvando...")
        html_file = salvar_html(html_content, json_file)
        
        if not html_file:
            sys.exit(1)
        
        print(f"✅ Salvo em: {html_file}")
        
        # Abrir
        print("\n" + "="*60)
        print("✨ RELATÓRIO GERADO!")
        print("="*60)
        
        while True:
            abrir = input("\n🌐 Abrir no navegador? (s/n): ").strip().lower()
            if abrir in ['s', 'sim', 'y', 'yes']:
                if abrir_no_navegador(html_file):
                    print("✅ Aberto!")
                else:
                    print(f"💡 Abra: {html_file}")
                break
            elif abrir in ['n', 'nao', 'não', 'no']:
                print(f"💡 Arquivo: {html_file}")
                break
        
        print("\n👋 Concluído!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrompido!")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
