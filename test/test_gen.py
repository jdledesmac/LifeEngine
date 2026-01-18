import pytest
from structures.gen import Gen

def test_gen_reaction():
    # Define initial state
    chemistry = {'A': 10, 'B': 5}
    energy = 100

    # Define a gene
    # Input: needs 2 'A'
    # Output: produces 1 'C'
    # Cost: 10 energy
    # Probability: 1.0 (always happens if possible)
    test_gen = Gen(input={'A': 2}, output={'C': 1}, cost=10, prob=1.0)

    # Check if reaction is possible
    can_react = test_gen.can_react(chemistry, energy)
    assert can_react is True, "Reaction should be possible"

    if can_react:
        # Perform reaction
        new_energy = test_gen.reaction(chemistry, energy)
        
        # Verify results
        assert chemistry['A'] == 8
        assert chemistry['B'] == 5
        assert chemistry.get('C', 0) == 1
        assert new_energy == 90
    else:
        pytest.fail("Reaction failed conditions unexpectedly")
        
