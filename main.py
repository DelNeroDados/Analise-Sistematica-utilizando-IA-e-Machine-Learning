import sqlite3
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import shutil

class BraveHistoryClassifier:
    def __init__(self):
        self.brave_history_path = self.get_brave_history_path()
        self.tfidf = TfidfVectorizer(stop_words='english')
        self.user_interests = None
        self.visit_frequency = None
        
    def get_brave_history_path(self):
        # Caminho para o histórico do Brave em diferentes sistemas operacionais
        if os.name == 'nt':  # Windows
            return os.path.join(os.getenv('LOCALAPPDATA'),
                              r'BraveSoftware\Brave-Browser\User Data\Default\History')
        elif os.name == 'posix':  # macOS
            return os.path.expanduser('~/Library/Application Support/BraveSoftware/Brave-Browser/Default/History')
        else:  # Linux
            return os.path.expanduser('~/.config/BraveSoftware/Brave-Browser/Default/History')

    def get_brave_history(self, days_back=30):
        # Cria uma cópia temporária do arquivo de histórico
        temp_path = 'temp_history'
        shutil.copy2(self.brave_history_path, temp_path)

        # Conecta ao banco de dados
        conn = sqlite3.connect(temp_path)
        cursor = conn.cursor()

        # Calcula a data limite
        cutoff_date = int((datetime.now() - timedelta(days=days_back)).timestamp() * 1000000)

        # Consulta o histórico
        query = """
        SELECT url, title, visit_count, last_visit_time
        FROM urls
        WHERE last_visit_time > ?
        """
        
        cursor.execute(query, (cutoff_date,))
        history = cursor.fetchall()
        
        conn.close()
        os.remove(temp_path)
        
        return history

    def analyze_user_interests(self, history_data):
        # Processa títulos e URLs para extrair temas de interesse
        texts = []
        visit_counts = []
        
        for url, title, visit_count, _ in history_data:
            if title:  # Alguns registros podem não ter título
                texts.append(title)
                visit_counts.append(visit_count)
        
        # Calcula TF-IDF dos títulos
        tfidf_matrix = self.tfidf.fit_transform(texts)
        
        # Calcula média ponderada dos vetores TF-IDF usando visit_counts
        weighted_vectors = []
        for i, vector in enumerate(tfidf_matrix):
            weighted_vectors.append(vector.toarray()[0] * visit_counts[i])
        
        self.user_interests = np.mean(weighted_vectors, axis=0)
        
        # Calcula frequência de visitas por domínio
        domains = [self.extract_domain(url) for url, _, _, _ in history_data]
        self.visit_frequency = Counter(domains)

    def extract_domain(self, url):
        # Extrai domínio da URL
        try:
            from urllib.parse import urlparse
            return urlparse(url).netloc
        except:
            return url

    def calculate_relevance_score(self, paper):
        # Calcula score de relevância baseado nos interesses do usuário
        paper_text = f"{paper['title']} {paper['abstract']}"
        paper_vector = self.tfidf.transform([paper_text])
        
        # Similaridade com interesses do usuário
        interest_similarity = cosine_similarity(
            paper_vector.toarray(), 
            self.user_interests.reshape(1, -1)
        )[0][0]
        
        # Verifica se há referências a domínios frequentemente visitados
        domain_relevance = 0
        for domain, freq in self.visit_frequency.most_common(10):
            if domain.lower() in paper_text.lower():
                domain_relevance += freq / sum(self.visit_frequency.values())
        
        # Combina os scores
        final_score = 0.7 * interest_similarity + 0.3 * domain_relevance
        return final_score



import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

def fetch_arxiv_papers(query, max_results=100):
    try:
        # Codifica a consulta para URL
        encoded_query = urllib.parse.quote(query)
        
        # Monta a URL da API do arXiv
        base_url = 'http://export.arxiv.org/api/query?'
        query_params = {
            'search_query': f'all:{encoded_query}',
            'start': 0,
            'max_results': max_results,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }
        
        url = base_url + urllib.parse.urlencode(query_params)
        
        # Faz a requisição
        with urllib.request.urlopen(url) as response:
            response_text = response.read()
        
        # Parse do XML
        root = ET.fromstring(response_text)
        
        # Lista para armazenar os papers
        papers = []
        
        # Namespace do XML do arXiv
        namespace = {'atom': 'http://www.w3.org/2005/Atom'}
        
        # Extrai informações de cada entrada
        for entry in root.findall('atom:entry', namespace):
            try:
                paper = {
                    'title': entry.find('atom:title', namespace).text.strip(),
                    'abstract': entry.find('atom:summary', namespace).text.strip(),
                    'authors': [author.find('atom:name', namespace).text 
                              for author in entry.findall('atom:author', namespace)],
                    'link': entry.find('atom:id', namespace).text,
                    'published': entry.find('atom:published', namespace).text
                }
                papers.append(paper)
            except AttributeError as e:
                print(f"Erro ao processar um artigo: {e}")
                continue
        
        print(f"Encontrados {len(papers)} artigos sobre '{query}'")
        return papers
    
    except Exception as e:
        print(f"Erro ao buscar artigos: {e}")
        return []

# Atualização da função main()
def main():
    print("=== Sistema de Classificação baseado no Histórico do Brave ===")
    
    # Inicializa o classificador
    classifier = BraveHistoryClassifier()
    
    # Carrega e analisa histórico do Brave
    print("\nAnalisando seu histórico de navegação no Brave...")
    try:
        history_data = classifier.get_brave_history(days_back=30)
        classifier.analyze_user_interests(history_data)
        print(f"Analisados {len(history_data)} registros do histórico.")
    except Exception as e:
        print(f"Erro ao acessar histórico do Brave: {e}")
        return

    # Busca artigos
    query = input("\nDigite sua consulta: ")
    papers = fetch_arxiv_papers(query)
    
    if not papers:
        print("Nenhum artigo encontrado. Tente outra consulta.")
        return
    
    print("\nClassificando artigos com base em seus interesses...")
    
    # Classifica artigos
    scored_papers = []
    for paper in papers:
        try:
            relevance_score = classifier.calculate_relevance_score(paper)
            scored_papers.append((paper, relevance_score))
        except Exception as e:
            print(f"Erro ao classificar artigo: {e}")
            continue
    
    if not scored_papers:
        print("Não foi possível classificar os artigos.")
        return
    
    # Ordena por relevância
    scored_papers.sort(key=lambda x: x[1], reverse=True)
    
    # Mostra resultados
    print("\nArtigos mais relevantes baseados em seu histórico de navegação no Brave:")
    for i, (paper, score) in enumerate(scored_papers[:10], 1):
        print(f"\n{i}. Título: {paper['title']}")
        print(f"Score de Relevância: {score:.2f}")
        print(f"Link: {paper['link']}")
        print("Abstract:", paper['abstract'][:200] + "...")

    # Salva resultados
    try:
        results_df = pd.DataFrame([
            {
                'title': paper['title'],
                'score': score,
                'link': paper['link'],
                'abstract': paper['abstract']
            }
            for paper, score in scored_papers
        ])
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'brave_personalized_papers_{timestamp}.xlsx'
        results_df.to_excel(filename, index=False)
        print(f"\nResultados salvos em '{filename}'")
    except Exception as e:
        print(f"Erro ao salvar resultados: {e}")

if __name__ == "__main__":
    main()
