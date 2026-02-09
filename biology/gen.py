import random

def bit_count(n):
    return bin(n).count('1')

class Gen:
    """
    Represents a Digital Enzyme (Gene) defined by a bitmask.
    
    Metabolism Logic (8-Bit Alchemy):
    - Reaction: Input & Mask
    - Energy Gain: bit_count(Reaction) * 20
    - Waste: Input XOR Reaction
    - Cost: Base + (Complexity * Factor)
    """
    def __init__(self, mask, cost_base=10, cost_per_bit=2):
        """
        Initializes a Digital Gene.
        
        Args:
            mask (int): 8-bit integer acting as the enzyme shape.
            cost_base (int): Base metabolic cost.
            cost_per_bit (int): Additional cost per bit of complexity.
        """
        self.mask = mask
        self.cost_base = cost_base
        self.cost_per_bit = cost_per_bit
        self._recalculate_cost()

    def _recalculate_cost(self):
        self.complexity = bit_count(self.mask)
        self.cost = self.cost_base + (self.complexity * self.cost_per_bit)

    def process(self, molecule):
        """
        Attempts to metabolize a molecule.
        
        Args:
            molecule (int): The 8-bit chemical input.
            
        Returns:
            dict: Result containing 'net_energy', 'waste', 'success'.
        """
        # 1. Reaction (Lock and Key)
        extracted = molecule & self.mask
        
        # 2. Energy Potential
        # Each bit extracted yields 20 units of energy
        energy_bits = bit_count(extracted)
        gross_energy = energy_bits * 20
        
        # 3. Waste Product
        # Waste is what was left of the molecule after extraction
        waste = molecule ^ extracted
        
        # 4. Net Gain
        net_energy = gross_energy - self.cost
        
        return {
            "input": molecule,
            "mask": self.mask,
            "extracted_bits": extracted,
            "waste": waste,
            "gross_energy": gross_energy,
            "cost": self.cost,
            "net_energy": net_energy,
            "success": net_energy > 0
        }

    def get_id(self):
        """Unique ID based on mask and cost configuration."""
        return f"M{self.mask:02X}-C{self.cost}"

    def __repr__(self):
        return f"Gen(mask={self.mask:08b}, cost={self.cost})"
