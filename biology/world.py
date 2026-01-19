import copy
import random
import warnings
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
    def __init__(self, width, height, cell_size):
        """
        Initializes the world with a specific grid size.

        Args:
            width (int): Grid width.
            height (int): Grid height.
        """
        self.width = width
        self.height = height
        self.cell_size=cell_size

        self.cols=width//cell_size
        self.rows=height//cell_size
        
        
        self.chemistry = [[{} for _ in range(self.rows)] for _ in range(self.cols)] 

        self.cells = []

    def seed(self, mol, amount):
        for x in range(self.cols):
            for y in range(self.rows):
                self.chemistry[x][y][mol] = amount



    def seed_clusters(self, mol, total_amount, num_clusters=5):
        """
        Seeds nutrients in concentrated clusters to form 'rich zones' and 'deserts'.
        
        Args:
            mol (str): The molecule key (e.g. "A").
            total_amount (float): The total budget of the molecule to distribute.
            num_clusters (int): How many distinct clusters to create.
        """
        if num_clusters < 1: return
        
        amt_per_cluster = total_amount / num_clusters
        
        for _ in range(num_clusters):
            # Pick a center
            cx = random.randint(0, self.cols - 1)
            cy = random.randint(0, self.rows - 1)
            
            # Spread geometry: 
            # We will perform 'splats' of nutrients around the center.
            # Radius approx 1/6th of min dimension
            radius = list(range(max(1, min(self.cols, self.rows) // 6))) # dummy usage to ensure int? No, just calculation.
            radius = max(1, min(self.cols, self.rows) // 6)

            # Number of splats/drops
            drops = 50
            drop_val = amt_per_cluster / drops
            
            for _ in range(drops):
                # Random offset within radius
                # Using gauss for natural falloff
                ox = int(random.gauss(cx, radius / 2))
                oy = int(random.gauss(cy, radius / 2))
                
                # Clamp to grid
                ox = max(0, min(self.cols - 1, ox))
                oy = max(0, min(self.rows - 1, oy))
                
                # Add to grid
                self.chemistry[ox][oy][mol] = self.chemistry[ox][oy].get(mol, 0) + drop_val

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
        new_grid = copy.deepcopy(self.chemistry)

        for x in range(self.cols):
            for y in range(self.rows):
                for mol, amt in self.chemistry[x][y].items():
                    # Calculate amount to spread to 4 neighbors
                    spread = amt * rate / 4

                    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                        nx, ny = x+dx, y+dy
                        
                        # Boundary check
                        if 0 <= nx < self.cols and 0 <= ny < self.rows:
                            # Add spread amount to neighbor in new grid
                            new_grid[nx][ny][mol] = new_grid[nx][ny].get(mol, 0) + spread
                            # Subtract spread amount from source in new grid
                            new_grid[x][y][mol] -= spread

        self.chemistry = new_grid    
    
    def exchange(self, cell, rate=0.5):
        """
        Handles the exchange of chemicals between a cell and its environment.
        Cells absorb nutrients from the grid location they occupy.

        Args:
            cell (Cell): The cell interacting with the environment.
            rate (float): Percentage of available nutrients absorbed by the cell.
        """
        cx, cy = self.cell_tile(cell)
        env = self.chemistry[cx][cy]

        for mol, amt in env.items():
            taken = amt * rate
            # Add to cell's internal chemistry
            cell.chemistry[mol] = cell.chemistry.get(mol, 0) + taken
            # Remove from environment
            env[mol] -= taken

    def release_waste(self, cell):
        """
        Moves waste products from the cell to the environment.
        """
        cx, cy = self.cell_tile(cell)
        tile = self.chemistry[cx][cy]
        # Release 'B' as it is toxic
        if "B" in cell.chemistry:
            amount = cell.chemistry.pop("B")
            tile["B"] = tile.get("B", 0) + amount

    def cell_tile(self,cell):
        return int(cell.x), int(cell.y)   

    def move_cell(self, cell, rate=0.05):
        if random.random() > rate:
            return
        dx, dy =random.choice([(-1,0),(1,0),(0,-1),(0,1)])
        new_x = cell.x + dx
        new_y = cell.y + dy
        #world limits
        new_x= max(0, min(self.cols-1, new_x))
        new_y=max(0, min(self.rows-1, new_y))   
        cell.x = new_x
        cell.y = new_y


    def step(self):
        """
        advances the world state by one step.
        1. Diffuses chemicals.
        2. Processes cell metabolism and environment exchange.
        """
        
        #world changes
        self.diffuse()

        new_cells = []

        #cell reacts to world 
        for cell in self.cells:
            # 2.1 Intercambio
            self.exchange(cell)

            # 2.2 Metabolismo interno
            cell.step()
            
            # Si murió, se elimina (no se agrega a new_cells)
            if not cell.alive:
                continue
            
            #passive movement
            self.move_cell(cell)
            
            # 2.3 Liberación de residuos
            self.release_waste(cell)
            
            # 2.4 División
            if cell.ready_to_divide:
                daughters = self.divide_cell(cell)
                new_cells.extend(daughters)
            else:
                new_cells.append(cell)

        self.cells = new_cells

    def divide_cell(self, cell):
        # copiar genoma
        g1 = copy.deepcopy(cell.genoma)
        g2 = copy.deepcopy(cell.genoma)

        # mutaciones independientes
        g1.mutate()
        g2.mutate()

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
        c2.x = max(0, min(self.cols-1, x+dx))
        c2.y = max(0, min(self.rows-1, y+dy))

        return [c1, c2]