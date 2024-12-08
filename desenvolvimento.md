Aqui está a versão revisada do texto, com os trechos de código colocados embaixo de cada parágrafo relevante:

---

Primeiramente, foi realizada a coleta de dados do histórico de navegação do navegador Brave. O navegador Brave armazena o histórico em um banco de dados SQLite, cujo caminho pode variar dependendo do sistema operacional (KROGH, 2020).

```python
class BraveHistoryClassifier:
    def get_brave_history_path():
        # Código que identifica o caminho do arquivo de histórico conforme o sistema operacional
        # Exemplos de caminhos para diferentes sistemas
```

Para acessá-lo, a classe `BraveHistoryClassifier` foi implementada com um método `get_brave_history_path()` que identifica o caminho correto do arquivo de histórico dependendo do sistema operacional em uso (WINDOWS, LINUX ou macOS). Visando o acesso de forma segura, uma cópia temporária é criada usando a biblioteca `shutil`, a fim de evitar bloqueios de acesso ao arquivo original (GRANERUD et al., 2023).

```python
import shutil

# Criar cópia temporária do arquivo de histórico para evitar bloqueios
shutil.copy2(original_path, temp_path)
```

Em seguida, para extrair os dados, a função `get_brave_history()` conecta-se ao arquivo SQLite temporário e executa uma consulta SQL para obter os registros dos últimos 30 dias. Este período pode ser ajustado conforme necessário para a análise. O método `cursor.execute()` foi empregado para realizar a consulta e recuperar os dados de URL, título, contagem de visitas e data da última visita (CONWAY, 2021).

```python
import sqlite3

def get_brave_history(temp_path):
    conn = sqlite3.connect(temp_path)
    cursor = conn.cursor()
    query = """
    SELECT url, title, visit_count, last_visit_time
    FROM urls
    WHERE last_visit_time >= ?
    """
    cursor.execute(query, (last_30_days,))
    results = cursor.fetchall()
    conn.close()
    return results
```

O processamento dos dados extraídos é essencial para a análise dos interesses do usuário. A técnica de TF-IDF (Term Frequency-Inverse Document Frequency) foi aplicada para converter os títulos das páginas visitadas em vetores numéricos que representam a relevância de cada termo (JONES, 1972).

```python
from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(page_titles)
```

Para vetorização dos textos, o método `analyze_user_interests()` foi utilizado, uma vez que usa o `TfidfVectorizer` para processar os títulos das páginas visitadas e gerar uma matriz TF-IDF. Esta matriz é ponderada pela contagem de visitas, calculando a média ponderada dos vetores TF-IDF (SALTON et al., 1988).

```python
def analyze_user_interests(page_titles, visit_counts):
    tfidf_matrix = vectorizer.fit_transform(page_titles)
    weighted_tfidf = (tfidf_matrix.T * visit_counts).T
    average_vector = weighted_tfidf.mean(axis=0)
    return average_vector
```

Já para a extração de domínios e contagem de frequência, foi escolhida a função `extract_domain()` que extrai os domínios das URLs para identificar quais sites são mais frequentemente visitados. A contagem de frequência dos domínios é feita usando a classe `Counter` da biblioteca `collections` (MCLOUGHLIN, 2014).

```python
from collections import Counter
from urllib.parse import urlparse

def extract_domain(urls):
    domains = [urlparse(url).netloc for url in urls]
    domain_counts = Counter(domains)
    return domain_counts
```

Por fim, a API do arXiv foi usada para obter artigos acadêmicos relevantes. A função `fetch_arxiv_papers()` realiza a consulta e parseia os resultados em formato XML (CHEN et al., 2020).

```python
import requests
import xml.etree.ElementTree as ET

def fetch_arxiv_papers(query):
    response = requests.get(f"http://export.arxiv.org/api/query?search_query={query}")
    tree = ET.fromstring(response.content)
    # Código para parsear o XML e extrair informações dos artigos
```

Os artigos dela obtidos foram avaliados de acordo com sua similaridade de conteúdo por meio do método `calculate_relevance_score()` que avalia a relevância dos artigos obtidos comparando-os com os interesses do usuário, utilizando similaridade de cosseno entre o vetor TF-IDF do artigo e o vetor médio dos interesses do usuário (WANG et al., 2018). Além disso, o método verifica se os domínios mais visitados pelo usuário aparecem nos textos dos artigos para calcular um fator de relevância adicional.

```python
from sklearn.metrics.pairwise import cosine_similarity

def calculate_relevance_score(user_vector, article_vector):
    score = cosine_similarity(user_vector, article_vector)
    return score
```

Por fim, os artigos foram classificados com base no score combinado de similaridade de interesses e relevância de domínios, e os resultados foram armazenados em um arquivo Excel usando a biblioteca `pandas` para fácil visualização e posterior análise (MCKINNEY, 2010).

```python
import pandas as pd

df = pd.DataFrame(results)
timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
df.to_excel(f"artigos_relevantes_{timestamp}.xlsx", index=False)
```

Este sistema pode ser expandido para incluir outras fontes de dados e métodos de análise mais sofisticados, como modelos de aprendizado profundo para PLN (YANG et al., 2019).

--- 

Desta forma, os trechos de código ilustram as descrições no texto explicativo.