from .action import CellAction
import biology.chemistry_dict as chem
import random

class Cell:
    def __init__(self, genoma):
        self.genoma = genoma
        self.chemistry = {} # Map of molecule_id (int) -> amount (float)
        # Energy scaled up: 200 units = 10 old units
        self.energy = 200 
        self.age = 0
        self.alive = True
        self.ready_to_divide = False
        self.division_cooldown = 0
        self.x = None   
        self.y = None
        
    def step(self):
        """Internal cell processes."""
        self.ready_to_divide = False
        if not self.alive:
            return
            
        self.dissipate()
        self.assess_state()
        self.age += 1

    def dissipate(self):
        """Energy maintenance cost."""
        # Base cost 2 (0.1) + age factor
        self.energy -= 2 + int(0.01 * self.age)

    def observe_environment(self, env_chemistry):
        return env_chemistry

    def decide_actions(self, env_chemistry, neighbors_chemistry):
        """Action decision logic using Digital Metabolism."""
        actions = []
        
        # 1. Absorb useful molecules
        # Scan environment for anything my genes can process
        useful_mols = self._identify_useful_molecules(env_chemistry)
        
        for mol_id in useful_mols:
            amount = env_chemistry[mol_id]
            # Desire 50% of available
            desired = amount * 0.5
            # Cost to absorb (active transport): 1 unit per 10 amount
            cost = int(desired * 0.1)
            
            if self.energy > cost + 10: # Safety buffer
                actions.append(CellAction(CellAction.ABSORB, molecule=mol_id, amount=desired))

        # 2. Release waste 
        # Release anything I cannot process
        waste_mols = self._identify_waste_molecules()
        for mol_id in waste_mols:
            amount = self.chemistry[mol_id]
            if amount > 1.0:
                 # Release all waste
                 actions.append(CellAction(CellAction.RELEASE, molecule=mol_id, amount=amount))

        # 3. Metabolize (Process internal stores)
        self._metabolize()
        
        # 4. Movement (Chemotaxis)
        movement = self._decide_movement(env_chemistry, neighbors_chemistry)
        if movement:
            actions.append(movement)
            
        return actions

    def _identify_useful_molecules(self, chemistry):
        """Returns list of molecule IDs that yield net positive energy."""
        useful = []
        for mol_id, amount in chemistry.items():
            if amount <= 0.1: continue
            
            # Check if ANY gene yields net positive energy
            for gene in self.genoma.genes:
                res = gene.process(mol_id)
                if res['success']:
                    useful.append(mol_id)
                    break
        return useful

    def _identify_waste_molecules(self):
        """Returns list of internal molecules that NO gene can process."""
        waste = []
        for mol_id, amount in self.chemistry.items():
            can_process = False
            for gene in self.genoma.genes:
                res = gene.process(mol_id)
                if res['success']:
                    can_process = True
                    break
            if not can_process:
                waste.append(mol_id)
        return waste

    def _metabolize(self):
        """
        Executes enzymes on stored molecules.
        Prioritizes high-yield reactions.
        """
        # Snapshot keys to modify dict safely
        for mol_id in list(self.chemistry.keys()):
            amount = self.chemistry[mol_id]
            if amount < 1.0: continue 
            
            best_gene = None
            best_yield = -float('inf')
            best_res = None
            
            # Find best gene for this molecule
            for gene in self.genoma.genes:
                res = gene.process(mol_id)
                if res['net_energy'] > best_yield:
                    best_yield = res['net_energy']
                    best_gene = gene
                    best_res = res
            
            # If we found a productive reaction
            if best_gene and best_yield > 0:
                # Process integer amount (Digital Biology is discrete-ish)
                process_amount = int(amount) 
                
                # Check energy for activation cost
                total_cost = best_res['cost'] * process_amount
                
                if self.energy >= total_cost:
                    # Execute
                    total_gain = best_res['gross_energy'] * process_amount
                    net_gain = total_gain - total_cost
                    
                    self.energy += net_gain
                    self.chemistry[mol_id] -= process_amount
                    
                    # Generate waste
                    waste_id = best_res['waste']
                    if waste_id != chem.get_value("VOID"):
                        self.chemistry[waste_id] = self.chemistry.get(waste_id, 0) + process_amount
                        
                    # Remove empty key
                    if self.chemistry[mol_id] <= 0:
                        del self.chemistry[mol_id]

    def _decide_movement(self, env_chemistry, neighbors_chemistry):
        """Moves towards efficient food sources."""
        # Calculate utility of current spot
        current_useful = self._identify_useful_molecules(env_chemistry)
        current_utility = sum(env_chemistry[m] for m in current_useful)
        
        # Don't move if well fed
        if current_utility > 10.0:
            return None
            
        if self.energy < 10: # Too tired
            return None
            
        # Find best neighbor
        directions = {
            'N': (0, -1), 'S': (0, 1),
            'E': (1, 0), 'W': (-1, 0)
        }
        
        best_utility = current_utility * 1.1 # 10% improvement needed
        best_dir = None
        
        for dir_name, (dx, dy) in directions.items():
            if dir_name in neighbors_chemistry:
                n_chem = neighbors_chemistry[dir_name]
                n_useful = self._identify_useful_molecules(n_chem)
                n_utility = sum(n_chem[m] for m in n_useful)
                
                if n_utility > best_utility:
                    best_utility = n_utility
                    best_dir = (dx, dy)
        
        if best_dir:
            return CellAction(CellAction.MOVE, direction=best_dir, cost=5)
            
        # Random wander
        if random.random() < 0.1:
             d = random.choice(list(directions.values()))
             return CellAction(CellAction.MOVE, direction=d, cost=2)
             
        return None

    def absorb(self, molecule, amount, cost_per_unit=0.1): # specific cost ignored, generic logic used
        # Simplified absorption logic called by World
        # World already deducted energy? No, Cell decides action, World executes.
        # World calls cell.absorb(mol, amt) -> returns actual
        
        # Re-check energy limit here
        cost = amount * 0.1
        if cost > self.energy:
            amount = self.energy / 0.1
            cost = self.energy
            
        if amount > 0:
            self.chemistry[molecule] = self.chemistry.get(molecule, 0) + amount
            self.energy -= cost
            
        return amount

    def release(self, molecule, amount):
        available = self.chemistry.get(molecule, 0)
        actual = min(amount, available)
        
        if actual > 0:
            self.chemistry[molecule] -= actual
            if self.chemistry[molecule] <= 0:
                del self.chemistry[molecule]
        return actual
        
    def assess_state(self):
        if self.energy < 0:
            self.alive = False
            return
            
        # Division checks
        total_mass = sum(self.chemistry.values())
        if total_mass >= 50 and self.energy > 100:
             self.ready_to_divide = True

    def total_chemistry(self):
        return sum(self.chemistry.values())
