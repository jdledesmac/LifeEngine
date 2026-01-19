import pygame
import pygame
import hashlib
import colorsys

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
        for x in range(self.world.cols):
            for y in range(self.world.rows):
                chem = self.world.chemistry[x][y]
                
                # Base black color
                r, g, b = 0, 0, 0

                # Nutrient 'A' -> Green
                if "A" in chem:
                    green_intensity = min(255, int(chem["A"] * 20))
                    g = min(255, g + green_intensity)
                
                # Waste 'B' -> Brown (139, 69, 19)
                if "B" in chem:
                    brown_factor = min(1.0, chem["B"] * 0.5) # Scale factor based on amount
                    # Add brown components
                    r = min(255, r + int(139 * brown_factor))
                    g = min(255, g + int(69 * brown_factor)) # Note: green channel overlaps
                    b = min(255, b + int(19 * brown_factor))

                color = (r, g, b)

                if r > 0 or g > 0 or b > 0:
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

            # Color based on genome hash
            color = self.get_cell_color(cell)

            
            rect = pygame.Rect(
                cell.x * self.cell_size,
                cell.y * self.cell_size,
                self.cell_size,
                self.cell_size
            )
            pygame.draw.rect(screen, color, rect)
            
        # ---- Step 6: Draw UI Dashboard ----
        self.draw_ui(screen)

    def get_cell_color(self, cell):
        """
        Generates a neon color based on the cell's genome using HSV.
        """
        # Create a unique string signature
        genome_str = str(cell.genoma)
        
        # Hash it (using md5 for decent distribution)
        hash_obj = hashlib.md5(genome_str.encode())
        hex_dig = hash_obj.hexdigest()
        
        # Use part of the hash to determine Hue (0.0 to 1.0)
        # We take first 4 hex chars -> 16 bits -> 0 to 65535
        # Normalize to 0-1
        hue_int = int(hex_dig[:4], 16)
        hue = hue_int / 65535.0
        
        # Saturation and Value high for "Neon" look
        saturation = 0.9
        value = 0.9
        
        # Convert HSV to RGB
        r_float, g_float, b_float = colorsys.hsv_to_rgb(hue, saturation, value)
        
        # Scale to 0-255
        r = int(r_float * 255)
        g = int(g_float * 255)
        b = int(b_float * 255)
        
        return (r, g, b)

    def draw_ui(self, screen):
        # ---- Step 6: Draw UI Dashboard ----
        # Draw background panel
        ui_y = self.world.rows * self.cell_size
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
            
            info = f"Cell #{i}: E={cell.energy:.1f} | Age={cell.age} | Chem={{ {chem_str} }}"
            detail_text = self.font.render(info, True, (200, 200, 200))
            screen.blit(detail_text, (20, ui_y + y_offset))
            y_offset += 20