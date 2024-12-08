import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import time
import random
import sqlite3
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def fetch_arxiv_papers(query, max_results=100):
    base_url = 'http://export.arxiv.org/api/query?'
    query_params = {
        'search_query': query,
        'start': 0,
        'max_results': max_results,
        'sortBy': 'relevance',
        'sortOrder': 'descending'
    }
    
    url = base_url + urllib.parse.urlencode(query_params)
    
    with urllib.request.urlopen(url) as response:
        response_text = response.read()
    
    root = ET.fromstring(response_text)
    
    papers = []
    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        title = entry.find('{http://www.w3.org/2005/Atom}title')
        summary = entry.find('{http://www.w3.org/2005/Atom}summary')
        authors = entry.findall('{http://www.w3.org/2005/Atom}author')
        published = entry.find('{http://www.w3.org/2005/Atom}published')
        link = entry.find('{http://www.w3.org/2005/Atom}id')
        
        paper = {
            'title': title.text if title is not None else "Título não disponível",
            'abstract': summary.text if summary is not None else "Resumo não disponível",
            'authors': [author.find('{http://www.w3.org/2005/Atom}name').text for author in authors if author.find('{http://www.w3.org/2005/Atom}name') is not None],
            'published': published.text if published is not None else "Data não disponível",
            'link': link.text if link is not None else "Link não disponível"
        }
        papers.append(paper)
    
    return papers

class ArxivClassifier:
    def __init__(self):
        self.tfidf = TfidfVectorizer(max_features=1000, stop_words='english')
        self.clf = RandomForestClassifier(n_estimators=100, random_state=42)

    def prepare_features(self, papers):
        texts = [f"{p['title']} {p['abstract']}" for p in papers]
        return self.tfidf.fit_transform(texts)

    def train(self, papers, labels):
        X = self.prepare_features(papers)
        self.clf.fit(X, labels)

    def predict(self, papers):
        X = self.tfidf.transform([f"{p['title']} {p['abstract']}" for p in papers])
        return self.clf.predict_proba(X)[:, 1]

class ChromeHistoryClassifier:
    def __init__(self):
        self.chrome_history_path = self.get_chrome_history_path()
        self.tfidf = TfidfVectorizer(stop_words='english')
        self.user_interests = None
        self.visit_frequency = None
        
    def get_chrome_history_path(self):
        # Caminho para o histórico do Chrome em diferentes sistemas operacionais
        if os.name == 'nt':  # Windows
            return os.path.join(os.getenv('LOCALAPPDATA'), r'Google\Chrome\User Data\Default\History')
        elif os.name == 'posix':  # macOS
            return os.path.expanduser('~/Library/Application Support/Google/Chrome/Default/History')
        else:  # Linux
            return os.path.expanduser('~/.config/google-chrome/Default/History')

    def get_chrome_history(self, days_back=30):
        if not os.path.exists(self.chrome_history_path):
            raise FileNotFoundError("O arquivo de histórico do Chrome não foi encontrado.")
        
        # Cria uma cópia temporária do arquivo de histórico
        temp_path = 'temp_history'
        try:
            with open(self.chrome_history_path, 'rb') as f:
                with open(temp_path, 'wb') as temp:
                    temp.write(f.read())

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
        finally:
            if os.path.exists(temp_path):
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
        except ValueError as e:
            print(f"Erro ao extrair domínio da URL: {e}")
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

def main():
    print("=== Sistema de Classificação baseado no Histórico do Chrome ===")
    
    # Inicializa o classificador
    classifier = ChromeHistoryClassifier()
    
    # Carrega e analisa histórico do Chrome
    print("\nAnalisando seu histórico de navegação...")
    try:
        history_data = classifier.get_chrome_history(days_back=30)
        classifier.analyze_user_interests(history_data)
        print(f"Analisados {len(history_data)} registros do histórico.")
    except Exception as e:
        print(f"Erro ao acessar histórico do Chrome: {e}")
        return

    # Busca artigos
    query = input("\nDigite sua consulta: ")
    papers = fetch_arxiv_papers(query)  # Usando a função do exemplo anterior
    
    print("\nClassificando artigos com base em seus interesses...")
    
    # Classifica artigos
    scored_papers = []
    for paper in papers:
        relevance_score = classifier.calculate_relevance_score(paper)
        scored_papers.append((paper, relevance_score))
    
    # Ordena por relevância
    scored_papers.sort(key=lambda x: x[1], reverse=True)
    
    # Mostra resultados
    print("\nArtigos mais relevantes baseados em seu histórico de navegação:")
    for i, (paper, score) in enumerate(scored_papers[:10], 1):
        print(f"\n{i}. Título: {paper['title']}")
        print(f"Score de Relevância: {score:.2f}")
        print(f"Link: {paper['link']}")
        print("Abstract:", paper['abstract'][:200] + "...")

    # Salva resultados
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
    results_df.to_excel(f'personalized_papers_{timestamp}.xlsx', index=False)
    print(f"\nResultados salvos em 'personalized_papers_{timestamp}.xlsx'")

if __name__ == "__main__":
    main()