import random

class Environment:
    def __init__(self, width=50, height=50):
        self.width = width
        self.height = height

        # creates 2D list of dictionaries, keeps track of both colonies pheromone trails
        self.grid = [
            [{"food": 0, "hazard": False, "pheromone": {1: 0, 2: 0}} for _ in range(width)]
            for _ in range(height)
        ]
        # sets nets position
        self.nests = {1: (width // 4, height // 4), 2: (3 * width // 4, 3 * height // 4)}
        # sets each colonies pheromone trails
        self.pheromone_trails = {1: {}, 2: {}}
        # for keeping track of food for both colonies
        self.food_returned = {1: 0, 2: 0}

    # spawns 15 food randomly across the grid
    def spawn_food(self, num_food=15):
        for _ in range(num_food):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            # sets random food amount to cell
            self.grid[y][x]["food"] = random.randint(2, 5)

    # small change to regen food not on hazard locations
    def regenerate_food(self, regen_rate=0.0000005):
        import random
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x]["food"] == 0 and not self.grid[y][x]["hazard"]:
                    if random.random() < regen_rate:
                        self.grid[y][x]["food"] = random.randint(2, 5)

    # removed food when collected also removes pheromone trail
    def collect_food(self, x, y):
        if self.is_food(x, y):
            self.grid[y][x]["food"] -= 1
            if self.grid[y][x]["food"] <= 0:
                self.grid[y][x]["food"] = 0
                food_location = (x, y)
                if food_location in self.pheromone_trails:
                    print(f"clearing pheromone trail at location: {food_location}")
                    for trail_x, trail_y in self.pheromone_trails[food_location]:
                        # checks if its overlap
                        is_part_of_other_trail = any(
                            (trail_x, trail_y) in trail
                            for other_food, trail in self.pheromone_trails.items()
                            if other_food != food_location
                        )
                        # clears trail where cells don't overlap
                        if not is_part_of_other_trail:
                            print(f"clearing pheromones at: ({trail_x}, {trail_y})")
                            if isinstance(self.grid[trail_y][trail_x]["pheromone"], dict):
                                self.grid[trail_y][trail_x]["pheromone"] = {1: 0, 2: 0}

                            # removes food location from pheromones trails
                            if food_location in self.pheromone_trails:
                                del self.pheromone_trails[food_location]
                            else:
                                print(f" trail at  {food_location} deleted already")
                else:
                    print(f"no trail found at this point: {food_location}")

    # checks if cell contains food
    def is_food(self, x, y):
        return self.grid[y][x]["food"] > 0

    # adds 500 hazards doesn't spawn them around the nest
    def add_hazards(self, num_hazards=500, safe_zone_radius=3):

        # calculates the safe zone around the nest
        safe_zones = set()
        for nest_x, nest_y in self.nests.values():
            for dx in range(-safe_zone_radius, safe_zone_radius + 1):
                for dy in range(-safe_zone_radius, safe_zone_radius + 1):
                    # adds safe coords to safe_zone
                    safe_zones.add(((nest_x + dx) % self.width, (nest_y + dy) % self.height))

        # adds in hazards avoiding safe zone and other hazard cells
        for _ in range(num_hazards):
            while True:
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                if (x, y) not in safe_zones and not self.grid[y][x].get("hazard"):
                    self.grid[y][x]["hazard"] = True
                    break

    # adds pheromones to grid taking in colony and tracks by food location, sets
    def add_pheromone(self, x, y, colony, amount=50, food_location=None, timeleft=1050):

        # accesses cell
        cell = self.grid[y][x]

        # initializes pheromone value for the colony if is doesn't already have one
        if colony not in cell["pheromone"]:
            cell["pheromone"][colony] = 0

        # adds pheromone value, capping value at 255
        cell["pheromone"][colony] += amount
        cell["pheromone"][colony] = min(cell["pheromone"][colony], 255)

        # connects the trail to the food location
        if food_location:
            if food_location not in self.pheromone_trails:
                self.pheromone_trails[food_location] = set()
            self.pheromone_trails[food_location].add((x, y))

        # updates time left for each cell
        if "timeleft" not in cell or cell["timeleft"] < timeleft:
            cell["timeleft"] = timeleft

    # reduces time left for pheromone trail cells
    def update_pheromone_timeleft(self):
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if "timeleft" in cell and cell["timeleft"] > 0:
                    cell["timeleft"] -= 1
                    if cell["timeleft"] == 0:
                        cell["pheromone"] = {1: 0, 2: 0}

                        # deletes trail section
                        if (x, y) in self.pheromone_trails:
                            for food_location, trail in self.pheromone_trails.items():
                                if (x, y) in trail:
                                    trail.remove((x, y))

                            # removes empty trails from dictionary
                            self.pheromone_trails = {k: v for k, v in self.pheromone_trails.items() if v}
