# Sistema de Recomendação de Artigos Científicos Personalizado

Este projeto implementa um sistema de recomendação de artigos científicos do arXiv com base no histórico de navegação do navegador Brave. A aplicação extrai dados de interesse do histórico, utiliza esses dados para classificar artigos do arXiv e recomenda os artigos mais relevantes para o usuário.

## Estrutura do Projeto

O sistema é composto por dois módulos principais:

1. **BraveHistoryClassifier**: Analisa o histórico de navegação do usuário no navegador Brave para identificar interesses baseados na frequência de visita e no conteúdo das páginas.
2. **ArxivClassifier**: Classifica artigos do arXiv de acordo com a relevância para o usuário, com base nas preferências calculadas pelo BraveHistoryClassifier.

## Pré-requisitos

- **Python 3.x**
- **Bibliotecas Python**:
  - `numpy`
  - `scikit-learn`
  - `pandas`
  - `sqlite3`
  - `shutil`
  - `datetime`
  - `urllib`
  - `xml.etree.ElementTree`

Instale as bibliotecas adicionais usando o comando:

```bash
pip install numpy scikit-learn pandas
```

## Descrição das Funções

### `fetch_arxiv_papers(query, max_results=100)`

Esta função busca artigos científicos no arXiv de acordo com a consulta informada e retorna uma lista de artigos. A busca é realizada via a API do arXiv.

- **Parâmetros**:
  - `query`: Termo de busca (ex.: "machine learning").
  - `max_results`: Número máximo de artigos a serem retornados.
  
- **Retorno**:
  - Uma lista de dicionários com `title`, `abstract`, `authors`, `published` e `link` de cada artigo.

### Classe `ArxivClassifier`

Esta classe utiliza um classificador Random Forest para treinar e prever a relevância de artigos para o usuário.

- **Métodos**:
  - `prepare_features(papers)`: Extrai características de artigos usando TF-IDF.
  - `train(papers, labels)`: Treina o classificador com os dados dos artigos e suas respectivas classificações.
  - `predict(papers)`: Realiza previsões de relevância com base em novos artigos.

### Classe `BraveHistoryClassifier`

Esta classe analisa o histórico de navegação no navegador Brave para identificar interesses e calcular frequências de visita por domínio.

- **Métodos**:
  - `get_brave_history_path()`: Determina o caminho para o arquivo de histórico do Brave.
  - `get_brave_history(days_back=30)`: Obtém o histórico de navegação dos últimos 30 dias.
  - `analyze_user_interests(history_data)`: Analisa os títulos do histórico e calcula os interesses do usuário com base na frequência de visitas.
  - `extract_domain(url)`: Extrai o domínio de uma URL.
  - `calculate_relevance_score(paper)`: Calcula a relevância de um artigo do arXiv com base nos interesses do usuário.

### `main()`

A função principal, que executa o fluxo do programa. Ela:
1. Inicializa o classificador de histórico Brave e analisa o histórico de navegação do usuário.
2. Coleta artigos relevantes do arXiv.
3. Classifica os artigos de acordo com os interesses do usuário.
4. Exibe os 10 artigos mais relevantes para o usuário.
5. Salva os resultados em um arquivo Excel com nome único baseado em timestamp.

## Uso

1. **Configuração Inicial**:
   - Certifique-se de que o histórico do navegador Brave está disponível no caminho padrão.
   - Instale as bibliotecas necessárias com `pip install`.

2. **Execução do Programa**:
   - Execute o script principal:
     ```bash
     python nome_do_arquivo.py
     ```
   - Informe a consulta para busca de artigos no arXiv.
   - O sistema analisará o histórico de navegação e classificará os artigos.

3. **Resultados**:
   - Os artigos mais relevantes são exibidos no console e salvos em um arquivo Excel na pasta de execução.

## Observações

- Este projeto depende do histórico do navegador Brave e do acesso à API do arXiv.
- Somente os domínios mais visitados e as palavras-chave mais frequentes são considerados para relevância.

## Limitações

- O sistema foi desenvolvido para identificar temas de interesse com base em textos de títulos e resumos, mas pode ser refinado para incluir uma análise mais robusta do conteúdo dos artigos e do histórico de navegação.
