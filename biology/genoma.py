import random

class Genoma:
    def __init__(self, genes):
        self.genes = genes  

    def __repr__(self):
        return f"Genoma(genes={[str(g) for g in self.genes]})"
    
    def mutate(self, gen_pool=None):
        """
        Applies random mutations to the genome.
        Types:
        1. Point Mutation: Modifies attributes of an existing gene.
        2. Duplication: Copies an existing gene.
        3. Deletion: Removes an existing gene.
        """
        if not self.genes:
            return

        # 1. Point Mutation (Most common)
        for gene in self.genes:
            if random.random() < 0.08: # 8% chance per gene to tweak cost
                 gene.cost = max(0.1, gene.cost + random.uniform(-0.1, 0.1))
            
            if random.random() < 0.05: # 5% chance per gene to tweak prob
                gene.prob = min(1.0, max(0.1, gene.prob + random.uniform(-0.1, 0.1)))

        # 2. Gene Duplication (Rare)
        if random.random() < 0.01: # 1% chance
            target = random.choice(self.genes)
            # Create a shallow copy (or deep if needed, but new instance is safer)
            import copy
            new_gen = copy.deepcopy(target)
            self.genes.append(new_gen)

        # 3. Gene Deletion (Very Rare, dangerous)
        if len(self.genes) > 1 and random.random() < 0.01: # 1% chance
            self.genes.pop(random.randint(0, len(self.genes)-1))