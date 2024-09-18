import os
import random
import threading
import time

class Formiga(threading.Thread):
    def __init__(self, matriz_movimento, matriz_comida, posicao_inicial, raio_visao, id_formiga, lock):
        threading.Thread.__init__(self)
        self.matriz_movimento = matriz_movimento
        self.matriz_comida = matriz_comida
        self.posicao = posicao_inicial
        self.raio_visao = raio_visao
        self.id_formiga = id_formiga
        self.carregando = False
        self.lock = lock
        self.viva = True

    def mover(self):
        x, y = self.posicao
        movimentos_possiveis = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        movimentos_validos = [(nx, ny) for nx, ny in movimentos_possiveis if 0 <= nx < len(self.matriz_movimento) and 0 <= ny < len(self.matriz_movimento[0])]

        if movimentos_validos:    

            nova_posicao = random.choice(movimentos_validos)

            with self.lock:
                if self.matriz_movimento[nova_posicao[0]][nova_posicao[1]] == 0:  # Se a célula estiver livre de formigas
                    self.matriz_movimento[x][y] = 0  # Liberar a célula anterior
                    self.matriz_movimento[nova_posicao[0]][nova_posicao[1]] = "*"  # Ocupa nova posição
                    self.posicao = nova_posicao

            time.sleep(random.uniform(0.1, 0.1))

    def contar_comida_vizinhanca(self):
        contadorItens = 0
        x, y = self.posicao
        # Define os limites do raio de visão, garantindo que não saímos da matriz
        x_min = max(0, x - self.raio_visao)
        x_max = min(len(self.matriz_comida), x + self.raio_visao + 1)
        y_min = max(0, y - self.raio_visao)
        y_max = min(len(self.matriz_comida[0]), y + self.raio_visao + 1)

        # Percorre as células ao redor
        for i in range(x_min, x_max):
            for j in range(y_min, y_max):
                if (i, j) != (x, y):  # Não conta a posição da formiga
                    contadorItens += self.matriz_comida[i][j]

        return contadorItens

    def acao(self):
            #print(f"Formiga: {self.id_formiga}")
            #print(self.posicao)
            #print(self.matriz_comida[self.posicao[0]][self.posicao[1]])
            
            if self.carregando:
                if (self.matriz_comida[self.posicao[0]][self.posicao[1]] == 0):
                    contadorComida = self.contar_comida_vizinhanca()
                    chanceLargar = contadorComida/((2*self.raio_visao)*(2*self.raio_visao)-1)
                    numero_aleatorio = random.random()
                    #if(True):
                    if(numero_aleatorio<chanceLargar):
                        self.carregando=False
                        self.matriz_comida[self.posicao[0]][self.posicao[1]] = 1
                        #print("largou")
            else:
                if (self.matriz_comida[self.posicao[0]][self.posicao[1]] == 1):
                    contadorComida = self.contar_comida_vizinhanca()
                    chancePegar = 1-(contadorComida/((2*self.raio_visao)*(2*self.raio_visao)-1))
                    numero_aleatorio = random.random()
                    #if(True):
                    if(numero_aleatorio<chancePegar):
                        self.carregando=True
                        self.matriz_comida[self.posicao[0]][self.posicao[1]] = 0
                        #print("pegou")
            #print()

    def run(self):
        while self.viva:
            self.acao()
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

def gerar_formigas(matriz_movimento, matriz_comida, num_formigas, raio_visao):
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
        formiga = Formiga(matriz_movimento, matriz_comida, posicao_inicial, raio_visao, id_formiga, lock)
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
        for elemento in linha:
            if elemento == 1:
                print(".", end="")
            elif elemento == '*':
                print("*", end="")
            else:
                print(" ", end="")
        print()
        #print(' '.join(map(str, linha)))

def salvar_matriz_em_arquivo(matriz, nome_arquivo):
    with open(nome_arquivo, 'w') as f:
        for linha in matriz:
            for elemento in linha:
                if elemento == 1:
                    f.write('.')
                else:
                    f.write(' ')
            f.write('\n')

def simular(linhas, colunas, num_formigas, num_comida, duracao_simulacao, intervalo_atualizacao, raio_visao):
    matriz_comida = gerar_matriz(linhas, colunas)
    matriz_movimento = gerar_matriz(linhas, colunas)
    distribuir_uns(matriz_comida, num_comida)

    formigas = gerar_formigas(matriz_movimento, matriz_comida, num_formigas, raio_visao)

    salvar_matriz_em_arquivo(matriz_comida, 'matriz_comida_inicio.txt')

    try:
        for _ in range(duracao_simulacao):
            limpar_terminal()
            ##print("\n")
            imprimir_matriz_combinada(matriz_comida, matriz_movimento)
            time.sleep(intervalo_atualizacao)
    finally:
        parar_formigas(formigas)
        salvar_matriz_em_arquivo(matriz_comida, 'matriz_comida_fim.txt')

linhas = 20
colunas = 60
num_formigas = 10
num_comida = 150
duracao_simulacao = 1000  # iteracoes
intervalo_atualizacao = 0.1
raio_visao = 1

simular(linhas, colunas, num_formigas, num_comida, duracao_simulacao, intervalo_atualizacao, raio_visao)
