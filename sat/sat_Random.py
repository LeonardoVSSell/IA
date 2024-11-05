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

def random_search(clausulas, n_variaveis, T0, itMax, t, SAmAx):
    # Solução aleatória inicial
    solucao_atual = gerar_solucao_aleatoria(n_variaveis)
    melhor_valor = solucao_atual[:]
    
    # Avalia a função objetivo para a solução inicial
    f_melhor = calcular_clausulas_nao_satisfeitas(clausulas, solucao_atual)
    
    historico_f_objetivo = [f_melhor]
    
    # Repita até atingir o limite de iterações
    for _ in range(itMax):
        # Gera uma nova solução aleatória
        nova_solucao = gerar_solucao_aleatoria(n_variaveis)
        f_nova = calcular_clausulas_nao_satisfeitas(clausulas, nova_solucao)
        
        # Se a nova solução for melhor, atualiza a melhor solução
        if f_nova < f_melhor:
            melhor_valor = nova_solucao[:]
            f_melhor = f_nova
        
        # Guarda a função objetivo atual para análise
        historico_f_objetivo.append(f_nova)
    
    return melhor_valor, f_melhor, historico_f_objetivo

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
    
        historicos_f_objetivo = []
        historicos_temperatura = []
        melhor_valor = 1065
        melhor_objetivo = []
        solucao_otima = []
        
        for _ in range(repeticoes):
            # Execute o simulated annealing
            solucao_final, valor_otimo, historico_f_objetivo = random_search(
                clausulas, numeroLiterais, T0, itMax, t, SAmAx
            )
            historicos_f_objetivo.append(historico_f_objetivo)
            #print(valor_otimo)
            #print(melhor_valor)
            if valor_otimo < melhor_valor:
                melhor_valor = valor_otimo
                melhor_objetivo = historico_f_objetivo
                solucao_otima = solucao_final


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
            plt.title(f'Convergência média do RS - Função 0')
            plt.xlabel('Iterações')
            plt.ylabel('Número médio de cláusulas não satisfeitas')
            plt.legend()
            plt.grid(True)
            plt.savefig(os.path.join(pasta_saida, f'RS_convergence_avg_std_0.png'))
            plt.close()

        # Salvar o gráfico de convergência para a função atual
        plt.figure(figsize=(12, 5))
        plt.plot(melhor_objetivo)
        plt.title(f'Convergência do melhor RS - Função 0')
        plt.xlabel('Iterações')
        plt.ylabel('Número de cláusulas não satisfeitas')
        plt.grid(True)
        plt.savefig(os.path.join(pasta_saida, f'RS_convergence_0.png'))
        plt.close()

        print(f"Arquivo: {arquivo_instancia}")
        print(f"Valor médio de cláusulas não-resolvidas: {min(medias_f_objetivo)}")
        print(f"Desvio Padrao de cláusulas não-resolvidas: {min(desvios_f_objetivo)}")
        print(f"Clausulas nao resolvidas: {melhor_valor}")
        print(f"Solucao: {solucao_otima}")        
        print("\n")