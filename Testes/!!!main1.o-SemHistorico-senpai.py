import requests  # Para fazer requisições HTTP
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from collections import Counter
from datetime import datetime

class PaperRecommender:
    def __init__(self):
        self.tfidf = TfidfVectorizer(stop_words='english')
        self.user_interests = None
        self.visit_frequency = None

    def calculate_relevance_score(self, paper):
        # Calcula score de relevância baseado nos interesses do usuário
        paper_text = f"{paper['title']} {paper['abstract']}"
        paper_vector = self.tfidf.transform([paper_text])
        
        # Similaridade com interesses do usuário
        interest_similarity = cosine_similarity(
            paper_vector.toarray(), 
            self.user_interests.reshape(1, -1)
        )[0][0]
        
        # Verifica se há referências a domínios frequentemente visitados (aqui pode ser adaptado)
        domain_relevance = 0
        # (A lógica de domínio pode ser adaptada ou removida, já que não estamos usando histórico)

        # Combina os scores
        final_score = 0.7 * interest_similarity + 0.3 * domain_relevance
        return final_score

    def analyze_user_interests(self, papers):
        # Processa títulos e resumos para extrair temas de interesse
        texts = [f"{paper['title']} {paper['abstract']}" for paper in papers]
        
        # Calcula TF-IDF dos textos
        tfidf_matrix = self.tfidf.fit_transform(texts)
        
        # Média dos vetores TF-IDF
        self.user_interests = np.mean(tfidf_matrix.toarray(), axis=0)

def fetch_sempai_papers(query, api_key, max_results=100):
    try:
        # Monta a URL da API do Sempai
        base_url = 'https://api.sempai.com/v1/papers'
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        params = {
            'query': query,
            'max_results': max_results
        }
        
        # Faz a requisição
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()  # Levanta um erro para códigos de status HTTP 4xx/5xx
        
        # Extrai informações dos artigos
        papers = response.json().get('papers', [])
        
        print(f"Encontrados {len(papers)} artigos sobre '{query}'")
        return papers
    
    except Exception as e:
        print(f"Erro ao buscar artigos: {e}")
        return []

# Atualização da função main()
def main():
    print("=== Sistema de Recomendação de Artigos ===")
    
    # Inicializa o recomendador
    recommender = PaperRecommender()

    # Busca artigos
    query = input("\nDigite sua consulta: ")
    api_key = "d6ccb17175bc57498fba26947fa270348792aca335e7d2eb8c651482f18b3952"  # Chave da API do Sempai
    papers = fetch_sempai_papers(query, api_key)
    
    if not papers:
        print("Nenhum artigo encontrado. Tente outra consulta.")
        return
    
    print("\nAnalisando artigos para recomendações...")
    
    # Analisa interesses do usuário com base nos artigos encontrados
    recommender.analyze_user_interests(papers)
    
    # Classifica artigos
    scored_papers = []
    for paper in papers:
        try:
            relevance_score = recommender.calculate_relevance_score(paper)
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
    print("\nArtigos mais relevantes baseados na sua consulta:")
    for i, (paper, score) in enumerate(scored_papers[:10], 1):
        print(f"\n{i}. Título: {paper['title']}")
        print(f"Score de Relevância: {score:.2f}")
        print(f"Link: {paper['link']}")
        print(" Abstract:", paper['abstract'][:200] + "...")

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
        filename = f'recommended_papers_{timestamp}.xlsx'
        results_df.to_excel(filename, index=False)
        print(f"\nResultados salvos em '{filename}'")
    except Exception as e:
        print(f"Erro ao salvar resultados: {e}")

if __name__ == "__main__":
    main()