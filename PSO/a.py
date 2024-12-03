import numpy as np
import matplotlib.pyplot as plt
import time  # Para medir o tempo de execução

# Funções de otimização
def griewank(sol):
    top1 = sum(x**2 for x in sol)
    top2 = np.prod(np.cos(x / np.sqrt(i + 1)) for i, x in enumerate(sol))
    return (1 / 4000.0) * top1 - top2 + 1

def ackley(sol):
    n = len(sol)
    aux1 = sum(x**2 for x in sol)
    aux2 = sum(np.cos(2.0 * np.pi * x) for x in sol)
    return -20 * np.exp(-0.2 * np.sqrt(aux1 / n)) - np.exp(aux2 / n) + 20 + np.e

# Classe para partículas
class Particle:
    def __init__(self, dim, bounds):
        self.position = np.random.uniform(bounds[0], bounds[1], dim)
        self.velocity = np.random.uniform(-1, 1, dim)
        self.best_position = np.copy(self.position)
        self.best_value = float('inf')
        self.value = float('inf')

    def update_velocity(self, global_best_position, w, c1, c2):
        r1 = np.random.random(len(self.position))
        r2 = np.random.random(len(self.position))
        cognitive = c1 * r1 * (self.best_position - self.position)
        social = c2 * r2 * (global_best_position - self.position)
        self.velocity = cognitive + social + self.velocity * w

    def update_position(self, bounds):
        self.position += self.velocity
        self.position = np.clip(self.position, bounds[0], bounds[1])

# Classe para o enxame
class Swarm:
    def __init__(self, n_particles, dim, bounds, w, c1, c2, n_iterations, function):
        self.n_particles = n_particles
        self.dim = dim
        self.bounds = bounds
        self.w = w
        self.c1 = c1
        self.c2 = c2
        self.n_iterations = n_iterations
        self.function = function
        self.particles = [Particle(dim, bounds) for _ in range(n_particles)]
        self.global_best_position = None
        self.global_best_value = float('inf')
        self.global_best_history = []
        self.mean_fitness_history = []

    def optimize(self):
        for iteration in range(self.n_iterations):
            fitness_values = []
            for particle in self.particles:
                particle.value = self.function(particle.position)
                fitness_values.append(particle.value)

                if particle.value < particle.best_value:
                    particle.best_value = particle.value
                    particle.best_position = np.copy(particle.position)

                if particle.value < self.global_best_value:
                    self.global_best_value = particle.value
                    self.global_best_position = np.copy(particle.position)

            # Registrar histórico
            self.global_best_history.append(self.global_best_value)
            self.mean_fitness_history.append(np.mean(fitness_values))

            for particle in self.particles:
                particle.update_velocity(self.global_best_position, self.w, self.c1, self.c2)
                particle.update_position(self.bounds)

            print(f"Iteration {iteration+1}/{self.n_iterations}, Global Best Value: {self.global_best_value}")

    def plot_convergence(self, filename="convergence_plot.png"):
        plt.figure(figsize=(10, 6))
        plt.plot(self.global_best_history, label="Global Best Value", color='blue')
        plt.plot(self.mean_fitness_history, label="Mean Swarm Fitness", color='orange')
        plt.yscale('log')  # Define escala logarítmica no eixo Y
        plt.xlabel("Iterations")
        plt.ylabel("Fitness Value")
        plt.title("PSO Convergence")
        plt.legend()
        plt.grid(True)
        plt.savefig(filename, format='png')  # Salva o gráfico como PNG
        #plt.show()
        print(f"Gráfico salvo como {filename}")

    def print_final_positions(self):
        print("\nFinal positions of particles:")
        for i, particle in enumerate(self.particles):
            print(f"Particle {i + 1}: {particle.position}")

# Parâmetros do PSO
params = {
    "n_particles": 20,
    "dim": 10,
    "bounds": (-32, 32),
    "w": 0.5, #0 ate 1.5
    "c1": 2.05,
    "c2": 2.05,
    "n_iterations": 1000,
    "function": ackley,  # Mudar para griewank para usar a outra função
}

# Medir tempo de execução
start_time = time.time()

# Execução
swarm = Swarm(**params)
swarm.optimize()
swarm.plot_convergence("convergence_plot.png")
swarm.print_final_positions()

# Calcular tempo total de execução
end_time = time.time()
execution_time = end_time - start_time
print(f"\nTotal execution time: {execution_time:.2f} seconds")
