import numpy as np
import matplotlib.pyplot as plt

# Constantes
DIMENSIONS = 10         # Número de dimensões
GLOBAL_BEST = 0.0       # Melhor valor global da função de custo
B_LO, B_HI = -5.0, 5.0  # Limites do espaço de busca
POPULATION = 20         # Número de partículas
V_MAX = 0.1             # Velocidade máxima
PERSONAL_C = 2.05        # Coeficiente pessoal
SOCIAL_C = 2.05          # Coeficiente social
CONVERGENCE = 0.001     # Critério de convergência
MAX_ITER = 5000          # Número máximo de iterações

# Função de custo (Ackley)
def ackley(sol):
    n = len(sol)
    aux1 = sum(x**2 for x in sol)
    aux2 = sum(np.cos(2.0 * np.pi * x) for x in sol)
    return -20 * np.exp(-0.2 * np.sqrt(aux1 / n)) - np.exp(aux2 / n) + 20 + np.e

# Função de custo (Griewank)
def griewank(sol):
    top1 = sum(x**2 for x in sol)
    top2 = np.prod(np.cos(x / np.sqrt(i + 1)) for i, x in enumerate(sol))
    return (1 / 4000.0) * top1 - top2 + 1

# Classe para uma partícula
class Particle:
    def __init__(self, dimensions):
        self.pos = np.random.uniform(B_LO, B_HI, dimensions)
        self.velocity = np.random.uniform(-V_MAX, V_MAX, dimensions)
        self.best_pos = self.pos.copy()
        self.best_pos_z = ackley(self.pos)
        self.pos_z = self.best_pos_z

    def update_velocity(self, global_best_pos, inertia_weight):
        r1, r2 = np.random.random(DIMENSIONS), np.random.random(DIMENSIONS)
        cognitive = PERSONAL_C * r1 * (self.best_pos - self.pos)
        social = SOCIAL_C * r2 * (global_best_pos - self.pos)
        self.velocity = inertia_weight * self.velocity + cognitive + social
        self.velocity = np.clip(self.velocity, -V_MAX, V_MAX)

    def update_position(self):
        self.pos += self.velocity
        self.pos = np.clip(self.pos, B_LO, B_HI)
        self.pos_z = ackley(self.pos)

        if self.pos_z < self.best_pos_z:
            self.best_pos = self.pos.copy()
            self.best_pos_z = self.pos_z

# Classe para o enxame
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

# Função principal para o PSO
def particle_swarm_optimization():
    swarm = Swarm(POPULATION, DIMENSIONS)
    inertia_weight = 0.5 + np.random.random() / 2.0

    iterations_data = []

    for iter_num in range(MAX_ITER):
        swarm.update(inertia_weight)

        avg_pos_z = np.mean([p.pos_z for p in swarm.particles])
        iterations_data.append((iter_num, swarm.best_pos_z, avg_pos_z))

        #if abs(swarm.best_pos_z - GLOBAL_BEST) < CONVERGENCE:
        #    print(f"Convergência atingida em {iter_num} iterações.")
        #    break

    print("Melhor posição encontrada:", swarm.best_pos)
    print("Melhor valor encontrado:", swarm.best_pos_z)

    return iterations_data

# Função para plotar os resultados
def plot_iterations(data, filename):
    iterations, best_values, avg_values = zip(*data)

    plt.figure(figsize=(10, 6))
    plt.plot(iterations, best_values, label="Melhor Valor", color="red")
    plt.plot(iterations, avg_values, label="Valor Médio", color="blue")
    plt.title("Valores ao Longo das Iterações")
    plt.yscale('log')  # Define escala logarítmica no eixo Y
    plt.xlabel("Iterações")
    plt.ylabel("Valor(ln)")
    plt.legend()
    plt.grid()
    plt.savefig(filename)
    plt.show()

# Executa o PSO e plota os resultados
if __name__ == "__main__":
    iterations_data = particle_swarm_optimization()
    plot_iterations(iterations_data, "pso_results.png")
