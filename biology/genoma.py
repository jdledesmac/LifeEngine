import random

class Genoma:
    def __init__(self, genes):
        self.genes = genes  
    
    def mutate(self, gen):
        if random.random() < 0.05:
            self.genes.append(detox_gen)
        if random.random() < 0.1:
            gen.cost += random.choice([-1, 1])
        if random.random() < 0.1:
            gen.prob = min(1.0, max(0.0, gen.prob + random.uniform(-0.1, 0.1)))