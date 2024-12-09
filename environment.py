import random

class Environment:
    def __init__(self, width=50, height=50):
        self.width = width
        self.height = height
        self.grid = [
            [{"food": 0, "durability": 0, "hazard": False, "pheromone": 0} for _ in range(width)]
            for _ in range(height)
        ]
        self.nest = (width // 2, height // 2)
        self.pheromone_trails = {}

    def spawn_food(self, num_food=15):
        """Spawn food randomly across the grid."""
        for _ in range(num_food):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.grid[y][x]["food"] = random.randint(1, 3)  # Food quantity
            self.grid[y][x]["durability"] = random.randint(2, 5)  # Food durability

    def regenerate_food(self, regen_rate=0.000001):
        """Regenerate food sources over time."""
        import random
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x]["food"] == 0 and not self.grid[y][x]["hazard"]:
                    if random.random() < regen_rate:  # Small chance to regenerate food
                        self.grid[y][x]["food"] = random.randint(1, 5)

    def is_nest(self, x, y):
        return (x, y) == self.nest

    def is_food(self, x, y):
        return self.grid[y][x]["food"] > 0

    def get_durability(self, x, y):
        """Get the current durability of food at a location."""
        return self.grid[y][x]["durability"]

    def add_hazards(self, num_hazards=300):
        """Add random hazard zones to the grid."""
        import random
        for _ in range(num_hazards):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.grid[y][x]["hazard"] = True

    def collect_food(self, x, y):
        """Reduce the durability of food and remove it if exhausted."""
        if self.is_food(x, y):
            self.grid[y][x]["durability"] -= 1
            if self.grid[y][x]["durability"] <= 0:
                # Remove food and reset durability
                self.grid[y][x]["food"] = 0
                self.grid[y][x]["durability"] = 0
                # Clear pheromone trail if linked to this food
                food_location = (x, y)
                if food_location in self.pheromone_trails:
                    for trail_x, trail_y in self.pheromone_trails[food_location]:
                        self.grid[trail_y][trail_x]["pheromone"] = 0
                    del self.pheromone_trails[food_location]
                    print(f"Pheromone trail cleared for food at ({x}, {y})")

    def add_pheromone(self, x, y, amount=1, food_location=None):
        """Add pheromones and track the trail."""
        self.grid[y][x]["pheromone"] += amount
        self.grid[y][x]["pheromone"] = min(self.grid[y][x]["pheromone"], 255)
        if food_location is not None:
            if food_location not in self.pheromone_trails:
                self.pheromone_trails[food_location] = set()
            self.pheromone_trails[food_location].add((x, y))

