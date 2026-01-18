import copy
import random
from .cell import Cell

class World:
    """
    Represents the game world as a grid where chemical reactions and cell life occur.
    
    Attributes:
        width (int): The width of the grid.
        height (int): The height of the grid.
        grid (list): A 2D list of dictionaries representing chemical concentrations at each coordinate.
        cells (list): A list of Cell objects currently traversing the world.
    """
    def __init__(self, width, height):
        """
        Initializes the world with a specific grid size.

        Args:
            width (int): Grid width.
            height (int): Grid height.
        """
        self.width = width
        self.height = height
        
        # Initialize grid with empty dictionaries for chemicals
        self.grid = [[{} for _ in range(height)] for _ in range(width)] 

        self.cells = []

    def seed_nutrients(self, mol, amount, density=0.5):
        """
        Randomly distributes a chemical molecule across the grid.

        Args:
            mol (str): The identifier of the molecule/chemical.
            amount (float): The amount of chemical to place at each seeded location.
            density (float): The probability (0.0 to 1.0) of a location being seeded.
        """
        for x in range(self.width):
            for y in range(self.height):
                if random.random() < density:
                    self.grid[x][y][mol] = amount    

    def add_cell(self, cell, x, y):
        """
        Places a cell into the world at a specific coordinate.

        Args:
            cell (Cell): The cell object to add.
            x (int): X coordinate.
            y (int): Y coordinate.
        """
        cell.x = x
        cell.y = y
        self.cells.append(cell)

    def diffuse(self, rate=0.1):
        """
        Simulates the diffusion of chemicals across the grid.
        Chemicals spread from high concentration to neighbors.
        
        Args:
            rate (float): The rate at which chemicals spread (0.0 to 1.0).
        """
        # Create a deep copy to apply changes simultaneously (cellular automata style)
        new_grid = copy.deepcopy(self.grid)

        for x in range(self.width):
            for y in range(self.height):
                for mol, amt in self.grid[x][y].items():
                    # Calculate amount to spread to 4 neighbors
                    spread = amt * rate / 4

                    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                        nx, ny = x+dx, y+dy
                        
                        # Boundary check
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            # Add spread amount to neighbor in new grid
                            new_grid[nx][ny][mol] = new_grid[nx][ny].get(mol, 0) + spread
                            # Subtract spread amount from source in new grid
                            new_grid[x][y][mol] -= spread

        self.grid = new_grid    
    
    def exchange(self, cell, rate=0.5):
        """
        Handles the exchange of chemicals between a cell and its environment.
        Cells absorb nutrients from the grid location they occupy.

        Args:
            cell (Cell): The cell interacting with the environment.
            rate (float): Percentage of available nutrients absorbed by the cell.
        """
        env = self.grid[cell.x][cell.y]

        for mol, amt in env.items():
            taken = amt * rate
            # Add to cell's internal chemistry
            cell.chemistry[mol] = cell.chemistry.get(mol, 0) + taken
            # Remove from environment
            env[mol] -= taken

    def step(self):
        """
        advances the world state by one step.
        1. Diffuses chemicals.
        2. Processes cell metabolism and environment exchange.
        """
        self.diffuse()

        new_cells = []

        for cell in self.cells:
            if not cell.alive:
                continue    
            
            self.exchange(cell)
            # Delegate metabolic step to the cell itself
            cell.step()
            
            if cell.ready_to_divide:
                daughters=self.divide_cell(cell)
                new_cells.extend(daughters)
            else:
                new_cells.append(cell)

        self.cells = new_cells

    def divide_cell(self, cell):
        # copiar genoma
        g1 = copy.deepcopy(cell.genoma)
        g2 = copy.deepcopy(cell.genoma)

        # mutaciones independientes
        for gen in g1.genes:
            g1.mutate(gen)
        for gen in g2.genes:
            g2.mutate(gen)

        # crear hijas
        c1 = Cell(g1)
        c1.ready_to_divide = False
        c1.division_cooldown = 5
        c1.energy = cell.energy * 0.45
        c2 = Cell(g2)
        c2.ready_to_divide = False
        c2.division_cooldown = 5
        c2.energy = cell.energy * 0.45

        # repartir energía
        c1.energy = cell.energy / 2
        c2.energy = cell.energy / 2

        # repartir química
        for mol, amt in cell.chemistry.items():
            half = amt / 2
            c1.chemistry[mol] = half
            c2.chemistry[mol] = amt - half

        # posición espacial
        x, y = cell.x, cell.y
        c1.x, c1.y = x, y

        # intentar poner la otra cerca
        dx, dy = random.choice([(-1,0),(1,0),(0,-1),(0,1)])
        c2.x = max(0, min(self.width-1, x+dx))
        c2.y = max(0, min(self.height-1, y+dy))

        return [c1, c2]