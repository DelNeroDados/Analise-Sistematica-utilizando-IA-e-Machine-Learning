import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
from bs4 import BeautifulSoup

# Baixando as stopwords apenas uma vez
nltk.download('stopwords')

# Função para limpar e preparar o texto
def limpa_texto(texto):
    stop_words = set(stopwords.words('portuguese'))
    palavras = texto.split()
    palavras_filtradas = [palavra.lower() for palavra in palavras if palavra.lower() not in stop_words]
    return ' '.join(palavras_filtradas)

# Simulando a obtenção de histórico de navegação do Brave (substituir por dados reais)
historico_navegacao = [
    {"titulo": "Filosofia e o sentido da vida", "url": "https://exemplo.com/filosofia-sentido-vida"},
    {"titulo": "Introdução à Filosofia Antiga", "url": "https://exemplo.com/introducao-filosofia-antiga"},
    {"titulo": "Error 400 (Solicitação inválida)!!1", "url": "https://console.cloud.google.com/invalid"},
    # Adicione outros exemplos
]

consulta = input("Digite sua consulta: ")

# Definindo palavras-chave relevantes para filtragem de relevância
palavras_chave = ["filosofia", "filósofo", "ética", "existencialismo", "aristóteles", "platonismo", "filosófico"]

# Extraindo textos das páginas para análise de relevância
resultados_analise = []
for item in historico_navegacao:
    try:
        response = requests.get(item["url"])
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            texto = soup.get_text(separator=" ", strip=True)
            
            # Filtra páginas com pouco conteúdo
            if len(texto) < 200:
                continue  # Ignora páginas com menos de 200 caracteres
            
            texto_limpo = limpa_texto(texto)
            
            # Filtra páginas que não contenham palavras-chave relevantes
            if not any(palavra in texto_limpo for palavra in palavras_chave):
                continue
            
            resultados_analise.append({"titulo": item["titulo"], "url": item["url"], "texto_limpo": texto_limpo})
    except requests.exceptions.RequestException:
        print(f"Erro ao acessar {item['url']}")

# Vetorizando e calculando similaridade
documentos = [consulta] + [res["texto_limpo"] for res in resultados_analise]
vetorizador = TfidfVectorizer()
matriz_tfidf = vetorizador.fit_transform(documentos)
similaridades = cosine_similarity(matriz_tfidf[0:1], matriz_tfidf[1:]).flatten()

# Exibindo resultados ordenados pela relevância
resultados_ordenados = sorted(zip(similaridades, resultados_analise), key=lambda x: x[0], reverse=True)

print("\nArtigos mais relevantes baseados em seu histórico de navegação:\n")
for i, (score, artigo) in enumerate(resultados_ordenados):
    if score > 0:  # Ignora resultados sem relevância
        print(f"{i+1}. Título: {artigo['titulo']}")
        print(f"Score de Relevância: {score:.2f}")
        print(f"Link: {artigo['url']}\n")
