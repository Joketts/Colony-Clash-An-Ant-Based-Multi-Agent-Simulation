from agents import ScoutAnt, WorkerAnt
from environment import Environment
import pygame


class Simulation:
    def __init__(self):
        self.environment = Environment(75, 75)

        nest_1_x, nest_1_y = self.environment.nests[1]
        self.agents = [
            ScoutAnt(nest_1_x, nest_1_y, self.environment, colony=1),
            WorkerAnt(nest_1_x, nest_1_y, self.environment, colony=1),
            WorkerAnt(nest_1_x, nest_1_y + 2, self.environment, colony=1),
            WorkerAnt(nest_1_x - 2, nest_1_y, self.environment, colony=1),
        ]

        # Create agents for Colony 2
        nest_2_x, nest_2_y = self.environment.nests[2]
        self.agents.extend([
            ScoutAnt(nest_2_x, nest_2_y, self.environment, colony=2),
            WorkerAnt(nest_2_x, nest_2_y, self.environment, colony=2),
            WorkerAnt(nest_2_x, nest_2_y + 2, self.environment, colony=2),
            WorkerAnt(nest_2_x - 2, nest_2_y, self.environment, colony=2),
        ])

        self.environment.spawn_food()
        self.environment.add_hazards(num_hazards=500)
        self.occupied_squares = set()  # Track occupied squares

    def update(self):
        self.occupied_squares.clear()
        for agent in self.agents:
            self.occupied_squares.add((agent.x, agent.y))
        for agent in self.agents:
            agent.act(self.occupied_squares)
        # Clear pheromones where food has been depleted
        self.environment.update_pheromone_lifetime()
        self.environment.regenerate_food()
        #if not any(cell["food"] > 0 for row in self.environment.grid for cell in row):
        #    self.environment.clear_pheromones_near_empty_food()

    def render(self, screen):
        screen.fill((30, 30, 30))   # Background color
        cell_size = 16

        for y, row in enumerate(self.environment.grid):
            for x, cell in enumerate(row):
                if cell["hazard"]:
                    pygame.draw.rect(screen, (139, 69, 19),
                                     (x * cell_size, y * cell_size, cell_size, cell_size))  # Dark red
                elif cell["food"] > 0:
                    pygame.draw.rect(screen, (57, 255, 20),
                                     (x * cell_size, y * cell_size, cell_size, cell_size))  # Green for food
                else:
                    # Check pheromone levels explicitly
                    has_pheromone = False
                    if isinstance(cell["pheromone"], dict):
                        for colony, value in cell["pheromone"].items():
                            if value > 0:
                                has_pheromone = True
                                break
                    else:
                        cell["pheromone"] = {1: 0, 2: 0}  # Reset to avoid rendering issues
                    if has_pheromone:
                        brightness_blue = min(255, int(cell["pheromone"].get(1, 0) * 2))  # Colony 1: Blue
                        brightness_green = min(255, int(cell["pheromone"].get(2, 0) * 2))  # Colony 2: Green
                        color = (0, brightness_green, brightness_blue)
                        pygame.draw.rect(screen, color, (x * cell_size, y * cell_size, cell_size, cell_size))

        # Draw the nest
        for colony, (nest_x, nest_y) in self.environment.nests.items():
            color = (255, 223, 0) if colony == 1 else (0, 223, 255)  # Different colors for each nest
            pygame.draw.rect(screen, color, (nest_x * cell_size, nest_y * cell_size, cell_size, cell_size))

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
        colony_1_text = font.render(f"Colony 1 Food Returned: {self.environment.food_returned[1]}", True,
                                    (255, 255, 255))
        colony_2_text = font.render(f"Colony 2 Food Returned: {self.environment.food_returned[2]}", True,
                                    (255, 255, 255))
        screen.blit(colony_1_text, (10, 10))
        screen.blit(colony_2_text, (10, 50))

