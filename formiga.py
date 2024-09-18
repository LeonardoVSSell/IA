import os
import random
import threading
import time


class Formiga(threading.Thread):
    def __init__(self, matriz_movimento, posicao_inicial, raio_visao, id_formiga, lock, matriz_comida):
        threading.Thread.__init__(self)
        self.matriz_movimento = matriz_movimento
        self.matriz_comida = matriz_comida
        self.posicao = posicao_inicial
        self.raio_visao = raio_visao
        self.id_formiga = id_formiga
        self.carregando = False
        self.lock = lock
        self.viva = True

    def mover(self):prob_pickup = 0
        while self.viva:
            x, y = self.posicao
            movimentos_possiveis = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
            movimentos_validos = [(nx, ny) for nx, ny in movimentos_possiveis if 0 <= nx < len(self.matriz_movimento) and 0 <= ny < len(self.matriz_movimento[0])]

            if not movimentos_validos:
                continue

            nova_posicao = random.choice(movimentos_validos)

            with self.lock:
                if self.matriz_movimento[nova_posicao[0]][nova_posicao[1]] == 0:  # Se a célula estiver livre de formigas
                    self.matriz_movimento[x][y] = 0  # Liberar a célula anterior
                    self.matriz_movimento[nova_posicao[0]][nova_posicao[1]] = "*"  # Ocupa nova posição
                    self.posicao = nova_posicao

      

            time.sleep(random.uniform(0.1, 0.1))


        def verificaItem(self):
            print('a')
             #Função de verificação de pegar/largar item com formiga.
                # SE ESTOU NUMA CÉLULA VAZIA
                    #Se não estou carregando algo:
                        # ME MOVO.
            if (self.viva == True and self.carregando == False and self.matriz_comida[self.posicao[0]][self.posicao[1]] == 0): #CÉLULA VAZIA + nada
                exit()
    
            #Estou carregando alguma coisa:
                # Usar raio de percepção para ver se largo ou não (agrupamento)
                # ME MOVO.
            
            if (self.viva == True and self.carregando == True and self.matriz_comida[self.posicao[0]][self.posicao[1]] == 0): #CÉLULA VAZIA + carregando
                # RAIO DE PERCEPÇÃO = verificar adjacência do ponto atual da matriz
                contadorItens = 0
                for x in range (-2,2):#verificação de todos os lados
                    if self.matriz_comida[self.posicao[0 + x][self.posicao[1+x]]] == 1: 
                        #contador
                        contadorItens += 1
                        self.carregando = True
                        self.matriz_comida[self.posicao[0 + x][self.posicao[1+x]]] = 0
                prob_ficarComItem = 1 - contadorItens/(self.raio_visao * 8)
                chanceDrop = randrange()
                if  (): #verificação se larga
                    #Larga a comida na posição
                    #Move


                # SE ESTOU NUMA CÉLULA COM ALGUMA COISA
                    #Se estou carregando alguma coisa:
                        # ME MOVO.
                    #Se não estou carregando alguma coisa:
                        # Usar o raio de percepção para ver se pego ou não.
                        # ME MOVO.



    def run(self):

        self.verificaItem()
        self.mover()

def gerar_matriz(linhas, colunas):
    return [[0 for _ in range(colunas)] for _ in range(linhas)]

def distribuir_uns(matriz, num_uns):
    linhas = len(matriz)
    colunas = len(matriz[0])
    total_celulas = linhas * colunas

    if num_uns > total_celulas:
        raise ValueError("Número de '1s' excede o número de células na matriz.")

    posicoes = [(i, j) for i in range(linhas) for j in range(colunas)]
    posicoes_escolhidas = random.sample(posicoes, num_uns)

    for i, j in posicoes_escolhidas:
        matriz[i][j] = 1

def gerar_formigas(matriz_movimento, num_formigas, raio_visao, matriz_comida):
    linhas = len(matriz_movimento)
    colunas = len(matriz_movimento[0])
    posicoes_livres = [(i, j) for i in range(linhas) for j in range(colunas) if matriz_movimento[i][j] == 0]

    if num_formigas > len(posicoes_livres):
        raise ValueError("Não há espaço suficiente na matriz para todas as formigas.")

    formigas = []
    lock = threading.Lock()

    for id_formiga in range(num_formigas):
        posicao_inicial = random.choice(posicoes_livres)
        posicoes_livres.remove(posicao_inicial)
        matriz_movimento[posicao_inicial[0]][posicao_inicial[1]] = "*"  # Posição inicial da formiga
        
        formiga = Formiga(matriz_movimento, posicao_inicial, raio_visao, id_formiga, lock, matriz_comida)
        formigas.append(formiga)

    for formiga in formigas:
        formiga.start()

    return formigas

def parar_formigas(formigas):
    for formiga in formigas:
        formiga.viva = False
        formiga.join()

def limpar_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def imprimir_matriz_combinada(matriz_comida, matriz_movimento):
    matriz_combinada = [[0 for _ in range(len(matriz_comida[0]))] for _ in range(len(matriz_comida))]
    
    for i in range(len(matriz_comida)):
        for j in range(len(matriz_comida[0])):
            if matriz_movimento[i][j] == "*":  # Se há uma formiga, sobrepõe a célula com o valor *
                matriz_combinada[i][j] = "*"
            else:
                matriz_combinada[i][j] = matriz_comida[i][j]  # Mantém o valor original da comida

    for linha in matriz_combinada:
        print(' '.join(map(str, linha)))

def simular(linhas, colunas, num_formigas, num_comida, duracao_simulacao, intervalo_atualizacao):
    matriz_comida = gerar_matriz(linhas, colunas)
    matriz_movimento = gerar_matriz(linhas, colunas)
    distribuir_uns(matriz_comida, num_comida)

    formigas = gerar_formigas(matriz_movimento, num_formigas, raio_visao=1, matriz_comida)

    try:
        for _ in range(duracao_simulacao):
            limpar_terminal()
            ##print("\n")
            imprimir_matriz_combinada(matriz_comida, matriz_movimento)
            time.sleep(intervalo_atualizacao)
    finally:
        parar_formigas(formigas)

linhas = 20
colunas = 50
num_formigas = 20
num_comida = 150
duracao_simulacao = 100  # iteracoes
intervalo_atualizacao = 0.1

simular(linhas, colunas, num_formigas, num_comida, duracao_simulacao, intervalo_atualizacao)
