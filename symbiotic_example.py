"""
Symbiotic Ecosystem Example - Closed Loop Life Cycle

This demonstrates how to create two species that form a symbiotic relationship:
- Species 1 (Producer): Eats A, produces B and C as waste
- Species 2 (Recycler): Eats B and C, produces A as waste

Together they form a closed loop where waste from one is food for the other!
"""

from engine.core import Engine
from render.world_object import WorldObject
from biology.cell import Cell
from biology.gen import Gen
from biology.genoma import Genoma
from biology.world import World


if __name__ == "__main__":
    print("Starting Symbiotic Ecosystem...")
    engine = Engine(width=800, height=700, title="Symbiotic Life")
    
    world = World(800, 600, cell_size=10)
    
    # Initial seed: Only A is available in the environment
    world.seed_clusters("A", total_amount=5000, num_clusters=8)
    
    # ========================================
    # SPECIES 1: "PRODUCER" (Green cells)
    # ========================================
    # Eats: A
    # Produces: B, C (as waste)
    # Energy: High yield
    
    gen_producer = Gen(
        input={"A": 1},
        output={"B": 0.5, "C": 0.5},  # Produces B and C
        cost=0.2,
        prob=0.98,
        energy_yield=2.5
    )
    
    genoma_producer = Genoma([gen_producer])
    
    # Verify waste
    cell_test = Cell(genoma_producer)
    print(f"Producer waste: {cell_test._identify_waste()}")  # Should be {B, C}
    
    # ========================================
    # SPECIES 2: "RECYCLER" (Different color)
    # ========================================
    # Eats: B, C (the waste from Producer!)
    # Produces: A (as waste, which feeds Producer!)
    # Energy: Medium yield
    
    gen_recycler_b = Gen(
        input={"B": 1},
        output={"A": 0.6},  # Converts B back to A
        cost=0.25,
        prob=0.95,
        energy_yield=1.5
    )
    
    gen_recycler_c = Gen(
        input={"C": 1},
        output={"A": 0.6},  # Converts C back to A
        cost=0.25,
        prob=0.95,
        energy_yield=1.5
    )
    
    # High tolerance to B and C since they eat it
    gen_tolerance = Gen(
        input={},
        output={},
        cost=0,
        prob=1.0,
        energy_yield=0,
        tolerance={"B": 100, "C": 100}
    )
    
    genoma_recycler = Genoma([gen_recycler_b, gen_recycler_c, gen_tolerance])
    
    # Verify waste
    cell_test2 = Cell(genoma_recycler)
    print(f"Recycler waste: {cell_test2._identify_waste()}")  # Should be {A}
    
    print("\n🔄 CLOSED LOOP DETECTED!")
    print("Producer: A → B,C (waste)")
    print("Recycler: B,C → A (waste)")
    print("Result: Perfect symbiosis! ♻️\n")
    
    # ========================================
    # CREATE INITIAL POPULATION
    # ========================================
    
    # Add Producer cells (will eat A, produce B and C)
    for i in range(3):
        cell = Cell(genoma_producer)
        world.add_cell(cell, 20 + i*5, 20 + i*3)
    
    # Add Recycler cells (will eat B and C, produce A)
    for i in range(3):
        cell = Cell(genoma_recycler)
        world.add_cell(cell, 50 + i*5, 30 + i*3)
    
    # ========================================
    # RUN SIMULATION
    # ========================================
    
    world_object = WorldObject(world)
    engine.add_object(world_object)
    
    print("Watch the symbiosis:")
    print("- Green cells (Producers) will create B and C waste")
    print("- Different colored cells (Recyclers) will consume that waste")
    print("- Recyclers will produce A, feeding the Producers")
    print("- A sustainable ecosystem emerges! 🌱\n")
    
    engine.run()
    print("Bye")
