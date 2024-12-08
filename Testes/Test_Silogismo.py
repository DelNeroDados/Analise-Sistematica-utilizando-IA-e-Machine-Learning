
#pip install sympy
#pip install --upgrade pip

import sympy as sp

# Verifique a versão instalada
print(sp.__version__)

from sympy import symbols, Implies, And, Or, Not, simplify_logic

def deduzir_silogismo(premissa1, premissa2, conclusao):
    # Definindo os símbolos
    # Extraindo os nomes das proposições
    p1, p2 = symbols(premissa1), symbols(premissa2)
    c = symbols(conclusao)

    # Definindo as premissas
    # A primeira premissa é uma implicação
    premissa1_logica = Implies(p1, c)  # Se P1, então C
    premissa2_logica = p2  # P2 é verdadeiro (ex: Socrates é Homem)

    # Representando a dedução
    conclusao_logica = simplify_logic(And(premissa1_logica, premissa2_logica))

    # Verificando se a conclusão se segue das premissas
    # Aqui, queremos verificar se a conclusão é verdadeira
    return conclusao_logica

# Exemplo de uso
if __name__ == "__main__":
    # Entradas do usuário
    premissa1 = input("Digite a primeira premissa (ex: 'Homem -> Mortal'): ")
    premissa2 = input("Digite a segunda premissa (ex: 'Socrates'): ")
    conclusao = input("Digite a conclusão (ex: 'Mortal'): ")

    # Deduza o silogismo
    resultado = deduzir_silogismo(premissa1, premissa2, conclusao)

    # Exibindo o resultado
    print("Resultado da dedução:", resultado)

    # Verificando se a conclusão se segue
    if resultado:
        print(f"A conclusão '{conclusao}' se segue das premissas.")
    else:
        print(f"A conclusão '{conclusao}' não se segue das premissas.")