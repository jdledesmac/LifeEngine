"""
Digital Chemistry Dictionary (8-Bit Alchemy)

This module provides the mapping between 8-bit integer values (0-255) 
and biological names. This allows the simulation to run on fast bitwise 
operations while presenting human-readable names in the UI and logs.

Mappings are based on bit pattern complexity:
- High bit count (e.g. 255): High energy/structural complexity
- Low bit count (e.g. 3): Low energy/waste
"""

# Core mappings
NAME_TO_INT = {
    # ENERGY CARRIERS (High complexity)
    "ATP": 255,        # 11111111 - Max energy
    "GLUCOSE": 240,    # 11110000 - High energy
    "FATTY_ACID": 204, # 11001100 - Specialized energy
    
    # STRUCTURAL (Stable patterns)
    "PROTEIN_A": 170,  # 10101010 - Alternating pattern (stable)
    "PROTEIN_B": 85,   # 01010101 - Complement of Protein A
    
    # WASTE / SIMPLE (Low complexity)
    "CO2": 15,         # 00001111 - Waste from Glucose
    "WATER": 3,        # 00000011 - Very simple
    "AMMONIA": 51,     # 00110011 - Nitrogenous waste
    
    # SPECIAL
    "TOXIN_A": 128,    # 10000000 - Signal/Disruptor
    "VOID": 0          # 00000000 - Nothing
}

# Inverse mapping for lookups
INT_TO_NAME = {v: k for k, v in NAME_TO_INT.items()}

def get_name(value):
    """Returns the biological name for an int value, or a formatted hex string."""
    if value in INT_TO_NAME:
        return INT_TO_NAME[value]
    return f"UNK_{value:02X}" # e.g. UNK_A5

def get_value(name):
    """Returns the int value for a biological name (case-insensitive)."""
    normalized = name.upper().replace(" ", "_")
    return NAME_TO_INT.get(normalized, 0)
