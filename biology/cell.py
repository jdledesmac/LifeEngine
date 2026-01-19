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
        self.ready_to_divide = False
        if not self.alive:
            return
        self.age += 1
        self.dissipate()
        self.metabolize()
        self.assess_state()
        
     
        
    def dissipate(self):
        self.energy -= 0.1 + 0.0001*self.age

    def metabolize(self):
        for gen in self.genoma.genes:
            # Assuming gen has can_react method matching this signature
            if gen.can_react(self.chemistry, self.energy):
                self.energy = gen.reaction(self.chemistry, self.energy)
    
    def assess_state(self):
        toxic = self.chemistry.get("B", 0)
        if toxic > 10:
            self.energy -= 0.2*(toxic-10)
            
        if self.division_cooldown > 0:
            self.division_cooldown -= 1
            return
        if self.energy < 0:
            self.alive = False
            return
        # Division threshold: "2 pixels" worth of mass (10 per pixel approx)
        if self.total_chemistry() >= 20 and self.energy > 5:
            self.ready_to_divide = True

    def total_chemistry(self):
        return sum(self.chemistry.values())