import re
from unidecode import unidecode

def clean_text(text):
    if not isinstance(text, str):
        return ''
    
    # Remove caracteres não ASCII
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)

    # Normaliza caracteres
    text = unidecode(text)

    # Corrige caracteres específicos de codificação
    replacements = {
        'â€¦': '...',   # Corrige o 'â€¦' para '...'
        'â€': '"',      # Corrige o caractere de aspas
        'â€™': '\'',    # Corrige o caractere de apóstrofo
        'â€“': '-',     # Corrige o caractere de travessão
        'â€œ': '"',     # Corrige aspas duplas esquerda
        'â€': '"',     # Corrige aspas duplas direita
        'â€˜': '\'',    # Corrige aspas simples esquerda
        'â€™': '\'',    # Corrige aspas simples direita
        '…': '...',     # Substitui '…' por '...'
    }

    # Aplica todas as substituições
    for old, new in replacements.items():
        text = text.replace(old, new)

    # Remove espaços extras
    text = re.sub(r'\s+', ' ', text).strip()

    return text


# Teste da função clean_text
test_snippet = "Ethical machine learning in healthcare,â€¦ Figure 1 We motivate the five steps in the ethical pipeline for healthcare model development. Each stage contains considerations for machine learning where ignoring technical â€¦"
cleaned_snippet = clean_text(test_snippet)
print(f"Snippet original: {test_snippet}")
print(f"Snippet limpo: {cleaned_snippet}")
