import random
import math
import numpy as np
import matplotlib.pyplot as plt

# Constantes
DIMENSIONS = 5  # Altere para o número de dimensões desejado
GLOBAL_BEST = 0.0  # Melhor valor global da função de custo
B_LO = -5.0  # Limite inferior do espaço de busca
B_HI = 5.0  # Limite superior do espaço de busca

POPULATION = 30  # Número de partículas no enxame
V_MAX = 0.1  # Velocidade máxima
CONVERGENCE = 0.000001  # Critério de convergência
MAX_ITER = 5000  # Número máximo de iterações

# Estrutura da Partícula
class Particle:
    def __init__(self, dim, v_max):
        self.pos = [random.uniform(B_LO, B_HI) for _ in range(dim)]
        self.velocity = [random.uniform(-v_max, v_max) for _ in range(dim)]
        self.pos_z = cost_function(self.pos)
        self.best_pos = self.pos[:]
        self.best_pos_z = self.pos_z

# Estrutura do Enxame
class Swarm:
    def __init__(self, population, dim, v_max):
        self.particles = [Particle(dim, v_max) for _ in range(population)]
        self.best_pos = None
        self.best_pos_z = float("inf")

        for particle in self.particles:
            if particle.pos_z < self.best_pos_z:
                self.best_pos = particle.pos[:]
                self.best_pos_z = particle.pos_z

# Função de custo (Ackley) generalizada para N dimensões
def cost_function(pos):
    a = 20.0
    b = 0.2
    c = 2.0 * math.pi

    sum_sq = sum(x ** 2 for x in pos)
    sum_cos = sum(math.cos(c * x) for x in pos)

    term_1 = math.exp(-b * math.sqrt(sum_sq / DIMENSIONS))
    term_2 = math.exp(sum_cos / DIMENSIONS)

    return -a * term_1 - term_2 + a + math.e

# Implementação base do PSO
def particle_swarm_optimization_base():
    swarm = Swarm(POPULATION, DIMENSIONS, V_MAX)
    curr_iter = 0
    iterations_data = []

    while curr_iter < MAX_ITER:
        for particle in swarm.particles:
            for i in range(DIMENSIONS):
                r1 = random.random()
                r2 = random.random()
                c1, c2 = 2.0, 2.0

                personal_coefficient = c1 * r1 * (particle.best_pos[i] - particle.pos[i])
                social_coefficient = c2 * r2 * (swarm.best_pos[i] - particle.pos[i])
                new_velocity = particle.velocity[i] + personal_coefficient + social_coefficient

                # Limitar a velocidade
                new_velocity = max(-V_MAX, min(V_MAX, new_velocity))
                particle.velocity[i] = new_velocity

                # Atualizar a posição
                particle.pos[i] += particle.velocity[i]
                particle.pos[i] = max(B_LO, min(B_HI, particle.pos[i]))

            particle.pos_z = cost_function(particle.pos)

            # Atualizar o melhor local
            if particle.pos_z < particle.best_pos_z:
                particle.best_pos = particle.pos[:]
                particle.best_pos_z = particle.pos_z

        # Atualizar o melhor global
        for particle in swarm.particles:
            if particle.pos_z < swarm.best_pos_z:
                swarm.best_pos = particle.pos[:]
                swarm.best_pos_z = particle.pos_z

        # Coletar dados para análise
        average_pos_z = sum(p.pos_z for p in swarm.particles) / POPULATION
        iterations_data.append({
            "iteration_number": curr_iter,
            "best_value": swarm.best_pos_z,
            "average_value": average_pos_z
        })

        # Verificar convergência
        #if abs(swarm.best_pos_z - GLOBAL_BEST) < CONVERGENCE:
        #    print(f"Convergência atingida após {curr_iter} iterações.")
        #    break

        curr_iter += 1

    print("Melhor posição encontrada:", swarm.best_pos)
    print("Melhor valor encontrado:", swarm.best_pos_z)

    # Salvar o melhor vetor de posição
    with open("best_position_base.txt", "w") as file:
        file.write(str(swarm.best_pos))

    return iterations_data

# Função principal
if __name__ == "__main__":
    data = particle_swarm_optimization_base()
    # Plotar os resultados
    iterations = [d["iteration_number"] for d in data]
    best_values = [d["best_value"] for d in data]
    plt.plot(iterations, best_values, label="Melhor valor")
    plt.xlabel("Iterações")
    plt.ylabel("Valor da função de custo")
    plt.title("PSO - Implementação Base")
    plt.legend()
    plt.grid()
    plt.show()
