import pygame
import colorsys
import numpy as np

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

        # Pre-calculated background color
        self.bg_color = (20, 40, 60) # Deep Ocean Blue

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
        # ---- Step 4: Draw Background ----
        screen.fill(self.bg_color)

        # ---- Step 5: Draw Nutrients (Subtle additive) ----
        # To avoid massive loop overhead, we only iterate where logical. 
        # But for strictly correct grid rendering, we iterate. 
        # For optimization, we rely on the fact that empty space is common? 
        # Actually, in this sim, diffusion spreads things everywhere. 
        # We will iterate, but keep math simple.
        
        chem_A = self.world.chemistry.get("A")
        chem_B = self.world.chemistry.get("B")
        
        # Optimization: Create a surface for nutrients if performance hits, but for now direct draw.
        # We will only draw if concentration is significant (> 0.1) to save calls.
        
        rows = self.world.rows
        cols = self.world.cols
        cell_size = self.cell_size
        
        # We can scan the arrays in numpy to find indices > threshold, but that might be complex to wire to rects efficiently in Pygame without blit_array.
        # Let's stick to the double loop but optimize checks.
        
        # Draw "plankton" (A) - Cyan/Greenish
        if chem_A is not None:
            # Vectorized index finding? 
            # indices = np.argwhere(chem_A > 0.5) 
            # This is much faster than python loop for sparse data.
            # For dense data, blit_array is better. Let's try argwhere for now as nutrients might be clumpy.
            
            indices = np.argwhere(chem_A > 0.5)
            for x, y in indices:
                val = chem_A[x, y]
                # Alpha simulation: blend with bg
                # Ocean (20, 40, 60) + Green (0, 255, 100) * val
                intensity = min(1.0, val / 20.0)
                
                # Simple additive tint
                color = (
                    min(255, 20 + int(0 * intensity)),
                    min(255, 40 + int(100 * intensity)),
                    min(255, 60 + int(60 * intensity))
                )
                if intensity > 0.05:
                     pygame.draw.rect(screen, color, (x*cell_size, y*cell_size, cell_size, cell_size))

        # Draw "waste" (B) - Murky Purple
        if chem_B is not None:
             indices = np.argwhere(chem_B > 0.5)
             for x, y in indices:
                val = chem_B[x, y]
                # Waste 'B' - High Contrast Rust/Orange (Sediment)
                if val > 0.05: # Lower threshold
                    # Much higher sensitivity: divide by 2.0 instead of 20.0 so we see small amounts
                    intensity = min(1.0, val / 2.0) 
                    
                    # Bright Rust/Orange: (220, 100, 50)
                    # We want it to be visible even at low intensity.
                    # Base color (visible brown) + intensity brightness
                    color = (
                        min(255, 100 + int(155 * intensity)), 
                        min(255, 50 + int(100 * intensity)),
                        min(255, 20 + int(50 * intensity))
                    )
                    
                    pygame.draw.rect(screen, color, (x*cell_size, y*cell_size, cell_size, cell_size))


        # ---- Step 6: Draw Cells (Organic) ----
        for cell in self.world.cells:
            if not cell.alive:
                continue

            color = self.get_cell_color(cell)
            
            # Draw cell
            rect = pygame.Rect(
                cell.x * self.cell_size,
                cell.y * self.cell_size,
                self.cell_size,
                self.cell_size
            )
            pygame.draw.rect(screen, color, rect)
            
        # ---- Step 7: UI ----
        self.draw_ui(screen)

    def get_cell_color(self, cell):
        """
        Generates an organic color based on the cell's genome properties.
        
        Properties mapping:
        - Base: Pale Organic Green/White (Hue=0.3)
        - High Cost (Metabolic expensive) -> Shifts hue towards Yellow/Orange (Hue decreases)
        - High Yield (High energy output) -> Increases Brightness/Sat
        - Number of genes -> Complexity -> Saturation?
        """
        genes = cell.genoma.genes
        if not genes:
            return (200, 200, 200) # Dead/Empty gray

        avg_cost = sum(g.cost for g in genes) / len(genes)
        avg_yield = sum(g.energy_yield for g in genes) / len(genes)
        
        # Base Hue: 0.35 (Green-Cyan)
        # Cost effect: Higher cost (e.g. 1.0) pushes hull down to 0.1 (Orange)
        # Cost range approx 0.1 to 1.0
        
        hue = 0.35 - (avg_cost * 0.2) # Max shift to ~0.15
        hue = max(0.0, min(1.0, hue))
        
        # Saturation: 
        # Healthy/High Yield = More saturated? Or more white?
        # Let's say High Yield = Brighter (Value), Lower Saturation (Glowing White)
        # Low Yield = Dimmer
        
        # Yield range approx 0 to 5
        sat = 0.6 - (avg_yield * 0.05)
        sat = max(0.2, min(1.0, sat))
        
        val = 0.7 + (avg_yield * 0.05)
        val = max(0.4, min(1.0, val))
        
        r, g, b = colorsys.hsv_to_rgb(hue, sat, val)
        return (int(r*255), int(g*255), int(b*255))

    def draw_ui(self, screen):
        # Draw background panel
        ui_y = self.world.rows * self.cell_size
        ui_rect = pygame.Rect(0, ui_y, screen.get_width(), 100)
        pygame.draw.rect(screen, (10, 20, 30), ui_rect)
        
        # Calculate stats
        alive_cells = [c for c in self.world.cells if c.alive]
        count = len(alive_cells)
        
        # Line 1: Summary
        summary_str = f"Alive Cells: {count} | Total Cells: {len(self.world.cells)}"
        summary_text = self.font.render(summary_str, True, (200, 220, 255))
        screen.blit(summary_text, (10, ui_y + 10))
        
        # Line 2+: Detail of first few live cells
        y_offset = 30
        for i, cell in enumerate(alive_cells[:3]): 
            # Division status safe access
            div_status = "YES" if getattr(cell, 'ready_to_divide', False) else "NO"
            
            # Simple stats for UI
            info = f"Cell #{i}: E={cell.energy:.1f} | Age={cell.age}"
            detail_text = self.font.render(info, True, (150, 180, 200))
            screen.blit(detail_text, (20, ui_y + y_offset))
            y_offset += 20