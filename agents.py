import random
import math
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
    def __init__(self, x, y, environment):
        super().__init__(x, y, environment)
        self.state = "searching"  # States: searching, returning
        self.target_food = None
        self.visited_food = set()  # Track visited food to avoid revisiting
        self.timeout_counter = 0  # Counter to track time spent away from the nest
        self.timeout_limit = 600  # Maximum steps before forced return to the nest
        self.forced_return = False

    def find_closest_unvisited_food(self):
        """Find the closest food source that has not been visited."""
        closest_food = None
        min_distance = float('inf')
        for y in range(self.environment.height):
            for x in range(self.environment.width):
                cell = self.environment.grid[y][x]
                if cell["food"] > 0 and (x, y) not in self.visited_food:
                    distance = self.euclidean_distance(self.x, self.y, x, y)
                    if distance < min_distance:
                        min_distance = distance
                        closest_food = (x, y)
        return closest_food

    def act(self, occupied_squares):
        # Increment timeout counter
        self.timeout_counter += 1

        if self.steps_since_last_move < 2:  # Adjust movement speed
            self.steps_since_last_move += 1
            return
        self.steps_since_last_move = 0

        # Check for timeout
        if self.timeout_counter > self.timeout_limit:
            # Force return to the nest
            self.state = "returning"
            self.target_food = None
            self.forced_return = True  # Mark as a forced return

        if self.state == "searching":
            if not self.target_food:
                # Find the closest unvisited food source
                self.target_food = self.find_closest_unvisited_food()
            if self.target_food:
                food_x, food_y = self.target_food
                if (self.x, self.y) == (food_x, food_y):
                    # Mark the food as visited and switch to returning state
                    self.visited_food.add(self.target_food)
                    self.state = "returning"
                    self.timeout_counter = 0  # Reset timeout upon finding food
                    self.forced_return = False  # Not a forced return
                else:
                    # Add slight randomness to movement to diversify paths
                    if random.random() < 0.2:  # 20% chance to move randomly
                        self.move_randomly(occupied_squares)
                    else:
                        self.move_towards(food_x, food_y, occupied_squares)
            else:
                # Explore randomly if no unvisited food is found
                self.move_randomly(occupied_squares)

        elif self.state == "returning":
            # Deposit pheromones while returning to the nest only if not a forced return
            if not self.forced_return:
                self.environment.add_pheromone(self.x, self.y, amount=10, food_location=self.target_food)

            nest_x, nest_y = self.environment.nest
            if (self.x, self.y) == (nest_x, nest_y):
                # Reset to searching state after returning to the nest
                self.state = "searching"
                self.target_food = None
                self.timeout_counter = 0  # Reset timeout upon returning to the nest
                self.forced_return = False  # Reset forced return flag
            else:
                # Add slight randomness to avoid overlap
                if random.random() < 0.1:  # 10% chance to deviate from path
                    self.move_randomly(occupied_squares)
                else:
                    self.move_towards(nest_x, nest_y, occupied_squares)
class WorkerAnt(AntBase):
    def __init__(self, x, y, environment):
        super().__init__(x, y, environment)
        self.carrying_food = False
        self.last_position = None  # Track the last position to avoid loops
        self.timeout_counter = 0  # Counter to track time spent away from the nest
        self.timeout_limit = 300  # Maximum steps before returning to the nest

    def act(self, occupied_squares):
        # Increment timeout counter
        self.timeout_counter += 1

        if self.steps_since_last_move < 5:
            self.steps_since_last_move += 1
            return
        self.steps_since_last_move = 0

        # Timeout check: force return to the nest
        if self.timeout_counter > self.timeout_limit:
            nest_x, nest_y = self.environment.nest
            if (self.x, self.y) != (nest_x, nest_y):
                self.move_towards(nest_x, nest_y, occupied_squares)
                return
            else:
                self.timeout_counter = 0  # Reset counter upon returning to the nest

        if self.carrying_food:
            # Return to the nest
            nest_x, nest_y = self.environment.nest
            if (self.x, self.y) == (nest_x, nest_y):
                # Drop food at the nest
                self.carrying_food = False
                self.environment.food_returned += 1
                print(f"[WorkerAnt] Food returned to nest. Total: {self.environment.food_returned}")
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

            # Filter moves by pheromone strength and avoid backtracking
            valid_moves = [
                pos for pos in potential_moves
                if pos != self.last_position and self.environment.grid[pos[1]][pos[0]]["pheromone"] > 0
            ]

            if valid_moves:
                # Choose the move with the highest pheromone level leading away from the nest
                best_move = max(valid_moves, key=lambda pos: (
                    self.environment.grid[pos[1]][pos[0]]["pheromone"],
                    self.euclidean_distance(pos[0], pos[1], self.environment.nest[0], self.environment.nest[1])
                ))
                self.last_position = (self.x, self.y)  # Update last position
                self.x, self.y = best_move

                # Check if food is found
                if self.environment.is_food(self.x, self.y):
                    self.carrying_food = True
                    self.environment.collect_food(self.x, self.y)
                    self.timeout_counter = 0  # Reset counter upon finding food
            else:
                # Random movement if no pheromones detected
                self.move_randomly(occupied_squares)
                self.last_position = (self.x, self.y)

