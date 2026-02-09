import pygame
import colorsys
import numpy as np
import biology.chemistry_dict as chem

class WorldObject:
    """
    Handles the visual representation and update loop of the game world.
    Adapted for Digital Biology (Integer-based Chemistry).
    """
    def __init__(self, world, cell_size=10):
        self.world = world
        self.cell_size = cell_size
        self.accumulator = 0.0
        self.step_time = 0.1
        
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 14)
        self.bg_color = (20, 40, 60) # Deep Ocean

    def update(self, dt):
        self.accumulator += dt
        while self.accumulator >= self.step_time:
            self.world.step()
            self.accumulator -= self.step_time

    def draw(self, screen):
        screen.fill(self.bg_color)

        # ---- Draw Chemicals ----
        total_conc = np.zeros((self.world.cols, self.world.rows))
        mixed_r = np.zeros((self.world.cols, self.world.rows))
        mixed_g = np.zeros((self.world.cols, self.world.rows))
        mixed_b = np.zeros((self.world.cols, self.world.rows))
        
        has_chemicals = False
        
        for mol_id, grid in self.world.chemistry.items():
            if np.max(grid) < 0.1: continue
            
            has_chemicals = True
            base_color = self.get_molecule_color(mol_id)
            
            total_conc += grid
            mixed_r += grid * base_color[0]
            mixed_g += grid * base_color[1]
            mixed_b += grid * base_color[2]

        if has_chemicals:
            # Draw wherever concentration > threshold
            active_indices = np.argwhere(total_conc > 0.5)
            
            for x, y in active_indices:
                t = total_conc[x, y]
                if t <= 0: continue
                
                r = mixed_r[x,y] / t
                g = mixed_g[x,y] / t
                b = mixed_b[x,y] / t
                
                # Standardize intensity visualization
                intensity = min(1.0, t / 50.0) # 50 = max visible saturation
                factor = 0.3 + 0.7 * intensity
                
                draw_r = int(min(255, r * factor))
                draw_g = int(min(255, g * factor))
                draw_b = int(min(255, b * factor))
                
                pygame.draw.rect(screen, (draw_r, draw_g, draw_b), 
                                 (x*self.cell_size, y*self.cell_size, self.cell_size, self.cell_size))

        # ---- Draw Cells ----
        for cell in self.world.cells:
            if not cell.alive: continue

            color = self.get_cell_color(cell)
            rect = pygame.Rect(cell.x*self.cell_size, cell.y*self.cell_size, self.cell_size, self.cell_size)
            pygame.draw.rect(screen, color, rect)
            
        self.draw_ui(screen)

    def get_molecule_color(self, mol_id):
        """Returns (R, G, B) for a given molecule ID."""
        name = chem.get_name(mol_id)
        
        # Fixed colors for common molecules
        if name == "GLUCOSE": return (255, 255, 255) # White Sugar
        if name == "ATP": return (255, 215, 0)       # Gold
        if name == "CO2": return (100, 100, 100)     # Gray Smoke
        if name == "WATER": return (0, 0, 255)       # Blue
        if name == "FATTY_ACID": return (200, 150, 50) # Oily
        if name == "AMMONIA": return (150, 255, 100) # Toxic Green
        
        # Procedural color for others based on ID
        import colorsys
        hue = (mol_id / 255.0)
        r, g, b = colorsys.hsv_to_rgb(hue, 0.8, 0.8)
        return (int(r*255), int(g*255), int(b*255))

    def get_cell_color(self, cell):
        """
        Color based on genome mask sum (functional profile).
        """
        if not cell.genoma.genes:
            return (100, 100, 100)

        # Calculate "Average Mask"
        avg_mask = 0
        for gene in cell.genoma.genes:
            avg_mask |= gene.mask
            
        # Use average mask for Hue
        hue = (avg_mask / 255.0)
        
        # Saturation by gene count
        num_genes = len(cell.genoma.genes)
        sat = 0.5 + min(0.5, num_genes * 0.1)
        
        # Value by Energy level (visual health)
        val = 0.5 + min(0.5, cell.energy / 500.0)
        
        r, g, b = colorsys.hsv_to_rgb(hue, sat, val)
        return (int(r*255), int(g*255), int(b*255))

    def draw_ui(self, screen):
        ui_y = self.world.rows * self.cell_size
        pygame.draw.rect(screen, (10, 20, 30), (0, ui_y, screen.get_width(), 100))
        
        alive_count = len([c for c in self.world.cells if c.alive])
        summary = f"Alive: {alive_count} | Total: {len(self.world.cells)}"
        screen.blit(self.font.render(summary, True, (200, 220, 255)), (10, ui_y + 10))
        
        # Inspect first few live cells
        active_cells = [c for c in self.world.cells if c.alive][:3]
        y_off = 30
        for i, cell in enumerate(active_cells):
            # Format chemistry using names
            chem_str = ", ".join([f"{chem.get_name(m)}:{int(a)}" for m, a in cell.chemistry.items()])
            info = f"#{i} E:{int(cell.energy)} | Age:{cell.age} | Chem:[{chem_str}]"
            screen.blit(self.font.render(info, True, (150, 180, 200)), (20, ui_y + y_off))
            y_off += 20