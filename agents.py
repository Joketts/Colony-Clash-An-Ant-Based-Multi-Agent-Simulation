import random
import math
import heapq


def a_star_search(environment, start, goal):

    # returns manhattan distance between points
    def heuristic(start_point, end_point):
        return abs(start_point[0] - end_point[0]) + abs(start_point[1] - end_point[1])

    # q for nodes to search, starts with priority of 0
    search_q = []
    heapq.heappush(search_q, (0, start))

    # dictionary to track path
    came_from = {}
    # dictionary to store cost
    cost_so_far = {start: 0}

    while search_q:

        # gets lowest priority node
        priority, current = heapq.heappop(search_q)

        if current == goal:
            break

        # explore all valid neighbors
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = ((current[0] + dx) % environment.width, (current[1] + dy) % environment.height)

            # avoids hazards
            if environment.grid[neighbor[1]][neighbor[0]]["hazard"]:
                continue

            # calculate new cost
            new_cost = cost_so_far[current] + 1
            # if neighbor hasn't been visited or a cheaper path found
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                # updates cost
                cost_so_far[neighbor] = new_cost
                # calculates priority for open set
                priority = new_cost + heuristic(goal, neighbor)
                # adds neighbor to open set
                heapq.heappush(search_q, (priority, neighbor))
                # records path to neighbor
                came_from[neighbor] = current

    # reconstructs path to goal node then returns the path as output
    current = goal
    path = []
    while current != start:
        path.append(current)
        current = came_from.get(current, start)
    path.reverse()
    return path


class AntBasicMovement:
    def __init__(self, x, y, environment):
        self.x = x
        self.y = y
        self.environment = environment
        self.steps_since_last_move = 0
        self.alive = True

    # moves ant randomly both straight and diagonally, avoiding occupied squares and hazards
    def move_randomly(self, occupied_squares):
        potential_moves = [
            ((self.x + dx) % self.environment.width, (self.y + dy) % self.environment.height)
            for dx, dy in [
                (0, 1), (1, 0), (0, -1), (-1, 0),
                (1, 1), (-1, -1), (1, -1), (-1, 1)
            ]
        ]
        valid_moves = [
            pos for pos in potential_moves
            if pos not in occupied_squares and not self.environment.grid[pos[1]][pos[0]]["hazard"]
        ]
        if valid_moves:
            self.x, self.y = random.choice(valid_moves)

    # gets Euclidean distance
    def euclidean_distance(self, x1, y1, x2, y2):
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    # moves ant one step towards target avoiding occupied squares and hazards
    def move_towards(self, target_x, target_y, occupied_squares):
        potential_moves = [
            ((self.x + dx) % self.environment.width, (self.y + dy) % self.environment.height)
            for dx, dy in [
                (0, 1), (1, 0), (0, -1), (-1, 0),
                (1, 1), (-1, -1), (1, -1), (-1, 1)
            ]
        ]
        valid_moves = [
            pos for pos in potential_moves
            if pos not in occupied_squares and not self.environment.grid[pos[1]][pos[0]]["hazard"]
        ]
        if valid_moves:
            best_move = min(valid_moves, key=lambda pos: self.euclidean_distance(pos[0], pos[1], target_x, target_y))
            self.x, self.y = best_move


class ScoutAnt(AntBasicMovement):
    def __init__(self, x, y, environment, colony):
        super().__init__(x, y, environment)
        self.colony = colony
        self.state = "scanning"
        self.current_food = None
        self.food = []
        self.hazards = []
        self.current_route = []

    # scans enviroment for food and hazards updates both lists
    def scan_environment(self):
        self.food = []
        self.hazards = []
        for y in range(self.environment.height):
            for x in range(self.environment.width):
                cell = self.environment.grid[y][x]
                if cell["food"] > 0:
                    self.food.append((x, y))
                if cell["hazard"]:
                    self.hazards.append((x, y))
        print(f"scout ant scanned grid found food: {len(self.food)}, hazards: {len(self.hazards)}")

    def act(self, occupied_squares, all_ants):

        # movement happens every three steps
        if self.steps_since_last_move < 3:
            self.steps_since_last_move += 1
            return
        self.steps_since_last_move = 0

        # scans grid, chooses random food
        if self.state == "scanning":
            self.scan_environment()
            if self.food:
                self.current_food = random.choice(self.food)
                self.current_route = a_star_search(self.environment, (self.x, self.y), self.current_food)
                # change state to traveling
                self.state = "traveling"
            else:
                self.move_randomly(occupied_squares)

        # follows path to food
        elif self.state == "traveling":
            if self.current_route:
                next_step = self.current_route.pop(0)
                self.x, self.y = next_step
                # once at food ,mark as visited
                if not self.current_route:
                    if self.current_food in self.food:
                        self.food.remove(self.current_food)
                    # change state to returning
                    self.state = "returning"
                    self.environment.add_pheromone(self.x, self.y, colony=self.colony, amount=20, food_location=self.current_food)
            else:
                self.state = "returning"

        # while returning leave pheromones
        elif self.state == "returning":
            self.environment.add_pheromone(self.x, self.y, colony=self.colony, amount=20, food_location=self.current_food)
            # gets nest coords
            nest_x, nest_y = self.environment.nests[self.colony]
            # once back at nest change state back to scanning, reset target food and clear path
            if (self.x, self.y) == (nest_x, nest_y):
                self.state = "scanning"
                self.current_food = None
                self.current_route = []
            else:
                # if not back at nest yet, continue back to nest
                if not self.current_route:
                    self.current_route = a_star_search(self.environment, (self.x, self.y), (nest_x, nest_y))
                if self.current_route:
                    next_step = self.current_route.pop(0)
                    self.x, self.y = next_step


class WorkerAnt(AntBasicMovement):
    def __init__(self, x, y, environment, colony):
        super().__init__(x, y, environment)
        self.colony = colony
        self.carrying_food = False
        self.last_position = None
        self.timeout_counter = 0
        # how long until ants head back to nest
        self.timeout_limit = 500
        # saves recent position to stop ants going in circles
        self.recent_positions = []
        self.memory_limit = 5

    def act(self, occupied_squares, all_ants):

        # adds 1 to timer
        self.timeout_counter += 1

        # movement happens every 5 steps
        if self.steps_since_last_move < 5:
            self.steps_since_last_move += 1
            return
        self.steps_since_last_move = 0

        # time out counter making ants return to the nest
        if self.timeout_counter > self.timeout_limit:
            nest_x, nest_y = self.environment.nests[self.colony]
            if (self.x, self.y) != (nest_x, nest_y):
                self.move_towards(nest_x, nest_y, occupied_squares)
                return
            else:
                self.timeout_counter = 0

        # if ant is carrying food, return to nest
        if self.carrying_food:
            # go to correct nest for the colony
            nest_x, nest_y = self.environment.nests[self.colony]
            # if at the nest drop the food & reset timer
            if (self.x, self.y) == (nest_x, nest_y):
                self.carrying_food = False
                self.environment.food_returned[self.colony] += 1
                self.timeout_counter = 0
            else:
                self.move_towards(nest_x, nest_y, occupied_squares)
        else:
            # when not carrying food, follow pheromone trails to find food
            potential_moves = [
                ((self.x + dx) % self.environment.width, (self.y + dy) % self.environment.height)
                for dx, dy in [
                    (0, 1), (1, 0), (0, -1), (-1, 0),
                    (1, 1), (-1, -1), (1, -1), (-1, 1)
                ]
            ]
            # filtering out bad moves
            valid_moves = [
                pos for pos in potential_moves
                if pos != self.last_position
                   and pos not in self.recent_positions
                   and not self.environment.grid[pos[1]][pos[0]]["hazard"]

                    # follow colony trail
                   and self.environment.grid[pos[1]][pos[0]]["pheromone"].get(self.colony, 0) > 0
            ]

            # within the valid moves choose the best move
            if valid_moves:
                # best move is one with highest pheromone level and moving further away from nest
                best_move = max(valid_moves, key=lambda pos: (
                    self.environment.grid[pos[1]][pos[0]]["pheromone"].get(self.colony, 0),
                    self.euclidean_distance(pos[0], pos[1], self.environment.nests[self.colony][0], self.environment.nests[self.colony][1])
                ))
                self.last_position = (self.x, self.y)
                self.x, self.y = best_move

                # updates last five positions
                self.recent_positions.append((self.x, self.y))
                if len(self.recent_positions) > self.memory_limit:
                    self.recent_positions.pop(0)

                # check if food is found
                if self.environment.is_food(self.x, self.y):
                    self.carrying_food = True
                    self.environment.collect_food(self.x, self.y)
                    self.last_position = None
            else:
                # if no pheromone trails move randomly
                self.move_randomly(occupied_squares)
                self.last_position = (self.x, self.y)

class AttackAnt(AntBasicMovement):
    def __init__(self, x, y, environment, colony):
        super().__init__(x, y, environment)
        self.colony = colony
        # range for attacks
        self.attack_radius = 2
        # distance they follow scout
        self.follow_distance = 5
        self.in_final_duel = False

    def act(self, occupied_squares, all_ants):

        # movement every 3 steps
        if self.steps_since_last_move < 3:
            self.steps_since_last_move += 1
            return
        self.steps_since_last_move = 0

        # check if only attackers
        self.check_only_attackers_left(all_ants)

        # change state to find and attack
        if self.only_attackers_left:
            enemy_ant = self.find_nearest_enemy_attacker(all_ants)
            if enemy_ant:
                # moves towards enemy ant
                self.move_towards(enemy_ant.x, enemy_ant.y, occupied_squares)
                if self.euclidean_distance(self.x, self.y, enemy_ant.x, enemy_ant.y) <= self.attack_radius:
                    self.attack([enemy_ant])
            else:
                self.move_randomly(occupied_squares)
        else:
            # protection state
            # if enemy attack
            enemy_ants = self.detect_enemies(all_ants)
            if enemy_ants:
                self.attack(enemy_ants)
            else:
                # locate nearest scout to defend
                scout_position = self.find_scout_position(all_ants)
                if scout_position:
                    distance = self.euclidean_distance(self.x, self.y, scout_position[0], scout_position[1])
                    # keeps within distance of 5
                    if distance > self.follow_distance:
                        self.move_towards(scout_position[0], scout_position[1], occupied_squares)
                    else:
                        self.move_randomly(occupied_squares)
                else:
                    self.move_randomly(occupied_squares)

    # check own colony if only attackers are left
    def check_only_attackers_left(self, all_ants):
        colony_ants = [ant for ant in all_ants if ant.colony == self.colony]
        self.only_attackers_left = all(isinstance(ant, AttackAnt) for ant in colony_ants)

    # finds nearest enemy ant
    def find_nearest_enemy_attacker(self, all_ants):
        nearest_enemy = None
        min_distance = float('inf')
        for ant in all_ants:
            if isinstance(ant, AttackAnt) and ant.colony != self.colony:
                distance = self.euclidean_distance(self.x, self.y, ant.x, ant.y)
                if distance < min_distance:
                    nearest_enemy = ant
                    min_distance = distance
        return nearest_enemy

    # detects all ants in attack radius, checks if enemy
    def detect_enemies(self, all_ants):
        enemies = []
        for ant in all_ants:
            if ant.colony != self.colony:
                distance = self.euclidean_distance(self.x, self.y, ant.x, ant.y)
                if distance <= self.attack_radius:
                    enemies.append(ant)
        return enemies

    # finds closest scout in colony
    def find_scout_position(self, all_ants):
        for ant in all_ants:
            if isinstance(ant, ScoutAnt) and ant.colony == self.colony:
                return ant.x, ant.y
        return None

    # attacks first enemy in list
    def attack(self, enemies):
        target = enemies[0]
        print(f"attack ant from colony {self.colony} attacked enemy at: ({target.x}, {target.y})!")
        target.alive = False
