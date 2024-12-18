import os
import random
import threading
import time
import math

class Comida:
    def __init__(self, x, y, grupo):
        self.valores = [float(x), float(y)]
        self.grupo = grupo
        self.simbolo = self.definir_simbolo()

    def definir_simbolo(self):
        if 0 <= (self.grupo + 64) <= 127:
            return chr(self.grupo + 64)  # simbolo correspondente da tabela asc
        else:
            return " "
        
    def get_valores(self):
        return self.valores

class Formiga(threading.Thread):
    def __init__(self, matriz_movimento, matriz_comida, posicao_inicial, raio_visao, id_formiga, lock, alfa, k1, k2):
        threading.Thread.__init__(self)
        self.matriz_movimento = matriz_movimento
        self.matriz_comida = matriz_comida
        self.posicao = posicao_inicial
        self.raio_visao = raio_visao
        self.id_formiga = id_formiga
        self.carregando = None
        self.lock = lock
        self.viva = True
        self.alfa = alfa
        self.k1 = k1
        self.k2 = k2

    def mover(self):
        x, y = self.posicao
        movimentos_possiveis = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        movimentos_validos = [(nx, ny) for nx, ny in movimentos_possiveis if 0 <= nx < len(self.matriz_movimento) and 0 <= ny < len(self.matriz_movimento[0])]

        if movimentos_validos:
            nova_posicao = random.choice(movimentos_validos)

            with self.lock:
                if self.matriz_movimento[nova_posicao[0]][nova_posicao[1]] == None:  # Se a célula estiver livre de formigas
                    self.matriz_movimento[x][y] = None  # Liberar a célula anterior
                    self.matriz_movimento[nova_posicao[0]][nova_posicao[1]] = "*"  # Ocupa nova posição
                    self.posicao = nova_posicao

            ######################################
            #gargalo de execução em background
            time.sleep(random.uniform(0.01, 0.01))
            ######################################

    def calcular_distancia_euclidiana(self, p1, p2):
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def contar_distancias_vizinhanca(self):
        distancias = []
        x, y = self.posicao
        if(isinstance(self.carregando, Comida)):
            valores_Posicao_Atual = self.carregando.get_valores()
        else:
            #caso nao esteja carregando nada, a disparidade é a igual para todos, eu fiz que a posicao atual é (0,0)
            valores_Posicao_Atual = (0,0)#certo?
        
        x_min = max(0, x - self.raio_visao)
        x_max = min(len(self.matriz_comida), x + self.raio_visao+1)
        y_min = max(0, y - self.raio_visao)
        y_max = min(len(self.matriz_comida[0]), y + self.raio_visao+1)
        for i in range(x_min, x_max):
            for j in range(y_min, y_max):
                if (i, j) != (x, y) and isinstance(self.matriz_comida[i][j], Comida):
                    valorObservado = self.matriz_comida[i][j].get_valores()
                    dist = self.calcular_distancia_euclidiana(valores_Posicao_Atual, valorObservado)
                    distancias.append(dist)

        if distancias:
            soma = 0
            for i in distancias:
                soma = soma + (1-i/self.alfa) 
            return soma  # Retorna a distância média
        return 0  # Se não houver vizinhos

    def contar_comida_vizinhanca(self):
        contadorItens = 0
        x, y = self.posicao
        # Define os limites do raio de visão, garantindo que não saímos da matriz
        x_min = max(0, x - self.raio_visao)
        x_max = min(len(self.matriz_comida), x + self.raio_visao+1)
        y_min = max(0, y - self.raio_visao)
        y_max = min(len(self.matriz_comida[0]), y + self.raio_visao+1)

        # Percorre as células ao redor
        for i in range(x_min, x_max):
            for j in range(y_min, y_max):
                if (i, j) != (x, y) and isinstance(self.matriz_comida[i][j], Comida):
                    contadorItens += 1
        return contadorItens

    def acao(self):
        #largar
        if self.carregando:
            if not isinstance(self.matriz_comida[self.posicao[0]][self.posicao[1]], Comida):
                if(self.contar_comida_vizinhanca()!=0):
                    f_i = self.contar_distancias_vizinhanca()/(self.contar_comida_vizinhanca()**2)
                    chanceLargar = (self.k1/(self.k1+f_i))**2  
                else:
                    #print("nenhuma comida proxima")
                    chanceLargar = 0
                numero_aleatorio = random.random()
                if numero_aleatorio < chanceLargar:
                    self.matriz_comida[self.posicao[0]][self.posicao[1]] = self.carregando
                    self.carregando = None
                    #print("largou: ", self.matriz_comida[self.posicao[0]][self.posicao[1]])
        #pegar
        else:
            if isinstance(self.matriz_comida[self.posicao[0]][self.posicao[1]], Comida):
                if(self.contar_comida_vizinhanca()!=0):
                    f_i = self.contar_distancias_vizinhanca()/(self.contar_comida_vizinhanca()**2)
                    chancePegar = (f_i/(self.k2+f_i))**2
                    
                else:
                    #print("nenhuma comida proxima")
                    chancePegar = 1
                numero_aleatorio = random.random()
                if numero_aleatorio < chancePegar:
                    self.carregando = self.matriz_comida[self.posicao[0]][self.posicao[1]]
                    self.matriz_comida[self.posicao[0]][self.posicao[1]] = None
                    #print("pegou: ", self.carregando)

    def run(self):
        while self.viva:
            self.acao()
            self.mover()

def gerar_matriz(linhas, colunas):
    return [[None for _ in range(colunas)] for _ in range(linhas)]

def normalizar_dados(lista_comidas):
    """ Normaliza os valores x e y de uma lista de objetos Comida """
    min_x = min(comida.valores[0] for comida in lista_comidas)
    max_x = max(comida.valores[0] for comida in lista_comidas)
    min_y = min(comida.valores[1] for comida in lista_comidas)
    max_y = max(comida.valores[1] for comida in lista_comidas)

    for comida in lista_comidas:
        comida.valores[0] = (comida.valores[0] - min_x) / (max_x - min_x)  # Normaliza x
        comida.valores[1] = (comida.valores[1] - min_y) / (max_y - min_y)  # Normaliza y
    return lista_comidas

def ler_dados_arquivo(nome_arquivo):
    lista_comidas = []
    with open(nome_arquivo, 'r') as arquivo:
        for linha in arquivo:
            dados = linha.strip().split()
            if len(dados) == 3:
                x, y, grupo = float(dados[0]), float(dados[1]), int(dados[2])
                lista_comidas.append(Comida(x, y, grupo))

    lista_comidas = normalizar_dados(lista_comidas)

    return lista_comidas

def distribuir_comida(matriz, lista_comidas):
    linhas = len(matriz)
    colunas = len(matriz[0])

    for comida in lista_comidas:
        i = random.randint(0, linhas - 1)
        j = random.randint(0, colunas - 1)
        matriz[i][j] = comida

def gerar_formigas(matriz_movimento, matriz_comida, num_formigas, raio_visao, alfa, k1, k2):
    linhas = len(matriz_movimento)
    colunas = len(matriz_movimento[0])
    posicoes_livres = [(i, j) for i in range(linhas) for j in range(colunas) if matriz_movimento[i][j] == None]

    if num_formigas > len(posicoes_livres):
        raise ValueError("Não há espaço suficiente na matriz para todas as formigas.")

    formigas = []
    lock = threading.Lock()

    for id_formiga in range(num_formigas):
        posicao_inicial = random.choice(posicoes_livres)
        posicoes_livres.remove(posicao_inicial)
        matriz_movimento[posicao_inicial[0]][posicao_inicial[1]] = "*"  # Posição inicial da formiga
        formiga = Formiga(matriz_movimento, matriz_comida, posicao_inicial, raio_visao, id_formiga, lock, alfa, k1, k2)
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
    matriz_combinada = [[' ' for _ in range(len(matriz_comida[0]))] for _ in range(len(matriz_comida))]
    
    for i in range(len(matriz_comida)):
        for j in range(len(matriz_comida[0])):
            if matriz_movimento[i][j] == "*":
                matriz_combinada[i][j] = "*"
            elif isinstance(matriz_comida[i][j], Comida):
                matriz_combinada[i][j] = matriz_comida[i][j].simbolo
            else:
                matriz_combinada[i][j] = " "

    for linha in matriz_combinada:
        print(''.join(linha))

def salvar_matriz_em_arquivo(matriz, nome_arquivo):
    with open(nome_arquivo, 'w') as f:
        for linha in matriz:
            for elemento in linha:
                if isinstance(elemento, Comida):
                    f.write(elemento.simbolo)
                else:
                    f.write(' ')
            f.write('\n')

def simular(linhas, colunas, num_formigas, duracao_simulacao, intervalo_atualizacao, raio_visao, alfa, k1, k2, arquivo_dados):
    matriz_comida = gerar_matriz(linhas, colunas)
    matriz_movimento = gerar_matriz(linhas, colunas)
    lista_comidas = ler_dados_arquivo(arquivo_dados)
    distribuir_comida(matriz_comida, lista_comidas)

    formigas = gerar_formigas(matriz_movimento, matriz_comida, num_formigas, raio_visao, alfa, k1, k2)

    salvar_matriz_em_arquivo(matriz_comida, 'matriz_15_comida_0_quartos.txt')

    try:
        for i in range(duracao_simulacao):
            #limpar_terminal()
            #print("")
            #imprimir_matriz_combinada(matriz_comida, matriz_movimento)
            #time.sleep(intervalo_atualizacao)

            if i == duracao_simulacao//4:
                salvar_matriz_em_arquivo(matriz_comida, 'matriz_15_comida_1_quartos.txt')
            if i == duracao_simulacao//2:
                salvar_matriz_em_arquivo(matriz_comida, 'matriz_15_comida_2_quartos.txt')
            if i == (3*duracao_simulacao//4):
                salvar_matriz_em_arquivo(matriz_comida, 'matriz_15_comida_3_quartos.txt')
            #continue
    finally:
        parar_formigas(formigas)
        salvar_matriz_em_arquivo(matriz_comida, 'matriz_15_comida_4_quartos.txt')

linhas = 30
colunas = 80
num_formigas = 20
intervalo_atualizacao = 0.1
duracao_simulacao = 8000000000  # iteracoes
raio_visao = 2
alfa = 0.08
k1 = 0.1
k2 = 0.9
arquivo_dados = 'dados_15Grupos.txt'

simular(linhas, colunas, num_formigas, duracao_simulacao, intervalo_atualizacao, raio_visao, alfa, k1, k2, arquivo_dados)
