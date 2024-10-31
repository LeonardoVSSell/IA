import random
import math
import matplotlib.pyplot as plt

def ler_instancia(arquivo):
    clausulas = []
    numeroLiterais = 0
    with open(arquivo, 'r') as f:
        for linha in f:
            if linha.startswith('c') or linha.startswith('0') or linha.startswith('%') or linha.startswith('\n'):
                continue
            if linha.startswith('p'):
                linha = linha.split()
                numeroLiterais = int(linha[2])
                #print(numeroLiterais)
                continue
            else:
                clausula = [int(x) for x in linha.strip().split()]
            #print(clausula)
            
            if clausula[-1] == 0:
                clausula.pop()
            clausulas.append(clausula)
    return clausulas, numeroLiterais

def gerar_solucao_aleatoria(n_variaveis):
    return [random.choice([True, False]) for _ in range(n_variaveis)]

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

# Rotina para geração de vizinho
def gerar_vizinho(solucao, percentual_modificacao=0.05):
    n_variaveis = len(solucao)
    n_bits_flip = max(1, int(percentual_modificacao * n_variaveis))  # Define a quantidade de bits a serem modificados (pelo menos 1)
    
    nova_solucao = solucao[:]
    indices_modificados = random.sample(range(n_variaveis), n_bits_flip)  # Escolhe aleatoriamente quais bits serão modificados
    
    for indice in indices_modificados:
        nova_solucao[indice] = not nova_solucao[indice]  # Bit-flip (muda o bit de True para False ou vice-versa)
    
    return nova_solucao

def coeficiente_temperatura_logistica(T0, TN, it, itMax):
    # Parâmetros para controlar a forma da curva sigmoidal
    midpoint = itMax / 3  # Ponto médio das iterações onde a transição ocorre
    steepness = 1000  # Ajusta a inclinação da transição; aumente para uma queda mais abrupta

    # Função logística para controlar a temperatura
    return TN + (T0 - TN) / (1 + math.exp((it - midpoint) / (itMax / steepness)))


def simulated_annealing(clausulas, n_variaveis, T0, itMax, t, SAmAx):
    solucao_atual = gerar_solucao_aleatoria(n_variaveis)
    melhor_solucao = solucao_atual[:]
    
    f_atual = calcular_clausulas_nao_satisfeitas(clausulas, solucao_atual)
    f_melhor = f_atual

    historico_f_objetivo = [f_atual]
    historico_temperatura = [T0]

    T = T0
    iteracoes = 0
    
    while iteracoes < itMax and T > 0.000000000001:
        iterT = 0
        
        while iterT < SAmAx:
            iterT += 1
            iteracoes += 1
            
            # Gera vizinho e sua função
            vizinho = gerar_vizinho(solucao_atual)
            f_vizinho = calcular_clausulas_nao_satisfeitas(clausulas, vizinho)
            
            delta = f_vizinho - f_atual
            
            # Nova solução
            if delta < 0:
                solucao_atual = vizinho[:]
                f_atual = f_vizinho
                
                # Melhor solução
                if f_vizinho < f_melhor:
                    melhor_solucao = vizinho[:]
                    f_melhor = f_vizinho
                    
            else:
                if random.uniform(0, 1) < math.exp(-delta / T):
                    solucao_atual = vizinho[:]
                    f_atual = f_vizinho

            # Guarda para gráfico
            historico_f_objetivo.append(f_atual)
                    
            # Guarda para gráfico
            historico_temperatura.append(T)
            T = coeficiente_temperatura_logistica(T0, 1, iteracoes, itMax)

    return melhor_solucao, f_melhor, historico_f_objetivo, historico_temperatura


if __name__ == "__main__":
    arquivo_instancia = 'uf250-01.cnf'  # caminho
    clausulas, numeroLiterais = ler_instancia(arquivo_instancia)
    T0 = 10000
    itMax = 80000
    t = 1
    SAmAx = 1000

    solucao_final, valor_otimo, historico_f_objetivo, historico_temperatura = simulated_annealing(clausulas, numeroLiterais, T0, itMax, t, SAmAx)
    
    #print(f"Solucao otima: {solucao_final}")
    print(f"Número de cláusulas não satisfeitas: {valor_otimo}")
    
    # Plotar o gráfico de convergência
    plt.figure(figsize=(12, 5))

    # Gráfico 1: Convergência do Simulated Annealing
    plt.plot(historico_f_objetivo)
    plt.title('Convergência do SA')
    plt.xlabel('Iteracoes')
    plt.ylabel('Numero de clausulas nao satisfeitas')
    plt.grid(True)
    
    plt.savefig('simulated_annealing_convergence.png')
    #plt.show()

    # Gráfico 2: Queda da temperatura
    plt.plot(historico_temperatura)
    plt.title('Queda de temperatura durante SA')
    plt.xlabel('Iteracoes')
    plt.ylabel('Temperatura')
    plt.grid(True)

    plt.savefig('simulated_annealing_temperatura.png')
    #plt.show()


