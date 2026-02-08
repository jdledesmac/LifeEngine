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

        # Chemical Colors Configuration
        self.chem_colors = {
            "A": (0, 200, 255),    # Cyan (Nutrient)
            "B": (160, 82, 45),    # Brown/Rust (Waste)
            "C": (50, 205, 50),    # Emerald Green (Exotic Nutrient)
        }

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

        # ---- Step 5: Draw Chemicals (Dynamic Mixing) ----
        # Iterate over all chemicals present in the world
        
        # We need to blend colors.
        # Strategy:
        # 1. Identify active tiles (optimize by union of indices > threshold? or just iterate non-empty arrays)
        # 2. Accumulate weighted colors.
        
        # For performance with 3+ chemicals, finding the union of all non-zero indices is tricky efficiently.
        # Let's iterate over ALL grid cells? No, too slow (80x60=4800 is fine, but if 800x600=480,000 is slow).
        # Existing logic used argwhere.
        
        # New approach: 
        # Create a "Total Concentration" grid and a "Accumulated Color" grid.
        
        # Using numpy for speed:
        total_conc = np.zeros((self.world.cols, self.world.rows))
        mixed_r = np.zeros((self.world.cols, self.world.rows))
        mixed_g = np.zeros((self.world.cols, self.world.rows))
        mixed_b = np.zeros((self.world.cols, self.world.rows))
        
        has_chemicals = False
        
        for mol_name, grid in self.world.chemistry.items():
            # Skip if empty (optimization)
            if np.max(grid) < 0.01: continue
            
            has_chemicals = True
            
            # Get color
            base_color = self.chem_colors.get(mol_name, (200, 200, 200)) # Default Grey
            
            # Add to total
            total_conc += grid
            
            # Accumulate weighted color components
            # We weight purely by amount. 
            # R_acc += amount * R_base
            mixed_r += grid * base_color[0]
            mixed_g += grid * base_color[1]
            mixed_b += grid * base_color[2]

        if has_chemicals:
            # Threshold to draw
            # Get indices where total > 0.2 (Increased to hide low-level diffusion fog)
            active_indices = np.argwhere(total_conc > 0.2)
            
            for x, y in active_indices:
                t = total_conc[x, y]
                
                # Setup normalized color
                # If t=10, r_acc = 10*R. r_final = r_acc / t = R. Correct.
                # If t=10 (5 A, 5 B). r_acc = 5*Ra + 5*Rb. r_final = (5Ra+5Rb)/10 = 0.5Ra + 0.5Rb. Correct.
                
                r = mixed_r[x,y] / t
                g = mixed_g[x,y] / t
                b = mixed_b[x,y] / t
                
                # Intensity scaling (brightness/alpha) using t
                # Standard: min(1.0, t / 20.0)
                intensity = min(1.0, t / 20.0)
                
                # Apply intensity (Dim if low concentration)
                # Formula: Color * (0.2 + 0.8 * intensity)
                factor = 0.2 + 0.8 * intensity
                
                draw_r = int(min(255, r * factor))
                draw_g = int(min(255, g * factor))
                draw_b = int(min(255, b * factor))
                
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
        Generates a color based on the cell's genome "functional signature".
        
        Uses a fuzzy hash approach that is stable across small mutations but
        distinguishes functionally different genomes:
        - Genome structure (number of genes, input/output chemistry)
        - Metabolic profile (cost/yield ranges, not exact values)
        
        This allows tracking evolutionary lineages without rainbow chaos.
        """
        genes = cell.genoma.genes
        if not genes:
            return (200, 200, 200)  # Dead/Empty gray

        # 1. Extract functional signature (stable across small mutations)
        signature = self._get_genome_signature(genes)
        
        # 2. Convert signature to deterministic color
        import hashlib
        sig_hash = hashlib.md5(signature.encode()).hexdigest()
        
        # Use first 6 hex chars for color (like web colors)
        # Convert to HSV for better control
        hash_int = int(sig_hash[:6], 16)
        
        # Map hash to hue (0-1)
        # We want diversity but also biological plausibility
        # Restrict to organic range: 0.05 (red-orange) to 0.65 (blue-green)
        hue = 0.05 + (hash_int % 1000) / 1000.0 * 0.6
        
        # Saturation based on genome complexity (number of genes)
        # More genes = more saturated (specialized)
        num_genes = len(genes)
        sat = 0.4 + min(0.5, num_genes * 0.1)
        
        # Value (brightness) based on average yield
        avg_yield = sum(g.energy_yield for g in genes) / len(genes)
        val = 0.6 + min(0.3, avg_yield * 0.06)
        
        r, g, b = colorsys.hsv_to_rgb(hue, sat, val)
        return (int(r*255), int(g*255), int(b*255))
    
    def _get_genome_signature(self, genes):
        """
        Creates a fuzzy functional signature of the genome.
        
        Captures essence without being sensitive to small mutations:
        - Number of genes (bucketed)
        - Input chemistry types
        - Output chemistry types  
        - Metabolic profile (cost/yield ranges)
        """
        # 1. Gene count bucket (1, 2-3, 4-5, 6+)
        num_genes = len(genes)
        if num_genes == 1:
            gene_bucket = "1"
        elif num_genes <= 3:
            gene_bucket = "2-3"
        elif num_genes <= 5:
            gene_bucket = "4-5"
        else:
            gene_bucket = "6+"
        
        # 2. Collect all input/output molecule types (sorted for consistency)
        inputs = set()
        outputs = set()
        for gene in genes:
            inputs.update(gene.input.keys())
            outputs.update(gene.output.keys())
        
        input_sig = ",".join(sorted(inputs)) if inputs else "none"
        output_sig = ",".join(sorted(outputs)) if outputs else "none"
        
        # 3. Metabolic profile (bucketed averages)
        avg_cost = sum(g.cost for g in genes) / len(genes)
        avg_yield = sum(g.energy_yield for g in genes) / len(genes)
        
        # Bucket costs: low (<0.3), medium (0.3-0.6), high (>0.6)
        if avg_cost < 0.3:
            cost_bucket = "low"
        elif avg_cost < 0.6:
            cost_bucket = "med"
        else:
            cost_bucket = "high"
        
        # Bucket yields: low (<1), medium (1-2.5), high (>2.5)
        if avg_yield < 1.0:
            yield_bucket = "low"
        elif avg_yield < 2.5:
            yield_bucket = "med"
        else:
            yield_bucket = "high"
        
        # Combine into signature string
        signature = f"{gene_bucket}|in:{input_sig}|out:{output_sig}|cost:{cost_bucket}|yield:{yield_bucket}"
        return signature


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
            
            # Format chemistry for display (rounded to 1 decimal)
            chem_str = ", ".join([f"{mol}:{amt:.1f}" for mol, amt in list(cell.chemistry.items())[:3]])
            if len(cell.chemistry) > 3:
                chem_str += "..."
            
            # Simple stats for UI
            info = f"Cell #{i}: E={cell.energy:.1f} | Age={cell.age} | ID={cell.genoma.get_hash()} | Chem=[{chem_str}]"
            detail_text = self.font.render(info, True, (150, 180, 200))
            screen.blit(detail_text, (20, ui_y + y_offset))
            y_offset += 20