# 📦 Package Analyzer & AI Reporter

> Sistema inteligente de análise de pacotes para Fedora Linux com relatórios humanizados via IA

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Fedora](https://img.shields.io/badge/Fedora-Linux-51A2DA?style=for-the-badge&logo=fedora&logoColor=white)](https://fedoraproject.org/)
[![Gemini](https://img.shields.io/badge/Google-Gemini_AI-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

## 🎯 O Problema

Gerenciar pacotes no Linux é chato. Você tem:
- **Centenas** (ou milhares) de pacotes instalados
- Atualizações pendentes que você esquece
- Pacotes órfãos ocupando espaço à toa
- Cache do DNF crescendo sem parar
- Dependências quebradas que você nem sabe que existem

E a saída do `dnf` é tão emocionante quanto ler um manual de geladeira.

## 💡 A Solução

Este projeto transforma dados brutos de pacotes em **relatórios HTML bonitos e inteligentes**, com análises em linguagem natural feitas pela IA do Google Gemini.

### O que ele faz:

1. 🔍 **Analisa** seu sistema Fedora coletando métricas detalhadas
2. 📊 **Processa** informações de pacotes, updates, órfãos, cache e dependências  
3. 🤖 **Interpreta** os dados usando IA para gerar insights humanizados
4. 🎨 **Gera** relatórios HTML lindos com recomendações práticas

### Por que você deveria usar:

- ✅ **Visual**: Chega de logs feios - relatórios bonitos e fáceis de ler
- ✅ **Inteligente**: IA explica o que cada métrica significa e o que fazer
- ✅ **Prático**: Comandos prontos para copiar e executar
- ✅ **Automático**: Agende e receba relatórios periodicamente
- ✅ **Modular**: Código limpo e extensível

---

## 🚀 Instalação

### 1. Requisitos

- **Sistema**: Fedora Linux (ou qualquer distro com DNF)
- **Python**: 3.8 ou superior
- **DNF**: Gerenciador de pacotes instalado
- **API Key**: Google Gemini API (gratuita)

### 2. Clone o repositório

```bash
git clone https://github.com/montezuma-p/packages.git
cd packages
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

Ou manualmente:
```bash
pip install psutil google-genai
```

### 4. Configure a API do Gemini

Obtenha sua chave gratuita em: [https://ai.google.dev/](https://ai.google.dev/)

```bash
export GEMINI_API_KEY='sua_chave_aqui'
```

Para tornar permanente, adicione ao `~/.bashrc` ou `~/.zshrc`:
```bash
echo 'export GEMINI_API_KEY="sua_chave_aqui"' >> ~/.bashrc
source ~/.bashrc
```

### 5. Configure os caminhos (opcional)

Edite `analyzer/config.json` para customizar o diretório de saída:

```json
{
  "output_dir": "/seu/caminho/personalizado",
  "analysis": {
    "include_orphans": true,
    "include_updates": true,
    "include_cache": true,
    "include_dependencies": true,
    "max_packages_sample": 100
  }
}
```

---

## 📖 Uso

### Modo Básico

#### 1. Coletar métricas do sistema

```bash
python analyzer/package_analyzer.py
```

Isso vai:
- ✅ Analisar todos os pacotes instalados
- ✅ Verificar atualizações disponíveis
- ✅ Detectar pacotes órfãos
- ✅ Medir cache do DNF
- ✅ Verificar dependências
- ✅ Salvar JSON em `output_dir`

#### 2. Gerar relatório HTML com IA

```bash
python reporter/ai_package_reporter.py
```

Isso vai:
- ✅ Pegar o último JSON gerado
- ✅ Enviar para IA Gemini analisar
- ✅ Gerar HTML com insights humanizados
- ✅ Abrir automaticamente no navegador

### Modo Avançado

#### Análise completa com relatório

```bash
# Analisa e gera relatório de uma vez
python analyzer/package_analyzer.py && python reporter/ai_package_reporter.py
```

#### Automatizar com cron

Para receber relatórios diários:

```bash
crontab -e
```

Adicione:
```cron
# Análise diária às 8h
0 8 * * * cd /caminho/para/packages && python analyzer/package_analyzer.py && python reporter/ai_package_reporter.py
```

#### Flags disponíveis

```bash
# Ver ajuda
python analyzer/package_analyzer.py --help

# Usar configuração customizada
python analyzer/package_analyzer.py --config /caminho/config.json

# Modo verboso
python analyzer/package_analyzer.py --verbose
```

---

## 🏗️ Estrutura do Projeto

```
packages/
├── analyzer/                    # Coleta de métricas
│   ├── package_analyzer.py     # Script principal de análise
│   ├── config.json             # Configurações
│   └── modules/                # Módulos especializados
│       ├── __init__.py
│       ├── cache.py            # Análise de cache DNF
│       ├── dependencies.py     # Verificação de dependências
│       ├── orphans.py          # Detecção de órfãos
│       ├── packages.py         # Listagem de pacotes
│       └── updates.py          # Checagem de updates
│
├── reporter/                    # Geração de relatórios
│   ├── ai_package_reporter.py  # Gerador com IA
│   └── template.html           # Template HTML
│
├── requirements.txt            # Dependências Python
├── README.md                   # Este arquivo
├── LICENSE                     # Licença MIT
└── .gitignore                  # Arquivos ignorados
```

### Componentes

#### 📊 Analyzer (`analyzer/`)

Módulos independentes que coletam métricas específicas:

- **`packages.py`**: Lista todos os pacotes instalados com detalhes (nome, versão, tamanho, repositório)
- **`updates.py`**: Verifica atualizações disponíveis e de segurança
- **`orphans.py`**: Detecta pacotes órfãos e autoremovíveis
- **`cache.py`**: Mede tamanho do cache DNF
- **`dependencies.py`**: Identifica problemas de dependências

#### 🤖 Reporter (`reporter/`)

- **`ai_package_reporter.py`**: Processa JSON e chama Gemini API para análise humanizada
- **`template.html`**: Template responsivo com CSS moderno

---

## 📊 Exemplo de Relatório

O relatório HTML gerado contém:

### 🎯 Resumo Executivo
> "Você tem 2.450 pacotes instalados ocupando 15GB. Isso é normal para um Fedora Workstation com desenvolvimento. Existem 23 atualizações disponíveis, incluindo 5 críticas de segurança..."

### 📈 Cards de Métricas
- Total de pacotes
- Espaço ocupado
- Atualizações pendentes
- Pacotes órfãos
- Tamanho do cache

### 📝 Análises Detalhadas
- **Pacotes**: Interpretação de quantidade e tamanho
- **Updates**: Urgência e tipo de atualizações
- **Órfãos**: Quanto espaço pode recuperar
- **Cache**: Se precisa limpar
- **Dependências**: Problemas detectados

### ✅ Recomendações Priorizadas
- 🔴 **Alta**: "Atualize os 5 pacotes de segurança imediatamente"
- 🟡 **Média**: "Remova 150 pacotes órfãos e recupere 500MB"
- 🟢 **Baixa**: "Limpe o cache DNF quando tiver tempo"

Com comandos prontos:
```bash
sudo dnf update --security
sudo dnf autoremove
sudo dnf clean all
```

---

## 🛠️ Casos de Uso

### 1. Manutenção Periódica
Execute mensalmente para manter o sistema limpo e atualizado.

### 2. Auditoria de Segurança
Identifique rapidamente atualizações de segurança pendentes.

### 3. Otimização de Espaço
Descubra pacotes órfãos e cache desnecessário ocupando disco.

### 4. Documentação
Mantenha histórico de pacotes instalados em cada período.

### 5. Servidor Headless
Gere relatórios em servidores sem interface e envie por email/Slack.

---

## 🔧 Customização

### Adicionar Novos Módulos

Crie um arquivo em `analyzer/modules/`:

```python
# analyzer/modules/meu_modulo.py

def collect_minha_metrica(config):
    """Coleta minha métrica personalizada"""
    # Sua lógica aqui
    return {
        "minha_metrica": valor
    }
```

Importe em `package_analyzer.py`:

```python
from modules import meu_modulo

metrics["minha_metrica"] = meu_modulo.collect_minha_metrica(config)
```

### Modificar Template HTML

Edite `reporter/template.html` para customizar aparência, cores, layout, etc.

### Trocar Modelo de IA

No `ai_package_reporter.py`, altere a variável `model`:

```python
model = "gemini-2.5-pro"  # Modelo mais poderoso
```

---

## 🤝 Contribuindo

Contribuições são muito bem-vindas! 

### Como contribuir:

1. **Fork** o projeto
2. Crie uma **branch** para sua feature (`git checkout -b feature/MinhaFeature`)
3. **Commit** suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. **Push** para a branch (`git push origin feature/MinhaFeature`)
5. Abra um **Pull Request**

### Ideias para contribuir:

- 🌟 Suporte para outras distros (Arch, Debian, Ubuntu)
- 📧 Envio de relatórios por email
- 📱 Versão mobile do HTML
- 🌐 Tradução para outros idiomas
- 📊 Gráficos e visualizações
- 🔔 Notificações push
- 🐳 Container Docker

---

## 📜 Licença

Este projeto está sob a licença **MIT**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 🙋 Autor

**Pedro Lucas Montezuma Loureiro**

- 🐙 GitHub: [@montezuma-p](https://github.com/montezuma-p)
- 💼 LinkedIn: [in/montezuma-p](https://www.linkedin.com/in/montezuma-p/)
- 📍 Rio de Janeiro, Brasil 🇧🇷

---

## 🌟 Projetos Relacionados

Confira meus outros projetos de automação Linux:

- 🖥️ [**monitor-linux-ia**](https://github.com/montezuma-p/monitor_linux_ia) - Monitoramento de sistemas com IA
- 🧹 [**linux-storage-manager**](https://github.com/montezuma-p/linux-storage-manager) - Gerenciamento inteligente de storage
- 🔐 [**backup-universal**](https://github.com/montezuma-p/backup-universal) - Sistema de backup automatizado
- 🤖 [**iaprojeto-setup**](https://github.com/montezuma-p/iaprojeto-setup) - Scaffolding de projetos com IA

---

## 💬 Feedback e Suporte

Encontrou um bug? Tem uma ideia? Precisa de ajuda?

- 🐛 [Abra uma Issue](https://github.com/montezuma-p/packages/issues)
- 💡 [Sugira uma Feature](https://github.com/montezuma-p/packages/issues/new)
- 📧 Entre em contato via LinkedIn

---

## ⭐ Gostou?

Se este projeto foi útil, deixe uma ⭐ no repositório!

---

<div align="center">

**[⬆ Voltar ao topo](#-package-analyzer--ai-reporter)**

Feito com ❤️ e ☕ no Rio de Janeiro

🚀 **Bora construir algo dahora juntos!** 🚀

</div>
