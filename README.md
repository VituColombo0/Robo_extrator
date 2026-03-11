# Robo Extrator Final 🤖📊

Robo Extrator é uma ferramenta de automação construída em Python para extração automática e tratamento de dados das estações meteorológicas/climáticas do painel do Streamlit. 

O objetivo principal é substituir o trabalho manual e repetitivo de visualização e download de dados diários por estacão, entregando planilhas padronizadas e tratadas estatisticamente no formato Excel (`.xlsx`), prontas para análises.

## Funcionalidades
- **Interface Gráfica Integrada:** Interface simples e amigável (GUI) construída com Tkinter, sem necessidade de tela preta ou códigos.
- **Múltiplos Filtros de Data:** Permite baixar o dia atual, um dia específico, últimos X dias, um mês fechado ou um intervalo personalizado.
- **Seleção de Múltiplas Estações:** Processe lotes inteiros de várias estações de uma só vez.
- **Correção Inteligente de Timezone:** A ferramenta força o Streamlit a respeitar o dia exato (00:00 às 23:55), preenchendo falhas de horário vazias num grid perfeito de 24 horas (288 linhas métricas/dia).
- **Tratamento Matemático (Savgol & Akima):** Aplica interpolação avançada nos dados brutos para gerar curvas confiáveis nas colunas numéricas de temperatura e radiação.
- **Validação Gráfica Automática:** Gera e salva gráficos comparativos (`.png`) de cada métrica (curva crua vs curva tratada) para confiabilidade das teses.
- **Instalador Autossuficiente (Standalone):** O projeto foi compilado para `.exe` e inclui seu próprio navegador Edge invisível via Selenium Manager e todas as bibliotecas de Data Science integradas, operando em qualquer máquina Windows sem requerer instalação de Python ou pacotes de terceiros.

## Como Usar (Versão Executável)
Se você apenas quer usar a ferramenta pronta:
1. Vá até a pasta `dist/Robo_Extrator`.
2. Dê um duplo clique no arquivo **`Robo_Extrator.exe`**.
3. Selecione as Estações que deseja na lista (segure `Ctrl` para selecionar várias).
4. Escolha a aba de Filtro de Data.
5. Clique em **Iniciar Extração**.
6. Acompanhe o log visual verde. Ao finalizar, todos os arquivos (CSVs originais, tratados, planilhas Excel e gráficos) estarão separados metodicamente dentro da pasta `saida/`.

## Estrutura do Projeto (Para Desenvolvedores)
- `scripts/robo_extrator_final.py`: Arquivo principal contendo toda a lógica do bot em Selenium, limpeza de dados do Pandas e interface do Tkinter.
- `dist/Robo_Extrator/`: Pasta de distribuição gerada via PyInstaller contendo o software final compilado e empacotado para o cliente local.
- `saida/` *(gerada dinamicamente)*: Ambiente onde o bot salva ordenadamente as extrações, segmentadas por Estação, Ano e Mês.

## Tecnologias Utilizadas
- **Python 3.14**
- **Selenium** (Automação de Navegadores Web)
- **Pandas & NumPY** (Mineração e Manuseio de Dataframes)
- **SciPy** (Tratamento Akima/Savgol)
- **Matplotlib** (Plotagem de Gráficos de Validação)
- **PyInstaller** (Empacotamento)
- **Tkinter** (Interface Gráfica)
