import pygame

class WorldObject:
    """
    Handles the visual representation and update loop of the game world.
    It bridges the simulation logic (World) with the rendering engine (Pygame).
    """
    def __init__(self, world, cell_size=10):
        """
        Initializes the WorldObject.

        Args:
            world (World): The simulation world instance containing grid and cells.
            cell_size (int): The pixel size of each grid cell for rendering.
        """
        self.world = world
        self.cell_size = cell_size
        self.accumulator = 0.0
        self.step_time = 0.1  # Time in seconds between simulation steps
        
        # Init font
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 14)

    def update(self, dt):
        """
        Updates the simulation based on delta time.
        Accumulates time to maintain a fixed time step for the physics/logic.

        Args:
            dt (float): Time in seconds since the last frame.
        """
        self.accumulator += dt
        while self.accumulator >= self.step_time:
            self.world.step()
            self.accumulator -= self.step_time

    def draw(self, screen):
        """
        Renders the world state to the screen.
        
        Args:
            screen (pygame.Surface): The target surface to draw onto.
        """
        # ---- Step 4: Draw the world (nutrients) ----
        for x in range(self.world.width):
            for y in range(self.world.height):
                chem = self.world.grid[x][y]
                
                # Visualize nutrient 'A' concentration as green intensity
                # Scale: 20 intensity per unit, capped at 255
                a = int(min(255, chem.get("A", 0) * 20))
                color = (0, a, 0)

                rect = pygame.Rect(
                    x * self.cell_size,
                    y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                pygame.draw.rect(screen, color, rect)

        # ---- Step 5: Draw the cells ----
        # Iterate through all cells in the world and draw the living ones
        for cell in self.world.cells:
            if not cell.alive:
                continue

            # Calculate center position based on grid coordinates
            cx = cell.x * self.cell_size + self.cell_size // 2
            cy = cell.y * self.cell_size + self.cell_size // 2
            
            # Radius depends on energy level, minimum 2 pixels
            mass = sum(cell.chemistry.values())
            radius = max(2, int(mass))
            energy_color=min(255, int(cell.energy*20))
            color=(energy_color, energy_color, 255)

            pygame.draw.circle(screen, color, (cx, cy), radius)

        # ---- Step 6: Draw UI Dashboard ----
        # Draw background panel
        ui_y = self.world.height * self.cell_size
        ui_rect = pygame.Rect(0, ui_y, screen.get_width(), 100)
        pygame.draw.rect(screen, (30, 30, 30), ui_rect)
        
        # Calculate stats
        alive_cells = [c for c in self.world.cells if c.alive]
        count = len(alive_cells)
        
        # Line 1: Summary
        summary_str = f"Alive Cells: {count} | Total Cells: {len(self.world.cells)}"
        summary_text = self.font.render(summary_str, True, (255, 255, 255))
        screen.blit(summary_text, (10, ui_y + 10))
        
        # Line 2+: Detail of first few live cells
        y_offset = 30
        for i, cell in enumerate(alive_cells[:3]): # Show stats for up to 3 cells
            chem_vals = [f"{k}:{v:.1f}" for k,v in cell.chemistry.items() if v > 0.1]
            chem_str = ", ".join(chem_vals)
            
            # Division status safe access
            div_status = "YES" if getattr(cell, 'ready_to_divide', False) else "NO"
            
            info = f"Cell #{i}: E={cell.energy:.1f} | Age={cell.age} | Chem={{ {chem_str} }} | Div={div_status}"
            detail_text = self.font.render(info, True, (200, 200, 200))
            screen.blit(detail_text, (20, ui_y + y_offset))
            y_offset += 20