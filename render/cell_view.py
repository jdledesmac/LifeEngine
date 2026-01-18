from engine.basic_objects import GameObject

class CellView(GameObject):
    def __init__(self, x, y, cell):
        # Initialize GameObject with position and size
        super().__init__(x, y, 10, 10, color=(0, 255, 0))
        self.cell = cell
    
    def update(self, dt):
        # Delegate logic to the cell
        self.cell.step()
        
        # Update visual state based on logic state
        if not self.cell.alive:
            self.color = (50, 50, 50) # Dark gray when dead
