import numpy as np
import matplotlib.pyplot as plt
import time  # tempo

DIMENSIONS = 10
B_LO, B_HI = -32.0, 32.0  # limites das dimensoes
POPULATION = 20
GLOBAL_BEST = 0.0 #alvo
V_MAX = 0.1  # Velocidade max
PERSONAL_C = 2.05
SOCIAL_C = 2.05
MAX_ITER = 7000
RUNS = 10  # N execucoes

CONVERGENCE = 0.000000000000001#convergencia

#pesos e fator
W_INIT = 1.5
W_FINAL = 0.1
PHI = PERSONAL_C + SOCIAL_C
CONSTRICTION_FACTOR = 2 / abs(2 - PHI - np.sqrt(PHI ** 2 - 4 * PHI))
CASE = 2 #Griewank ou Ackley

#funcao de custo
def cost_function(pos):
    if CASE == 1:  # Griewank
        top1 = np.sum((pos ** 2)/4000)
        top2 = np.prod(np.cos((pos / np.sqrt(np.arange(1, len(pos) + 1))) * np.pi / 180))
        return (1 / 4000.0) * top1 - top2 + 1
    elif CASE == 2:  # Ackley
        aux = np.sum(pos ** 2)
        aux1 = np.sum(np.cos(2.0 * np.pi * pos))
        return (-20.0 * np.exp(-0.2 * np.sqrt(aux / len(pos))) -
                np.exp(aux1 / len(pos)) + 20.0 + np.exp(1))
    else:
        raise ValueError("Caso inválido. Escolha 1 (Griewank) ou 2 (Ackley).")

class Particle:
    def __init__(self, dimensions):
        self.pos = np.random.uniform(B_LO, B_HI, dimensions)
        self.velocity = np.random.uniform(-V_MAX, V_MAX, dimensions)
        self.best_pos = self.pos.copy()
        self.best_pos_z = cost_function(self.pos)
        self.pos_z = self.best_pos_z

    def update_velocity(self, global_best_pos, inertia_weight):
        r1, r2 = np.random.random(DIMENSIONS), np.random.random(DIMENSIONS)
        cognitive = PERSONAL_C * r1 * (self.best_pos - self.pos)
        social = SOCIAL_C * r2 * (global_best_pos - self.pos)
        self.velocity = CONSTRICTION_FACTOR * (inertia_weight * self.velocity + cognitive + social)
        self.velocity = np.clip(self.velocity, -V_MAX, V_MAX)

    def update_position(self):
        self.pos += self.velocity
        self.pos = np.clip(self.pos, B_LO, B_HI)
        self.pos_z = cost_function(self.pos)
        if self.pos_z < self.best_pos_z:
            self.best_pos = self.pos.copy()
            self.best_pos_z = self.pos_z

class Swarm:
    def __init__(self, population, dimensions):
        self.particles = [Particle(dimensions) for _ in range(population)]
        self.best_pos = min(self.particles, key=lambda p: p.best_pos_z).best_pos
        self.best_pos_z = min(p.best_pos_z for p in self.particles)

    def update(self, inertia_weight):
        for particle in self.particles:
            particle.update_velocity(self.best_pos, inertia_weight)
            particle.update_position()

        best_particle = min(self.particles, key=lambda p: p.best_pos_z)
        if best_particle.best_pos_z < self.best_pos_z:
            self.best_pos = best_particle.best_pos
            self.best_pos_z = best_particle.best_pos_z

def particle_swarm_optimization(inertia_weight_func):
    swarm = Swarm(POPULATION, DIMENSIONS)
    iterations_data = []

    for iter_num in range(MAX_ITER):
        inertia_weight = inertia_weight_func(iter_num)
        swarm.update(inertia_weight)

        avg_pos_z = np.mean([p.pos_z for p in swarm.particles])
        iterations_data.append((iter_num, swarm.best_pos_z, avg_pos_z))

        if abs(swarm.best_pos_z - GLOBAL_BEST) < CONVERGENCE:
            print(f"Convergência atingida em {iter_num} iterações.")
            break

    print(f"fim das iteracoes, valor obtido: {swarm.best_pos_z}")   
    return iterations_data, swarm.best_pos_z

def run_experiments(version):
    all_best_values = []
    all_iterations_data = []

    if version == "simple":
        inertia_weight_func = lambda iter_num: 1
    elif version == "weights":
        inertia_weight_func = lambda iter_num: W_INIT - (W_INIT - W_FINAL) * (iter_num / MAX_ITER)
    elif version == "weights_and_constriction":
        inertia_weight_func = lambda iter_num: CONSTRICTION_FACTOR * (W_INIT - (W_INIT - W_FINAL) * (iter_num / MAX_ITER))
    else:
        raise ValueError("Versão inválida")

    for _ in range(RUNS):
        iterations_data, best_value = particle_swarm_optimization(inertia_weight_func)
        all_iterations_data.append(iterations_data)
        all_best_values.append(best_value)

    return all_best_values, all_iterations_data

#boxplots
def plot_boxplots(results, filename):
    labels = list(results.keys())
    data = list(results.values())

    plt.figure(figsize=(10, 6))
    plt.boxplot(data, labels=labels)
    plt.ylabel("Melhor Valor (log)")
    plt.yscale('log')
    plt.title("Comparação de Desempenho - PSO")
    plt.grid()
    plt.savefig(filename)
    plt.show()

def plot_convergence(data, filename, version):
    max_iters = max(len(run) for run in data)

    #padronizar para o mesmo comprimento
    padded_data = []
    for run in data:
        padded_run = list(run)
        last_value = run[-1] if len(run) > 0 else (0, float('inf'), float('inf'))
        while len(padded_run) < max_iters:
            padded_run.append(last_value)
        padded_data.append(np.array(padded_run))

    iterations = range(max_iters)
    avg_best_values = np.mean([run[:, 1] for run in padded_data], axis=0)
    avg_values = np.mean([run[:, 2] for run in padded_data], axis=0)

    plt.figure(figsize=(10, 6))
    plt.plot(iterations, avg_best_values, label="Melhor Valor (Global)", color="red", linewidth=2)
    plt.plot(iterations, avg_values, label="Valor Médio do Swarm", color="blue", linestyle="--", linewidth=2)
    plt.title(f"Convergência do PSO - {version}")
    plt.yscale('log')
    plt.xlabel("Iterações")
    plt.ylabel("Valor (log)")
    plt.legend()
    plt.grid()
    plt.savefig(filename)
    plt.show()

if __name__ == "__main__":
    results = {}
    convergence_data = {}
    execution_times = {}
   
    for version in ["simple", "weights", "weights_and_constriction"]:
       
        start_time = time.time()

        best_values, iterations_data = run_experiments(version)
        results[f"{version}"] = best_values
        convergence_data[f"{version}"] = iterations_data    

        end_time = time.time()
        execution_time = end_time - start_time
        print(f"tempo de execução para a versao {version}:  {execution_time:.2f} \n\n")
            

    if CASE == 1:
        plot_boxplots(results, f"comparacao_boxplot_Griewank_{DIMENSIONS}.png")
    if CASE == 2:
        plot_boxplots(results, f"comparacao_boxplot_Ackley_{DIMENSIONS}.png")
    

    # Gerar gráficos de convergência
    for version, data in convergence_data.items():
        if CASE == 1:
            plot_convergence(data, f"convergencia_{version}_Griewank_{DIMENSIONS}.png", version)
        if CASE == 2:
            plot_convergence(data, f"convergencia_{version}_Ackley_{DIMENSIONS}.png", version)
