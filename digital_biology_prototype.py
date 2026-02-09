"""
Digital Biology Prototype (8-Bit Alchemy)

This script simulates the bitwise metabolic process:
- Molecules are 8-bit integers (0-255).
- Enzymes are 8-bit bitmasks.
- Reaction: (Food & Enzyme) -> Energy + Waste.
- Waste = Food XOR (Food & Enzyme)
- Includes metabolic cost calculation.
"""

def bit_count(n):
    return bin(n).count('1')

class DigitalEnzyme:
    def __init__(self, mask, cost_base=10, cost_per_bit=2):
        """
        Energy Units are INTEGERS (e.g. 10 units = 1.0 "Standard Energy").
        Using integers avoids floating point overhead and errors.
        """
        self.mask = mask
        self.complexity = bit_count(mask)
        # Cost depends on complexity
        # Example: Base 10 + (4 bits * 2) = 18 units
        self.metabolic_cost = cost_base + (self.complexity * cost_per_bit)

    def analyze(self, molecule):
        """Simulate the reaction process."""
        # 1. Reaction (Lock and Key)
        extracted = molecule & self.mask
        
        # 2. Energy Potential (Gross Energy)
        # Each bit extracted yields energy useful for the cell
        energy_bits = bit_count(extracted)
        gross_energy = energy_bits * 20  # 20 units per bit (was 2.0)
        
        # 3. Waste Product
        waste = molecule ^ extracted
        
        # 4. Net Gain
        net_energy = gross_energy - self.metabolic_cost
        
        return {
            "input": molecule,
            "mask": self.mask,
            "extracted_bits": extracted,
            "waste": waste,
            "gross_energy": gross_energy,
            "cost": self.metabolic_cost,
            "net_energy": net_energy,
            "success": net_energy > 0
        }

    def __repr__(self):
        return f"Enzyme(Mask={self.mask:08b}, Cost={self.metabolic_cost})"

# ==========================================
# SIMULATION TESTS
# ==========================================
import biology.chemistry_dict as chem

print("=== 🧪 DIGITAL BIOLOGY PROTOTYPE (8-BIT) ===\n")

# 1. Create a "Glucose-eating" Enzyme
# Glucose is 240 (11110000). To eat it, we need a matching mask.
# Let's say enzyme matches the high energy part perfectly.
glucose_val = chem.get_value("GLUCOSE")
enzyme_mask = 0b11110000 

enzyme = DigitalEnzyme(mask=enzyme_mask) 
print(f"Created {enzyme} (Targeting: {glucose_val:08b})")

# Test A: Eating Glucose
print(f"\n--- Eating {chem.get_name(glucose_val)}: {glucose_val:08b} ({glucose_val}) ---")
result = enzyme.analyze(glucose_val)

print(f"Extracted: {result['extracted_bits']:08b} (Energy bits: {bit_count(result['extracted_bits'])})")
waste_name = chem.get_name(result['waste'])
print(f"Waste:     {result['waste']:08b} ({waste_name})")
print(f"Energies:  Gross={result['gross_energy']} - Cost={result['cost']} = NET {result['net_energy']}")

if result['success']:
    print("✅ Reaction Successful! (Gain)")
else:
    print("❌ Starvation! (Loss)")

# Test B: Eating ATP (High Energy) with Glucose Enzyme
# ATP (255) & Glucose Mask (240) -> Extracted 240, Waste 15 (CO2)
atp_val = chem.get_value("ATP")
print(f"\n--- Eating {chem.get_name(atp_val)}: {atp_val:08b} ({atp_val}) ---")
result_b = enzyme.analyze(atp_val)

print(f"Extracted: {result_b['extracted_bits']:08b} (Energy bits: {bit_count(result_b['extracted_bits'])})")
waste_name_b = chem.get_name(result_b['waste'])
print(f"Waste:     {result_b['waste']:08b} ({waste_name_b})")
print(f"Energies:  Gross={result_b['gross_energy']} - Cost={result_b['cost']} = NET {result_b['net_energy']}")

if result_b['success']:
    print("✅ Reaction Successful! (Gain)")
else:
    print("❌ Starvation! (Loss)")

# Test C: Eating CO2 (Low Energy)
co2_val = chem.get_value("CO2")
print(f"\n--- Eating {chem.get_name(co2_val)}: {co2_val:08b} ({co2_val}) ---")
result_c = enzyme.analyze(co2_val)

print(f"Extracted: {result_c['extracted_bits']:08b}")
print(f"Waste:     {result_c['waste']:08b} ({chem.get_name(result_c['waste'])})")
print(f"Energies:  Gross={result_c['gross_energy']} - Cost={result_c['cost']} = NET {result_c['net_energy']}")

if result_c['success']:
    print("✅ Reaction Successful!")
else:
    print("❌ Starvation! (Net Loss - Metabolic cost exceeded gain)")

print("\n=== EVOLUTIONARY IMPLICATIONS ===")
print(f"The waste from ATP was: {waste_name_b}")
print(f"A scavenger cell could evolve to eat {waste_name_b} specifically!")
