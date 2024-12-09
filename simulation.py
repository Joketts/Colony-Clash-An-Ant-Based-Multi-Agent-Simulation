from agents import ScoutAnt, WorkerAnt
from environment import Environment
import pygame

class Simulation:
    def __init__(self):
        self.environment = Environment(50, 50)
        nest_x, nest_y = self.environment.nest
        self.agents = [
            ScoutAnt(nest_x, nest_y, self.environment),
            ScoutAnt(nest_x + 1, nest_y + 1, self.environment),
            WorkerAnt(nest_x, nest_y + 1, self.environment),
            WorkerAnt(nest_x, nest_y + 2, self.environment),
            WorkerAnt(nest_x - 1, nest_y, self.environment)
        ]
        self.environment.spawn_food()
        self.environment.add_hazards(num_hazards=300)
        self.occupied_squares = set()  # Track occupied squares

    def update(self):
        self.occupied_squares.clear()
        for agent in self.agents:
            self.occupied_squares.add((agent.x, agent.y))
        for agent in self.agents:
            agent.act(self.occupied_squares)
        # Clear pheromones where food has been depleted

        self.environment.regenerate_food()
        if not any(cell["food"] > 0 for row in self.environment.grid for cell in row):
            self.environment.clear_pheromones_near_empty_food()

    def render(self, screen):
        screen.fill((30, 30, 30))   # Background color
        cell_size = 17

        for y, row in enumerate(self.environment.grid):
            for x, cell in enumerate(row):
                if cell["hazard"]:
                    pygame.draw.rect(screen, (139, 69, 19),
                                     (x * cell_size, y * cell_size, cell_size, cell_size))  # Dark red
                elif cell["food"] > 0:
                    pygame.draw.rect(screen, (57, 255, 20),
                                     (x * cell_size, y * cell_size, cell_size, cell_size))  # Green for food
                elif cell["pheromone"] > 0:
                    brightness = min(255, int(cell["pheromone"] * 5))  # Scale brightness for pheromone
                    pygame.draw.rect(screen, (0, 0, brightness), (x * cell_size, y * cell_size, cell_size, cell_size))

        # Draw the nest
        nest_x, nest_y = self.environment.nest
        pygame.draw.rect(screen, (255, 223, 0),
                         (nest_x * cell_size, nest_y * cell_size, cell_size, cell_size))  # Yellow for nest

        # Draw ants
        for agent in self.agents:
            if isinstance(agent, ScoutAnt):
                color = (0, 255, 255)  # Cyan for scouts
            elif isinstance(agent, WorkerAnt):
                color = (255, 165, 0)  # Orange for workers
            else:
                color = (255, 0, 0)  # Red for unknown types
            pygame.draw.circle(screen, color,
                               (agent.x * cell_size + cell_size // 2, agent.y * cell_size + cell_size // 2),
                               cell_size // 3)

        font = pygame.font.Font(None, 36)
        text = font.render(f"Food Returned: {self.environment.food_returned}", True, (255, 255, 255))
        screen.blit(text, (10, 10))

