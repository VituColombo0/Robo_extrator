# Robo_extrator: Pipeline de Extração e Tratamento de Dados Meteorológicos

Sistema automatizado de extração, validação física, interpolação matemática e visualização gráfica de dados meteorológicos coletados de estações de monitoramento remotas baseadas em Streamlit.

[![Python: 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Automation: Selenium](https://img.shields.io/badge/Browser%20Automation-Selenium%20Edge-informational.svg)](https://www.selenium.dev/)
[![Math: SciPy & NumPy](https://img.shields.io/badge/Signal%20Processing-SciPy%20%2F%20Akima-orange.svg)](https://scipy.org/)
[![Data: Pandas & OpenPyXL](https://img.shields.io/badge/Data-Pandas%20%2B%20Excel-darkgreen.svg)](https://pandas.pydata.org/)
[![GUI: Tkinter](https://img.shields.io/badge/Interface-Tkinter%20Desktop-purple.svg)](https://docs.python.org/3/library/tkinter.html)

---

## Visão Geral

Estações meteorológicas remotas frequentemente apresentam falhas pontuais de transmissão, ruídos eletromagnéticos em sensores de radiação/vento e indisponibilidade temporária de link. O **Robo_extrator** substitui o download manual e o pós-processamento artesanal por um fluxo ponta a ponta robusto com validações físicas e filtros de processamento de sinais.

```
[ Estação Meteorológica ]
  (Streamlit Web Portal)
            │
            ▼
 [ Camada de Ingestão ] ── Selenium EdgeChromium com tratamento de retry e paginação
            │
            ▼
 [ Validação Física ]   ── Correção de limites (radiação >= 0, umidade 0-100%, etc.)
            │
            ▼
 [ Interpolação Akima ] ── Preenchimento contínuo de lacunas temporais sem sobreoscilações
            │
            ▼
[ Filtro Savitzky-Golay]── Suavização de ruído de alta frequência preservando picos reais
            │
            ▼
 [ Camada de Entrega ]  ── Planilhas Excel tratadas (.xlsx) e gráficos comparativos (.png)
```

---

## Camadas da Arquitetura

### 1. Ingestão Automatizada
- Opera via **Selenium WebDriver** configurado para o navegador **Microsoft Edge (EdgeChromium)** em modo assistido ou headless.
- Implementa esperas explícitas (*Explicit Waits*) e tratamento de exceções de conexão para contornar instabilidades no carregamento dos elementos do Streamlit.

### 2. Tratamento e Validação de Dados
- **Sanitização de Fronteira:** Garante consistência física nas leituras (bloqueio de valores negativos de irradiância solar global, corte de umidades relativas superiores a 100%).
- **Interpolação Akima 1D:** Utilizada para preenchimento de períodos curtos de perda de dados. O algoritmo de Akima constrói polinômios de terceiro grau contínuos sem os artefatos de oscilação artificial (*Runge's phenomenon*) típicos de *cubic splines* convencionais.
- **Filtragem Savitzky-Golay:** Aplica convolução polinomial por mínimos quadrados sobre janelas móveis de tempo, atenuando ruído elétrico dos sensores sem distorcer picos pontuais de rajadas de vento e picos térmicos.

### 3. Visualização e Auditoria
- Produz automaticamente painéis com **Matplotlib** contrapondo a série temporal bruta (*Raw*) à série tratada (*Sanitized*), permitindo validação visual rápida por meteorologistas e pesquisadores.

### 4. Interface Gráfica (GUI)
- Desenvolvida com **Tkinter**, permite selecionar facilmente as estações monitoradas, parametrizar intervalos de datas e acompanhar a barra de progresso e logs em tempo real.

---

## Pré-requisitos de Ambiente

- **Python 3.10** ou superior instalado no host
- **Microsoft Edge** instalado (o `webdriver-manager` gerencia o download automático do driver compatível)

---

## Instalação

```bash
# Clone o repositório
git clone https://github.com/VituColombo0/Robo_extrator.git
cd Robo_extrator

# Instale os módulos necessários via pip
pip install selenium pandas numpy scipy matplotlib webdriver-manager openpyxl
```

---

## Como Executar

1. Inicie a aplicação gráfica:
   ```bash
   python robo_extrator.py
   ```
2. Na janela da interface:
   - Marque as estações meteorológicas de interesse.
   - Defina o intervalo de datas (Data Inicial e Data Final).
   - Clique em **INICIAR EXTRAÇÃO**.
3. O robô executará o fluxo de navegação, coleta, cálculo e renderização.

---

## Estrutura do Projeto e Saídas

Os arquivos processados são consolidados automaticamente no diretório `saida/`:

```text
Robo_extrator/
├── robo_extrator.py          # Lógica central de raspagem, tratamento matemático e GUI
├── _internal/                # Recursos de empacotamento e assets da aplicação
├── saida/
│   ├── ORIGINAL/             # Arquivos CSV brutos exportados do portal
│   ├── CORRIGIDO/            # Séries temporais após validação de limites físicos
│   ├── EXCEL_TRATADO/        # Planilhas consolidadas em formato final (.xlsx)
│   ├── GRAFICOS/             # Imagens comparativas (Bruto vs Tratado) em alta definição
│   └── LOGS/                 # Registros de depuração e auditoria de cada execução
└── README.md                 # Documentação técnica
```

---

## Licença

Projeto desenvolvido para automação de coleta de dados ambientais.
