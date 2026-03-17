# Robo Extrator 🤖

Este projeto é um extrator automatizado desenvolvido para minerar e processar dados meteorológicos (Pluviometria, Temperatura, Umidade, Radiação e Vento).

## 🚀 Funcionalidades

- **Extração Automatizada**: Coleta dados brutos de fontes meteorológicas.
- **Processamento de Dados**: Limpa e formata os dados para saída em formato CSV.
- **Correção de Radiação**: Inclui algoritmos para evitar valores negativos ou absurdos nos índices de radiação.
- **Alta Performance**: Executável otimizado (redução de >140MB em bibliotecas desnecessárias).

## 📂 Estrutura do Projeto

- `Robo_Extrator.exe`: Executável principal da aplicação.
- `_internal/`: Dependências e bibliotecas necessárias para o funcionamento do executável.

## 🛠️ Como Utilizar

1. **Configuração**: Certifique-se de que a pasta `_internal` esteja no mesmo diretório que o `Robo_Extrator.exe`.
2. **Execução**: Dê um duplo clique no arquivo `Robo_Extrator.exe`.
3. **Saída**: Os dados processados serão gerados na pasta de destino configurada (geralmente em formato `.csv`).

## 🧹 Manutenção e Otimização

O projeto passou por uma limpeza rigorosa onde bibliotecas pesadas de ciência de dados (como `scipy` e `matplotlib`) foram removidas para tornar o executável mais leve, mantendo 100% da funcionalidade de extração e automação.

## 👤 Autor

Desenvolvido por **Victor Vieira Colombo**.
