import os
import random
import math
import matplotlib.pyplot as plt
import numpy as np
from math import exp, log, cos, cosh, tanh, pi

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

def func0(T0: int, it: int, TN:int, itMax:int) -> float:
    """Função de resfriamento 0"""
    return T0 - (it * ((T0 - TN)/itMax))

def func1(T0: int, it: int, TN:int, itMax:int) -> float:
    """Função de resfriamento 1"""
    return T0 * ((TN/T0)**(it/itMax))

def func2(T0: int, it: int, TN:int, itMax:int) -> float:
    """Função de resfriamento 2"""
    a = ((T0 - TN) * (itMax + 1))/itMax
    return (a/(it+1))+ (T0 - a)

def func3(T0: int, it: int, TN:int, itMax:int) -> float:
    """Função de resfriamento 3"""
    a = log(T0 - TN)/log(itMax)
    return T0 - it**a

def func4(T0: int, it: int, TN:int, itMax:int) -> float:
    """Função de resfriamento 4 com controle de overflow"""
    exp_argument = 0.3 * (it - (itMax / 2))
    
    # Limitar o argumento da exponencial para evitar overflow
    if exp_argument > 700:
        exp_argument = 700
    elif exp_argument < -700:
        exp_argument = -700
    
    return ((T0 - TN) / (1 + exp(exp_argument))) + TN

def func5(T0: int, it: int, TN:int, itMax:int) -> float:
    """Função de resfriamento 5"""
    return (0.5*(T0-TN)*(1+cos((it*pi)/itMax))) + TN

def func6(T0: int, it: int, TN:int, itMax:int) -> float:
    """Função de resfriamento 6"""
    return 0.5*(T0-TN)*(1-tanh((10.0*it/itMax)-5.0)) + TN

def func7(T0: int, it: int, TN:int, itMax:int) -> float:
    """Função de resfriamento 7"""
    exp_argument = (10*it)/itMax
    
    # Limitar o argumento da exponencial para evitar overflow
    if exp_argument > 700:
        exp_argument = 700
    elif exp_argument < -700:
        exp_argument = -700
    
    return ((T0 - TN) / cosh(exp_argument)) + TN

def func8(T0: int, it: int, TN:int, itMax:int) -> float:
    """Função de resfriamento 8"""
    a = -1*((it/itMax)*log(T0/TN))
    return T0*exp(a*it)

def func9(T0: int, it: int, TN:int, itMax:int) -> float:
    """Função de resfriamento 9"""
    a = -1*((1/itMax**2)*log(T0/TN))
    return T0*exp(a*it**2)

def func10(T0, it, TN, itMax):
    # Parâmetros para controlar a forma da curva sigmoidal
    midpoint = itMax / 3  # Ponto médio das iterações onde a transição ocorre
    steepness = 100  # Ajusta a inclinação da transição; aumente para uma queda mais abrupta

    # Função logística para controlar a temperatura
    return TN + (T0 - TN) / (1+ math.exp((it - midpoint) / (itMax / steepness)))

def simulated_annealing(clausulas, n_variaveis, T0, itMax, t, SAmAx, cont):
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
            if cont==0:
                #print(f"entrando na funcao {i}")
                T = func0(T0, iteracoes, 1 , itMax)
            if cont==1:
                #print(f"entrando na funcao {i}")
                T = func1(T0, iteracoes, 1 , itMax)
            elif cont==2:
                #print(f"entrando na funcao {i}")
                T = func2(T0, iteracoes, 1 , itMax)
            elif cont==3:
                #print(f"entrando na funcao {i}")
                T = func3(T0, iteracoes, 1 , itMax)
            elif cont==4:
                #print(f"entrando na funcao {i}")
                T = func4(T0, iteracoes, 1 , itMax)
            elif cont==5:
                #print(f"entrando na funcao {i}")
                T = func5(T0, iteracoes, 1 , itMax)
            elif cont==6:
                #print(f"entrando na funcao {i}")
                T = func6(T0, iteracoes, 1 , itMax)
            elif cont==7:
                #print(f"entrando na funcao {i}")
                T = func7(T0, iteracoes, 1 , itMax)
            elif cont==8:
                #print(f"entrando na funcao {i}")
                T = func8(T0, iteracoes, 1 , itMax)
            elif cont==9:
                #print(f"entrando na funcao {i}")
                T = func9(T0, iteracoes, 1 , itMax)
            elif cont==10:
                #print(f"entrando na funcao {i}")
                T = func10(T0, iteracoes, 1 , itMax)
                

    return melhor_solucao, f_melhor, historico_f_objetivo, historico_temperatura


if __name__ == "__main__":
    T0 = 10000
    itMax = 80000
    t = 1
    SAmAx = 1000
    entradas = [
        ('uf20-01.cnf', 'uf20'),
        ('uf100-01.cnf', 'uf100'),
        ('uf250-01.cnf', 'uf250')
    ]
    repeticoes = 10

    for arquivo_instancia, pasta_saida in entradas:
        # Crie a pasta de saída, se não existir
        os.makedirs(pasta_saida, exist_ok=True)
        
        # Carregue as cláusulas e literais do arquivo de entrada atual
        clausulas, numeroLiterais = ler_instancia(arquivo_instancia)

        for i in range(11):
            if i not in {0, 1, 3, 5, 6, 7, 9}:
                
                
                historicos_f_objetivo = []
                melhor_solucao = 1065
                melhor_objetivo = []
                
                for _ in range(repeticoes):
                    # Execute o simulated annealing
                    solucao_final, valor_otimo, historico_f_objetivo, historico_temperatura = simulated_annealing(
                        clausulas, numeroLiterais, T0, itMax, t, SAmAx, i
                    )
                    historicos_f_objetivo.append(historico_f_objetivo)
                    if solucao_final<melhor_solucao:
                        melhor_solucao = solucao_final
                        melhor_objetivo = historico_f_objetivo


                    # Calcula média e desvio padrão para cada ponto de iteração
                    medias_f_objetivo = np.mean(historicos_f_objetivo, axis=0)
                    desvios_f_objetivo = np.std(historicos_f_objetivo, axis=0)

                    # Salvar gráfico de média de convergência com desvio padrão
                    plt.figure(figsize=(12, 5))
                    plt.plot(medias_f_objetivo, label='Média')
                    plt.fill_between(range(len(medias_f_objetivo)),
                                    medias_f_objetivo - desvios_f_objetivo,
                                    medias_f_objetivo + desvios_f_objetivo,
                                    color='b', alpha=0.2, label='Desvio padrão')
                    plt.title(f'Convergência média do SA - Função {i}')
                    plt.xlabel('Iterações')
                    plt.ylabel('Número médio de cláusulas não satisfeitas')
                    plt.legend()
                    plt.grid(True)
                    plt.savefig(os.path.join(pasta_saida, f'SA_convergence_avg_std_{i}.png'))
                    plt.close()

                # Salvar o gráfico de convergência para a função atual
                plt.figure(figsize=(12, 5))
                plt.plot(melhor_objetivo)
                plt.title(f'Convergência do melhor SA - Função {i}')
                plt.xlabel('Iterações')
                plt.ylabel('Número de cláusulas não satisfeitas')
                plt.grid(True)
                plt.savefig(os.path.join(pasta_saida, f'SA_convergence_{i}.png'))

                print(f"Arquivo: {arquivo_instancia}, Função de resfriamento: {i}")
                print(f"Valor médio de cláusulas não-resolvidas: {min(medias_f_objetivo)}")
                print(f"Desvio Padrao de cláusulas não-resolvidas: {min(desvios_f_objetivo)}")
                print("\n")