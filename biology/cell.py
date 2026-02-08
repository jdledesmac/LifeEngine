from .action import CellAction

class Cell:
    def __init__(self, genoma):
        self.genoma = genoma
        self.chemistry = {}
        self.energy = 20 
        self.age = 0
        self.alive=True
        self.ready_to_divide = False
        self.division_cooldown = 0
        self.x = None   
        self.y = None
        
    
    def step(self):
        """
        Internal cell processes: energy dissipation, toxicity assessment, aging.
        Metabolism is now handled through decide_actions().
        """
        self.ready_to_divide = False
        if not self.alive:
            return
        self.dissipate()
        self.assess_state()
        self.age += 1
     
        
    def dissipate(self):
        """Energy dissipation due to maintenance costs."""
        self.energy -= 0.1 + 0.0005*self.age

    def observe_environment(self, env_chemistry):
        """
        Observes the local environment.
        
        Args:
            env_chemistry (dict): Chemistry available at cell's current position.
            
        Returns:
            dict: The environment chemistry (pass-through for now, could add perception filters).
        """
        return env_chemistry
    
    def decide_actions(self, env_chemistry, neighbors_chemistry):
        """
        Core decision-making logic. Cell analyzes its genome, internal state,
        and environment to decide what actions to take.
        
        Args:
            env_chemistry (dict): Chemistry at cell's current position.
            neighbors_chemistry (dict): Chemistry at neighboring positions (N, S, E, W).
            
        Returns:
            list[CellAction]: List of actions the cell wants to perform.
        """
        actions = []
        
        # 1. Decide what to absorb based on genome needs
        needed_mols = self._identify_needs()
        for mol in needed_mols:
            if mol in env_chemistry and env_chemistry[mol] > 0:
                # Absorb up to 50% of available, limited by energy cost
                available = env_chemistry[mol]
                desired = available * 0.5
                
                # Energy cost: 0.01 per unit
                cost = desired * 0.01
                if self.energy > cost:
                    actions.append(CellAction(CellAction.ABSORB, molecule=mol, amount=desired))
        
        # 2. Decide what to release (toxins, waste)
        tolerances = self._calculate_tolerances()
        waste_molecules = self._identify_waste()
        
        for mol, amount in self.chemistry.items():
            limit = tolerances.get(mol, 10.0)
            is_waste = mol in waste_molecules
            
            # Release if:
            # - It's metabolic waste (produced but not consumed)
            # - It exceeds tolerance (toxic buildup)
            if is_waste or amount > limit:
                # Release all waste, or excess above 80% of tolerance
                release_amt = amount if is_waste else (amount - limit * 0.8)
                if release_amt > 0:
                    actions.append(CellAction(CellAction.RELEASE, molecule=mol, amount=release_amt))
        
        # 3. Metabolize (internal decision, executed immediately)
        self._metabolize()
        
        # 4. Decide movement
        movement = self._decide_movement(env_chemistry, neighbors_chemistry)
        if movement:
            actions.append(movement)
        
        return actions
    
    def _identify_needs(self):
        """Identifies molecules needed by the cell's genes."""
        needed_mols = set()
        for gene in self.genoma.genes:
            for input_mol in gene.input.keys():
                needed_mols.add(input_mol)
        return needed_mols
    
    def _identify_waste(self):
        """
        Identifies metabolic waste molecules based on genome.
        
        Waste = molecules that are PRODUCED but NOT CONSUMED by any gene.
        This makes waste an emergent property of the genome, not hardcoded.
        
        Returns:
            set: Set of molecule names that are metabolic waste.
        """
        produced = set()
        consumed = set()
        
        for gene in self.genoma.genes:
            # Collect all outputs (produced)
            produced.update(gene.output.keys())
            # Collect all inputs (consumed)
            consumed.update(gene.input.keys())
        
        # Waste = produced but not consumed
        waste = produced - consumed
        return waste
    
    def _calculate_tolerances(self):
        """Calculates toxicity tolerances based on genome."""
        tolerances = {}
        for gen in self.genoma.genes:
            for mol, level in gen.tolerance.items():
                tolerances[mol] = max(tolerances.get(mol, 0), level)
        return tolerances
    
    def _metabolize(self):
        """
        Internal metabolism: runs genetic reactions.
        This is now part of the decision phase, not forced by the world.
        """
        for gen in self.genoma.genes:
            if gen.can_react(self.chemistry, self.energy):
                self.energy = gen.reaction(self.chemistry, self.energy)
    
    def _decide_movement(self, env_chemistry, neighbors_chemistry):
        """
        Decides whether to move based on chemotaxis.
        
        Args:
            env_chemistry (dict): Current position chemistry.
            neighbors_chemistry (dict): Dict with keys 'N', 'S', 'E', 'W'.
            
        Returns:
            CellAction or None: Movement action if beneficial.
        """
        needed_mols = self._identify_needs()
        if not needed_mols:
            return None
        
        # Calculate utility at current position
        current_utility = sum(env_chemistry.get(mol, 0) for mol in needed_mols)
        
        # Don't move if well-fed (save energy)
        if current_utility > 0.5:
            return None
        
        # Check if movement is worth the cost
        if self.energy < 0.5:  # Not enough energy to move
            return None
        
        # Find best neighbor
        directions = {
            'N': (0, -1),
            'S': (0, 1),
            'E': (1, 0),
            'W': (-1, 0)
        }
        
        best_utility = current_utility * 1.05  # Require 5% improvement
        best_direction = None
        
        for dir_name, (dx, dy) in directions.items():
            if dir_name in neighbors_chemistry:
                neighbor_chem = neighbors_chemistry[dir_name]
                utility = sum(neighbor_chem.get(mol, 0) for mol in needed_mols)
                
                if utility > best_utility:
                    best_utility = utility
                    best_direction = (dx, dy)
        
        if best_direction:
            return CellAction(CellAction.MOVE, direction=best_direction, cost=0.5)
        
        # Passive random movement (5% chance)
        import random
        if random.random() < 0.05:
            direction = random.choice(list(directions.values()))
            return CellAction(CellAction.MOVE, direction=direction, cost=0)
        
        return None
    
    def absorb(self, molecule, amount, cost_per_unit=0.01):
        """
        Absorbs a molecule from the environment (active transport).
        
        Args:
            molecule (str): Molecule name.
            amount (float): Amount to absorb.
            cost_per_unit (float): Energy cost per unit absorbed.
            
        Returns:
            float: Actual amount absorbed (may be less if insufficient energy).
        """
        cost = amount * cost_per_unit
        
        # Limit by available energy
        if cost > self.energy:
            amount = self.energy / cost_per_unit
            cost = self.energy
        
        if amount > 0:
            self.chemistry[molecule] = self.chemistry.get(molecule, 0) + amount
            self.energy -= cost
        
        return amount
    
    def release(self, molecule, amount):
        """
        Releases a molecule to the environment (passive diffusion).
        
        Args:
            molecule (str): Molecule name.
            amount (float): Amount to release.
            
        Returns:
            float: Actual amount released.
        """
        available = self.chemistry.get(molecule, 0)
        actual = min(amount, available)
        
        if actual > 0:
            self.chemistry[molecule] -= actual
            if self.chemistry[molecule] <= 0:
                del self.chemistry[molecule]
        
        return actual
    
    def assess_state(self):
        """Assesses cell state: toxicity damage, death, division readiness."""
        # 1. Calculate Tolerances based on Genome
        tolerances = self._calculate_tolerances()

        # 2. Check internal chemistry for toxicity
        for mol, amount in self.chemistry.items():
            # Base tolerance is 10 for everything unless specified
            limit = tolerances.get(mol, 10.0)
            
            if amount > limit:
                # Damage proportional to excess
                excess = amount - limit
                self.energy -= 0.2 * excess
            
        if self.division_cooldown > 0:
            self.division_cooldown -= 1
            return

        if self.energy < 0:
            self.alive = False
            return
        # Division threshold: "2 pixels" worth of mass (10 per pixel approx)
        if self.total_chemistry() >= 5 and self.energy > 5:
            self.ready_to_divide = True

    def total_chemistry(self):
        """Returns total biomass (sum of all internal molecules)."""
        return sum(self.chemistry.values())
