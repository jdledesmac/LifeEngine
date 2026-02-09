
from engine.core import Engine
from render.world_object import WorldObject
from biology.cell import Cell
from biology.gen import Gen
from biology.genoma import Genoma
from biology.world import World
import biology.chemistry_dict as chem


if __name__ == "__main__":
    print("Starting Digital Biology Engine...")
    engine = Engine(width=800, height=700, title="Digital Biology (8-Bit)")
    
    world = World(800, 600, cell_size=10)
    
    # 1. Seed the World with Digital Nutrients
    # Primary Source: ATP (255) - High Energy
    atp = chem.get_value("ATP")
    world.seed_clusters(atp, total_amount=5000, num_clusters=5)
    
    # Secondary Source: Glucose (240)
    glucose = chem.get_value("GLUCOSE")
    world.seed_clusters(glucose, total_amount=2000, num_clusters=3)

    # 2. Create Digital Genomes
    # "Sugar Eater": Target mask matches Glucose (240)
    # Reaction with ATP (255): Extracts 240, Waste = 15 (CO2)
    gen_sugar = Gen(mask=glucose, cost_base=10)
    genome_consumer = Genoma([gen_sugar])
    
    # "Scavenger": Target mask matches CO2 (15)
    # Targets the waste left by consumers
    co2 = chem.get_value("CO2")
    gen_scavenger = Gen(mask=co2, cost_base=5) # Cheaper enzyme
    genome_cleaner = Genoma([gen_scavenger])
    
    # "Omnivore": Has both
    genome_omni = Genoma([gen_sugar, gen_scavenger])

    # 3. Spawn Cells
    cell_consumer = Cell(genome_consumer)
    cell_cleaner = Cell(genome_cleaner)
    cell_omni = Cell(genome_omni)

    # Place them in rich zones
    world.add_cell(cell_consumer, 40, 30)
    world.add_cell(cell_cleaner, 42, 32)
    world.add_cell(cell_omni, 38, 35)
    
    # Add a few more random ones
    import random
    for _ in range(5):
        c = Cell(Genoma([gen_sugar]))
        c.energy = 500 # Give them a head start
        world.add_cell(c, random.randint(30, 50), random.randint(20, 40))
  
    # 4. Setup Visualization
    world_object = WorldObject(world)
    engine.add_object(world_object)
    
    engine.run()
    print("Simulation Ended")
