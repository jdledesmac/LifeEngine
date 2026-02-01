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

        # ---- Step 5: Draw Chemicals (Mixed) ----
        # Mix Nutrients (A) and Waste (B)
        chem_A = self.world.chemistry.get("A")
        chem_B = self.world.chemistry.get("B")

        if chem_A is not None or chem_B is not None:
            # Create zero grids if they don't exist
            if chem_A is None: chem_A = np.zeros((self.world.cols, self.world.rows))
            if chem_B is None: chem_B = np.zeros((self.world.cols, self.world.rows))

            # Threshold to display
            threshold = 0.05
            
            # Find indices where there is something to draw
            # Use 'or' logic: (A > t) | (B > t)
            active_indices = np.argwhere((chem_A > threshold) | (chem_B > threshold))
            
            for x, y in active_indices:
                val_a = chem_A[x, y]
                val_b = chem_B[x, y]
                
                total = val_a + val_b
                if total <= 0: continue
                
                # Ratios
                ratio_a = val_a / total
                ratio_b = val_b / total
                
                # Base Colors
                # Nutrient: Brilliant Blue/Cyan (0, 200, 255)
                # Waste: Brown/Rust (160, 82, 45)
                
                # Mix colors
                r = ratio_a * 0   + ratio_b * 160
                g = ratio_a * 200 + ratio_b * 82
                b = ratio_a * 255 + ratio_b * 45
                
                # Intensity/Brightness based on total concentration.
                # Adjust scale factor so common amounts look good.
                # Assuming max concentrations around 20-50 usually?
                intensity = min(1.0, total / 20.0)
                
                # Apply intensity to blend with background or simply scale the color
                # If we want "opaque" for low concentration, we might just reduce brightness.
                # Let's map 0..1 intensity to a color scale.
                
                # Final color = MixedColor * Intensity + Background * (1-Intensity) ?
                # Or just simple brightness scaling. User said "more intense or lighter".
                # Let's try simple additive-like brightness but capped.
                
                draw_r = int(min(255, r * (0.2 + 0.8 * intensity)))
                draw_g = int(min(255, g * (0.2 + 0.8 * intensity)))
                draw_b = int(min(255, b * (0.2 + 0.8 * intensity)))
                
                # Ensure it's not darker than background if we want it to "glow" or stand out?
                # The background is (20, 40, 60).
                # Let's ensure minimum visibility.
                
                pygame.draw.rect(screen, (draw_r, draw_g, draw_b), 
                                 (x*self.cell_size, y*self.cell_size, self.cell_size, self.cell_size))


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