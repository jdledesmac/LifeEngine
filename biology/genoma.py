import random

class Genoma:
    def __init__(self, genes):
        self.genes = genes  

    def get_hash(self):
        """Returns a short unique hash of the genome configuration."""
        import hashlib
        # Sort gene IDs to ensure that order (if commutative) doesn't change hash
        # though order usually matters for execution, let's keep it sorted for "identity"
        gene_ids = sorted([g.get_id() for g in self.genes])
        combined_id = "|".join(gene_ids)
        return hashlib.md5(combined_id.encode()).hexdigest()[:6].upper()

    def __repr__(self):
        return f"Genoma(id={self.get_hash()}, genes={[str(g) for g in self.genes]})"
    
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

        for gene in self.genes:
            # 1. Point Mutation in Mask (Flip bits)
            if random.random() < 0.1: # 10% chance per gene to mutate mask
                # Flip 1 random bit in the 8-bit mask (0-7)
                bit_to_flip = 1 << random.randint(0, 7)
                gene.mask ^= bit_to_flip
                gene._recalculate_cost()
            
            # 2. Mutate Cost Base
            if random.random() < 0.05: # 5% chance
                # Small integer change (-1, 0, +1)
                change = random.randint(-1, 1)
                gene.cost_base = max(1, gene.cost_base + change)
                gene._recalculate_cost()

        # 2. Gene Duplication (Rare)
        if random.random() < 0.02: # 2% chance
            target = random.choice(self.genes)
            import copy
            new_gen = copy.deepcopy(target)
            # Add slight variation to duplicate immediately to avoid redundancy
            if random.random() < 0.5:
                 new_gen.mask ^= (1 << random.randint(0, 7))
                 new_gen._recalculate_cost()
            self.genes.append(new_gen)

        # 3. Gene Deletion (Very Rare)
        if len(self.genes) > 1 and random.random() < 0.01: # 1% chance
            self.genes.pop(random.randint(0, len(self.genes)-1))