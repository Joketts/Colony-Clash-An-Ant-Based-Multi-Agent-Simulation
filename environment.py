import random

class Environment:
    def __init__(self, width=50, height=50):
        self.width = width
        self.height = height
        self.grid = [
            [{"food": 0, "durability": 0, "hazard": False, "pheromone": {1: 0, 2: 0}} for _ in range(width)]
            for _ in range(height)
        ]
        self.nests = {1: (width // 4, height // 4), 2: (3 * width // 4, 3 * height // 4)}  # Two nests
        self.pheromone_trails = {1: {}, 2: {}}  # Separate trails for colonies
        self.food_returned = {1: 0, 2: 0}  # Food counters for each colony


    def spawn_food(self, num_food=15):
        """Spawn food randomly across the grid."""
        for _ in range(num_food):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.grid[y][x]["food"] = random.randint(1, 3)  # Food quantity
            self.grid[y][x]["durability"] = random.randint(2, 8)  # Food durability

    def regenerate_food(self, regen_rate=0.0000005):
        """Regenerate food sources over time."""
        import random
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x]["food"] == 0 and not self.grid[y][x]["hazard"]:
                    if random.random() < regen_rate:  # Small chance to regenerate food
                        self.grid[y][x]["food"] = random.randint(1, 5)

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
                    print(f"Clearing pheromone trail for food at {food_location}")
                    for trail_x, trail_y in self.pheromone_trails[food_location]:
                        # Check if this cell is part of another food trail
                        is_part_of_other_trail = any(
                            (trail_x, trail_y) in trail
                            for other_food, trail in self.pheromone_trails.items()
                            if other_food != food_location
                        )
                        # Only clear if not part of another trail
                        if not is_part_of_other_trail:
                            print(f"Clearing pheromone at ({trail_x}, {trail_y})")
                            if isinstance(self.grid[trail_y][trail_x]["pheromone"], dict):
                                self.grid[trail_y][trail_x]["pheromone"] = {1: 0, 2: 0}  # Reset pheromones
                            else:
                                print(f"Warning: Pheromone at ({trail_x}, {trail_y}) is not a dictionary. Resetting.")
                                self.grid[trail_y][trail_x]["pheromone"] = {1: 0, 2: 0}

                            if food_location in self.pheromone_trails:
                                del self.pheromone_trails[food_location]
                            else:
                                print(f"Trail for {food_location} already deleted by another ant.")
                else:
                    print(f"No pheromone trail found for food at {food_location}")

    def is_food(self, x, y):
        return self.grid[y][x]["food"] > 0

    def add_hazards(self, num_hazards=500, safe_zone_radius=3):
        """Add random hazard zones to the grid, avoiding safe zones around nests."""
        import random

        # Calculate safe zones around each nest
        safe_zones = set()
        for nest_x, nest_y in self.nests.values():
            for dx in range(-safe_zone_radius, safe_zone_radius + 1):
                for dy in range(-safe_zone_radius, safe_zone_radius + 1):
                    safe_zones.add(((nest_x + dx) % self.width, (nest_y + dy) % self.height))

        # Add hazards while avoiding safe zones
        for _ in range(num_hazards):
            while True:
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                if (x, y) not in safe_zones and not self.grid[y][x].get("hazard"):
                    self.grid[y][x]["hazard"] = True
                    break

    def add_pheromone(self, x, y, colony, amount=50, food_location=None, lifetime=1050):
        """Add pheromones to the grid for a specific colony and track them by food location."""
        cell = self.grid[y][x]

        if not isinstance(cell["pheromone"], dict):  # Ensure pheromone is a dictionary
            cell["pheromone"] = {1: 0, 2: 0}

        if colony not in cell["pheromone"]:
            cell["pheromone"][colony] = 0

        cell["pheromone"][colony] += amount
        cell["pheromone"][colony] = min(cell["pheromone"][colony], 255)

        if food_location:
            if food_location not in self.pheromone_trails:
                self.pheromone_trails[food_location] = set()
            self.pheromone_trails[food_location].add((x, y))

        # Add a lifetime tracker for the pheromone
        if "lifetime" not in cell or cell["lifetime"] < lifetime:
            cell["lifetime"] = lifetime
    def update_pheromone_lifetime(self):
        """Reduce pheromone lifetime and remove expired pheromones."""
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if "lifetime" in cell and cell["lifetime"] > 0:
                    cell["lifetime"] -= 1
                    if cell["lifetime"] == 0:
                        cell["pheromone"] = {1: 0, 2: 0}  # Reset pheromone correctly
                        if (x, y) in self.pheromone_trails:
                            # Remove this location from any food-linked pheromone trail
                            for food_location, trail in self.pheromone_trails.items():
                                if (x, y) in trail:
                                    trail.remove((x, y))
                            # Clean up empty trails
                            self.pheromone_trails = {k: v for k, v in self.pheromone_trails.items() if v}
