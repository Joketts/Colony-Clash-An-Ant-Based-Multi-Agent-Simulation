from agents import ScoutAnt, WorkerAnt, AttackAnt
from environment import Environment
import pygame


class Simulation:
    def __init__(self):
        self.environment = Environment(75, 75)
        self.food_counters = {1: 0, 2: 0}

        nest_1_x, nest_1_y = self.environment.nests[1]
        self.agents = [
            ScoutAnt(nest_1_x, nest_1_y, self.environment, colony=1),
            WorkerAnt(nest_1_x, nest_1_y, self.environment, colony=1),
            WorkerAnt(nest_1_x, nest_1_y + 2, self.environment, colony=1),
            WorkerAnt(nest_1_x - 2, nest_1_y, self.environment, colony=1),
            AttackAnt(nest_1_x, nest_1_y - 4, self.environment, colony=1),  # Add AttackAnt for Colony 1
        ]

        # Create agents for Colony 2
        nest_2_x, nest_2_y = self.environment.nests[2]
        self.agents.extend([
            ScoutAnt(nest_2_x, nest_2_y, self.environment, colony=2),
            WorkerAnt(nest_2_x, nest_2_y, self.environment, colony=2),
            WorkerAnt(nest_2_x, nest_2_y + 2, self.environment, colony=2),
            WorkerAnt(nest_2_x - 2, nest_2_y, self.environment, colony=2),
            AttackAnt(nest_2_x, nest_2_y - 4, self.environment, colony=2),  # Add AttackAnt for Colony 2
        ])

        self.all_ants = self.agents.copy()  # Initialize self.all_ants
        self.environment.spawn_food()
        self.environment.add_hazards(num_hazards=500)
        self.occupied_squares = set()  # Track occupied squares

    def update(self):
        self.occupied_squares.clear()

        # Mark occupied squares
        for agent in self.agents:
            self.occupied_squares.add((agent.x, agent.y))

        # Remove dead ants
        self.all_ants = [ant for ant in self.all_ants if ant.alive]
        self.agents = [ant for ant in self.agents if ant.alive]

        for colony in [1, 2]:
            if self.environment.food_returned[colony] >= 6:
                self.environment.food_returned[colony] -= 6
                self.food_counters[colony] += 1

                # Spawn a new ant
                nest_x, nest_y = self.environment.nests[colony]
                if self.food_counters[colony] % 2 == 0:  # Alternate between WorkerAnt and AttackAnt
                    new_ant = WorkerAnt(nest_x, nest_y, self.environment, colony)
                    print(f"[Colony {colony}] Spawned a new WorkerAnt at the nest.")
                else:
                    new_ant = AttackAnt(nest_x, nest_y, self.environment, colony)
                    print(f"[Colony {colony}] Spawned a new AttackAnt at the nest.")

                self.all_ants.append(new_ant)
                self.agents.append(new_ant)

            # Check if there are no ScoutAnts and promote a WorkerAnt if needed
            if not any(isinstance(ant, ScoutAnt) and ant.colony == colony for ant in self.all_ants):
                for index, ant in enumerate(self.all_ants):
                    if isinstance(ant, WorkerAnt) and ant.colony == colony:
                        print(f"[Colony {colony}] Promoting WorkerAnt at ({ant.x}, {ant.y}) to ScoutAnt.")
                        new_scout = ScoutAnt(ant.x, ant.y, self.environment, colony)
                        self.all_ants[index] = new_scout

                        # Update in self.agents
                        for i, agent in enumerate(self.agents):
                            if agent is ant:
                                self.agents[i] = new_scout
                                break
                        break

            # Check if there are no AttackAnts and promote a WorkerAnt if needed
            if not any(isinstance(ant, AttackAnt) and ant.colony == colony for ant in self.all_ants):
                for index, ant in enumerate(self.all_ants):
                    if isinstance(ant, WorkerAnt) and ant.colony == colony:
                        print(f"[Colony {colony}] Promoting WorkerAnt at ({ant.x}, {ant.y}) to AttackAnt.")
                        new_attacker = AttackAnt(ant.x, ant.y, self.environment, colony)
                        self.all_ants[index] = new_attacker

                        # Update in self.agents
                        for i, agent in enumerate(self.agents):
                            if agent is ant:
                                self.agents[i] = new_attacker
                                break
                        break
            # check if last scout is the last alive change to attacker
            colony_ants = [ant for ant in self.all_ants if ant.colony == colony]
            if len(colony_ants) == 1 and isinstance(colony_ants[0], ScoutAnt):
                scout = colony_ants[0]
                print(f"[Colony {colony}] Last ScoutAnt at ({scout.x}, {scout.y}) becoming AttackAnt.")
                new_attacker = AttackAnt(scout.x, scout.y, self.environment, colony)
                self.all_ants.remove(scout)
                self.all_ants.append(new_attacker)

                # Update in self.agents
                for i, agent in enumerate(self.agents):
                    if agent is scout:
                        self.agents[i] = new_attacker
                        break

            # checks if only a scout ant and an attacker ant remains turns scout into attacker ant
            colony_ants = [ant for ant in self.all_ants if ant.colony == colony]
            scouts = [ant for ant in colony_ants if isinstance(ant, ScoutAnt)]
            attackers = [ant for ant in colony_ants if isinstance(ant, AttackAnt)]
            if len(colony_ants) == 2 and len(scouts) == 1 and len(attackers) == 1:
                scout = scouts[0]
                print(
                    f"[Colony {colony}] Only ScoutAnt and AttackAnt remain. Promoting ScoutAnt at ({scout.x}, {scout.y}) to AttackAnt.")

                # Replace the ScoutAnt with an AttackAnt
                new_attacker = AttackAnt(scout.x, scout.y, self.environment, colony)
                self.all_ants.remove(scout)
                self.all_ants.append(new_attacker)

                # Update in self.agents
                for i, agent in enumerate(self.agents):
                    if agent is scout:
                        self.agents[i] = new_attacker
                        break

            # Count the number of each type of ant
            colony_ants = [ant for ant in self.all_ants if ant.colony == colony]
            scout_ants = [ant for ant in colony_ants if isinstance(ant, ScoutAnt)]
            worker_ants = [ant for ant in colony_ants if isinstance(ant, WorkerAnt)]
            attack_ants = [ant for ant in colony_ants if isinstance(ant, AttackAnt)]

            # Check if the colony is unbalanced: 1 ScoutAnt and 2 AttackAnts but no WorkerAnts
            if len(scout_ants) == 1 and len(attack_ants) >= 2 and len(worker_ants) == 0:
                # Convert one of the AttackAnts into a WorkerAnt
                attack_ant_to_convert = attack_ants[0]  # Select the first AttackAnt
                print(
                    f"[Colony {colony}] Converting AttackAnt at ({attack_ant_to_convert.x}, {attack_ant_to_convert.y}) to WorkerAnt.")
                new_worker = WorkerAnt(attack_ant_to_convert.x, attack_ant_to_convert.y, self.environment, colony)

                # Replace the AttackAnt with the new WorkerAnt
                self.all_ants.remove(attack_ant_to_convert)
                self.all_ants.append(new_worker)

                # Update in self.agents
                for i, agent in enumerate(self.agents):
                    if agent is attack_ant_to_convert:
                        self.agents[i] = new_worker
                        break

        # Update all ants
        for agent in self.all_ants:
            agent.act(self.occupied_squares, self.all_ants)

        # Clear pheromones where food has been depleted
        self.environment.update_pheromone_lifetime()
        self.environment.regenerate_food()

        self.count_ants()
        # Check for victory
        if self.check_victory():
            return  # Stop simulation if a colony has won

    def check_victory(self):
        colony_counts = {1: 0, 2: 0}
        for ant in self.all_ants:
            colony_counts[ant.colony] += 1

        if colony_counts[1] == 0:
            self.winning_colony = 'Red'
            return True
        elif colony_counts[2] == 0:
            self.winning_colony = 'Blue'
            return True
        return False

    def count_ants(self):
        """Count ants by type for each colony."""
        colony_counts = {1: {"scouts": 0, "workers": 0, "attackers": 0},
                         2: {"scouts": 0, "workers": 0, "attackers": 0}}
        for ant in self.all_ants:
            if isinstance(ant, ScoutAnt):
                colony_counts[ant.colony]["scouts"] += 1
            elif isinstance(ant, WorkerAnt):
                colony_counts[ant.colony]["workers"] += 1
            elif isinstance(ant, AttackAnt):
                colony_counts[ant.colony]["attackers"] += 1
        return colony_counts

    def render(self, screen):
        screen.fill((10, 100, 25))   # Background color
        cell_size = 16

        for y, row in enumerate(self.environment.grid):
            for x, cell in enumerate(row):
                if cell["hazard"]:
                    pygame.draw.rect(screen, (102, 51, 0),
                                     (x * cell_size, y * cell_size, cell_size, cell_size))  # Dark red
                elif cell["food"] > 0:
                    pygame.draw.rect(screen, (255, 255, 102),
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
                        brightness_green = min(255, int(cell["pheromone"].get(2, 0) * 2))  # Colony 2: red
                        color = (brightness_green, 55, brightness_blue)
                        pygame.draw.rect(screen, color, (x * cell_size, y * cell_size, cell_size, cell_size))

        # Draw the nest
        for colony, (nest_x, nest_y) in self.environment.nests.items():
            color = (0, 102, 255) if colony == 1 else (255, 51, 51)  # Different colors for each nest
            pygame.draw.rect(screen, color, (nest_x * cell_size, nest_y * cell_size, cell_size, cell_size))

        # Draw ants
        for agent in self.agents:
            if isinstance(agent, ScoutAnt):
                color = (0, 255, 255)  # Cyan for scouts
            elif isinstance(agent, WorkerAnt):
                color = (255, 165, 0)  # Orange for workers
            elif isinstance(agent, AttackAnt):
                color = (255, 0, 0)  # Red for AttackAnt
            else:
                color = (255, 255, 255)  # White for other/unexpected ants
            pygame.draw.circle(screen, color,
                               (agent.x * cell_size + cell_size // 2, agent.y * cell_size + cell_size // 2),
                               cell_size // 3)

        font = pygame.font.Font(None, 36)
        colony_counts = self.count_ants()

        # Display Colony 1 Information
        header_1 = font.render("Colony Blue", True, (255, 255, 255))
        screen.blit(header_1, (10, 10))
        colony_1_text = [
            f"Food Returned: {self.environment.food_returned[1]}/6",
            f"Scouts: {colony_counts[1]['scouts']}",
            f"Workers: {colony_counts[1]['workers']}",
            f"Attackers: {colony_counts[1]['attackers']}"
        ]
        for i, line in enumerate(colony_1_text):
            text = font.render(line, True, (255, 255, 255))
            screen.blit(text, (10, 50 + i * 30))

        # Display Colony 2 Information
        header_2 = font.render("Colony Red", True, (255, 255, 255))
        screen.blit(header_2, (screen.get_width() - 300, 10))
        colony_2_text = [
            f"Food Returned: {self.environment.food_returned[2]}/6",
            f"Scouts: {colony_counts[2]['scouts']}",
            f"Workers: {colony_counts[2]['workers']}",
            f"Attackers: {colony_counts[2]['attackers']}"
        ]
        for i, line in enumerate(colony_2_text):
            text = font.render(line, True, (255, 255, 255))
            screen.blit(text, (screen.get_width() - 300, 50 + i * 30))

        if hasattr(self, 'winning_colony'):
            another_font = pygame.font.Font(None, 125)  # Bigger font size
            winning_text = another_font.render(f"Colony {self.winning_colony} Wins!", True, (255, 255, 255))  # White text
            screen.blit(winning_text,
                        (screen.get_width() // 2 - winning_text.get_width() // 2,
                         screen.get_height() // 2 - winning_text.get_height() // 2))  # Center the text

        pygame.display.flip()