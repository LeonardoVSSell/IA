import random

def ler_instancia(arquivo):
    clausulas = []
    with open(arquivo, 'r') as f:
        for linha in f:
            if linha.startswith('c') or linha.startswith('p') or linha.startswith('0') or linha.startswith('%') or linha.startswith('\n'):
                continue
            clausula = [int(x) for x in linha.strip().split()]
            print(clausula)
            if clausula[-1] == 0:
                clausula.pop()
            clausulas.append(clausula)
    return clausulas

def gerar_solucao_aleatoria(n_variaveis):
    return [random.choice([True, False]) for _ in range(n_variaveis)]

def calcular_clausulas_satisfeitas(clausulas, solucao):
    satisfeitas = 0
    for clausula in clausulas:
        for literal in clausula:
            var_index = abs(literal) - 1
            if (literal > 0 and solucao[var_index]) or (literal < 0 and not solucao[var_index]):
                satisfeitas += 1
                break
    return satisfeitas

def calcular_clausulas_nao_satisfeitas(clausulas, solucao):
    nao_satisfeitas = 0
    for clausula in clausulas:
        satisfeita = False
        for literal in clausula:
            var_index = abs(literal) - 1
            if (literal > 0 and solucao[var_index]) or (literal < 0 and not solucao[var_index]):
                satisfeita = True
                break
        if not satisfeita:
            nao_satisfeitas += 1
    return nao_satisfeitas

# SA
def simulated_annealing(clausulas, n_variaveis):
    pass  # A implementação do SA será feita aqui

# Testando as funções com uma instância de exemplo
if __name__ == "__main__":
    arquivo_instancia = 'uf20-01.cnf'  # Substituir pelo caminho do arquivo real
    clausulas = ler_instancia(arquivo_instancia)
    
    n_variaveis = max(abs(literal) for clausula in clausulas for literal in clausula)  # Calcula o número de variáveis
    solucao_aleatoria = gerar_solucao_aleatoria(n_variaveis)
    print(solucao_aleatoria)

    # Testando versão de maximização
    satisfeitas = calcular_clausulas_satisfeitas(clausulas, solucao_aleatoria)
    print(f"Cláusulas satisfeitas (maximização): {satisfeitas}")
    
    # Testando versão de minimização
    nao_satisfeitas = calcular_clausulas_nao_satisfeitas(clausulas, solucao_aleatoria)
    print(f"Cláusulas não satisfeitas (minimização): {nao_satisfeitas}")


