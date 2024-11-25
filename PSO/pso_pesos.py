# Modificado para incluir peso de inércia adaptativo
import numpy as np
import matplotlib.pyplot as plt

# Constantes
DIMENSIONS = 10         # Número de dimensões
GLOBAL_BEST = 0.0       # Melhor valor global da função de custo
B_LO, B_HI = -5.0, 5.0  # Limites do espaço de busca
POPULATION = 20         # Número de partículas
V_MAX = 0.1             # Velocidade máxima
PERSONAL_C = 2.0        # Coeficiente pessoal
SOCIAL_C = 2.0          # Coeficiente social
CONVERGENCE = 0.001     # Critério de convergência
MAX_ITER = 100          # Número máximo de iterações
W_INIT = 0.9            # Peso de inércia inicial
W_FINAL = 0.4           # Peso de inércia final

# Função de custo (Ackley)
def cost_function(pos):
    a = 20.0
    b = 0.2
    c = 2 * np.pi
    d = len(pos)

    sum_sq = np.sum(pos ** 2)
    sum_cos = np.sum(np.cos(c * pos))

    term_1 = -a * np.exp(-b * np.sqrt(sum_sq / d))
    term_2 = -np.exp(sum_cos / d)
    return term_1 + term_2 + a + np.exp(1)

# Classe para uma partícula
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
        self.velocity = inertia_weight * self.velocity + cognitive + social
        self.velocity = np.clip(self.velocity, -V_MAX, V_MAX)

    def update_position(self):
        self.pos += self.velocity
        self.pos = np.clip(self.pos, B_LO, B_HI)
        self.pos_z = cost_function(self.pos)

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
    iterations_data = []

    for iter_num in range(MAX_ITER):
        # Peso de inércia decai linearmente
        inertia_weight = W_INIT - (W_INIT - W_FINAL) * (iter_num / MAX_ITER)
        
        swarm.update(inertia_weight)

        avg_pos_z = np.mean([p.pos_z for p in swarm.particles])
        iterations_data.append((iter_num, swarm.best_pos_z, avg_pos_z))

        if abs(swarm.best_pos_z - GLOBAL_BEST) < CONVERGENCE:
            print(f"Convergência atingida em {iter_num} iterações.")
            break

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
    plt.xlabel("Iterações")
    plt.ylabel("Valor")
    plt.legend()
    plt.grid()
    plt.savefig(filename)
    plt.show()

# Executa o PSO e plota os resultados
if __name__ == "__main__":
    iterations_data = particle_swarm_optimization()
    plot_iterations(iterations_data, "pso_results_with_inertia.png")
