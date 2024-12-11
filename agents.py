import random
import math

import heapq

def a_star_search(environment, start, goal):
    """A* algorithm to find the shortest path avoiding hazards."""
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])  # Manhattan distance

    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    cost_so_far = {start: 0}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            break

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Four directions
            neighbor = ((current[0] + dx) % environment.width, (current[1] + dy) % environment.height)

            if environment.grid[neighbor[1]][neighbor[0]]["hazard"]:
                continue  # Skip hazardous cells

            new_cost = cost_so_far[current] + 1
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + heuristic(goal, neighbor)
                heapq.heappush(open_set, (priority, neighbor))
                came_from[neighbor] = current

    # Reconstruct path
    current = goal
    path = []
    while current != start:
        path.append(current)
        current = came_from.get(current, start)
    path.reverse()
    return path
class AntBase:
    def __init__(self, x, y, environment):
        self.x = x
        self.y = y
        self.environment = environment
        self.steps_since_last_move = 0

    def move_randomly(self, occupied_squares):
        """Move randomly, avoiding occupied and hazard squares."""
        potential_moves = [
            ((self.x + dx) % self.environment.width, (self.y + dy) % self.environment.height)
            for dx, dy in [
                (0, 1), (1, 0), (0, -1), (-1, 0),  # Straight directions
                (1, 1), (-1, -1), (1, -1), (-1, 1)  # Diagonal directions
            ]
        ]
        valid_moves = [
            pos for pos in potential_moves
            if pos not in occupied_squares and not self.environment.grid[pos[1]][pos[0]]["hazard"]
        ]
        if valid_moves:
            self.x, self.y = random.choice(valid_moves)

    def euclidean_distance(self, x1, y1, x2, y2):
        """Calculate the Euclidean distance between two points."""
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def move_towards(self, target_x, target_y, occupied_squares):
        """Move one step closer to the target, avoiding occupied and hazard squares."""
        potential_moves = [
            ((self.x + dx) % self.environment.width, (self.y + dy) % self.environment.height)
            for dx, dy in [
                (0, 1), (1, 0), (0, -1), (-1, 0),  # Straight directions
                (1, 1), (-1, -1), (1, -1), (-1, 1)  # Diagonal directions
            ]
        ]
        valid_moves = [
            pos for pos in potential_moves
            if pos not in occupied_squares and not self.environment.grid[pos[1]][pos[0]]["hazard"]
        ]
        if valid_moves:
            best_move = min(valid_moves, key=lambda pos: self.euclidean_distance(pos[0], pos[1], target_x, target_y))
            self.x, self.y = best_move

class ScoutAnt(AntBase):
    def __init__(self, x, y, environment, colony):
        super().__init__(x, y, environment)
        self.colony = colony  # Store colony ID
        self.state = "scanning"  # States: scanning, traveling, returning
        self.target_food = None
        self.resources = []  # List of food locations
        self.hazards = []  # List of hazard locations
        self.path = []  # Path to follow

    def scan_environment(self):
        """Scan the entire grid to identify resources and hazards."""
        self.resources = []
        self.hazards = []
        for y in range(self.environment.height):
            for x in range(self.environment.width):
                cell = self.environment.grid[y][x]
                if cell["food"] > 0:
                    self.resources.append((x, y))
                if cell["hazard"]:
                    self.hazards.append((x, y))
        print(f"[ScoutAnt] Scanned environment. Resources: {len(self.resources)}, Hazards: {len(self.hazards)}")

    def act(self, occupied_squares):
        if self.steps_since_last_move < 3:  # Adjust movement speed
            self.steps_since_last_move += 1
            return
        self.steps_since_last_move = 0

        if self.state == "scanning":
            self.scan_environment()
            if self.resources:
                # Choose a random resource and compute a path to it
                self.target_food = random.choice(self.resources)
                self.path = a_star_search(self.environment, (self.x, self.y), self.target_food)
                self.state = "traveling"
            else:
                self.move_randomly(occupied_squares)  # No resources found, move randomly

        elif self.state == "traveling":
            if self.path:
                next_step = self.path.pop(0)
                self.x, self.y = next_step
                if not self.path:  # Reached the target
                    # Mark the food as "visited" by removing it from the resource list
                    if self.target_food in self.resources:
                        self.resources.remove(self.target_food)

                    self.state = "returning"
                    self.environment.add_pheromone(self.x, self.y, colony=self.colony, amount=20, food_location=self.target_food)
            else:
                self.state = "returning"  # Fallback if the path is empty

        elif self.state == "returning":
            # Deposit pheromones while returning to the nest
            self.environment.add_pheromone(self.x, self.y, colony=self.colony, amount=20, food_location=self.target_food)
            nest_x, nest_y = self.environment.nests[self.colony]
            if (self.x, self.y) == (nest_x, nest_y):
                self.state = "scanning"
                self.target_food = None
                self.path = []          # Reset the target food after returning to the nest
            else:
                # Calculate path dynamically or move step-by-step toward the nest
                if not self.path:
                    self.path = a_star_search(self.environment, (self.x, self.y), (nest_x, nest_y))
                if self.path:
                    next_step = self.path.pop(0)
                    self.x, self.y = next_step


class WorkerAnt(AntBase):
    def __init__(self, x, y, environment, colony):
        super().__init__(x, y, environment)
        self.colony = colony  # Store colony ID
        self.carrying_food = False
        self.last_position = None  # Track the last position to avoid loops
        self.timeout_counter = 0  # Counter to track time spent away from the nest
        self.timeout_limit = 500  # Maximum steps before returning to the nest
        self.recent_positions = []  # Keep track of last few visited positions
        self.memory_limit = 5  # Number of positions to remember

    def act(self, occupied_squares):
        # Increment timeout counter
        self.timeout_counter += 1

        if self.steps_since_last_move < 5:
            self.steps_since_last_move += 1
            return
        self.steps_since_last_move = 0

        # Timeout check: force return to the nest
        if self.timeout_counter > self.timeout_limit:
            nest_x, nest_y = self.environment.nests[self.colony]
            if (self.x, self.y) != (nest_x, nest_y):
                self.move_towards(nest_x, nest_y, occupied_squares)
                return
            else:
                self.timeout_counter = 0  # Reset counter upon returning to the nest

        if self.carrying_food:
            # Return to the nest
            nest_x, nest_y = self.environment.nests[self.colony]  # Use the correct nest for the colony
            if (self.x, self.y) == (nest_x, nest_y):
                # Drop food at the nest
                self.carrying_food = False
                self.environment.food_returned[self.colony] += 1
                #print(
                 #   f"[WorkerAnt] Colony {self.colony} returned food. Total: {self.environment.food_returned[self.colony]}")
                self.timeout_counter = 0  # Reset counter upon successful return
            else:
                self.move_towards(nest_x, nest_y, occupied_squares)
        else:
            # Follow pheromone trails to find food
            potential_moves = [
                ((self.x + dx) % self.environment.width, (self.y + dy) % self.environment.height)
                for dx, dy in [
                    (0, 1), (1, 0), (0, -1), (-1, 0),  # Straight directions
                    (1, 1), (-1, -1), (1, -1), (-1, 1)  # Diagonal directions
                ]
            ]
            # Filter out invalid moves
            valid_moves = [
                pos for pos in potential_moves
                if pos != self.last_position  # Avoid immediate backtracking
                   and pos not in self.recent_positions  # Avoid recently visited positions
                   and not self.environment.grid[pos[1]][pos[0]]["hazard"]  # Avoid hazards
                   and self.environment.grid[pos[1]][pos[0]]["pheromone"].get(self.colony, 0) > 0
                # Follow colony-specific pheromones
            ]

            if valid_moves:
                best_move = max(valid_moves, key=lambda pos: (
                    self.environment.grid[pos[1]][pos[0]]["pheromone"].get(self.colony, 0),
                    -self.euclidean_distance(pos[0], pos[1], self.environment.nests[self.colony][0],
                                             self.environment.nests[self.colony][1])
                ))
                print(f"[WorkerAnt] Colony {self.colony} following pheromone at {best_move} with strength {self.environment.grid[best_move[1]][best_move[0]]['pheromone'].get(self.colony, 0)}")
                self.last_position = (self.x, self.y)
                self.x, self.y = best_move

                # Update recent positions
                self.recent_positions.append((self.x, self.y))
                if len(self.recent_positions) > self.memory_limit:
                    self.recent_positions.pop(0)

                # Check if food is found
                if self.environment.is_food(self.x, self.y):
                    self.carrying_food = True
                    self.environment.collect_food(self.x, self.y)
                    self.last_position = None  # Reset last position to avoid blocking
            else:
                # Fallback: Explore randomly if no valid pheromone trails are detected
                self.move_randomly(occupied_squares)
                self.last_position = (self.x, self.y)
