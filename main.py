
from engine.core import Engine
from render.world_object import WorldObject
from biology.cell import Cell
from biology.gen import Gen
from biology.genoma import Genoma
from biology.world import World




if __name__ == "__main__":
    print("Starting engine...")
    engine = Engine(width=800, height=700, title="Basic Life")
    
    world = World(800, 600, cell_size=10)
    # world.seed("A",10)
    # Use clustered seeding for interesting gameplay (Rich zones vs Deserts)
    world.seed_clusters("A", total_amount=40000, num_clusters=6)

    gen = Gen({"A":1}, {"B":0.2, "C":0.8}, cost=0.2, prob=0.95, energy_yield=2)
    detox_gen=Gen(input={"B":1}, output={}, cost=0.3, prob=0.95, energy_yield=0)
    genoma = Genoma([gen, detox_gen])
    cell = Cell(genoma)

    world.add_cell(cell, 40, 30)
    
  
    world_object = WorldObject(world)
    engine.add_object(world_object)
    
    engine.run()
    print("Bye")
