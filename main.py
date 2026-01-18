
from engine.core import Engine
from render.world_object import WorldObject
from biology.cell import Cell
from biology.gen import Gen
from biology.genoma import Genoma
from biology.world import World




if __name__ == "__main__":
    print("Starting engine...")
    engine = Engine(width=800, height=700, title="Basic Life")
    
    world = World(80, 60)
    world.seed_nutrients("A", 5)

    gen = Gen({"A":1}, {"B":1}, cost=0.5, prob=1.0, energy_yield=1)
    genoma = Genoma([gen])
    cell = Cell(genoma)

    world.add_cell(cell, 40, 30)
  
    world_object = WorldObject(world)
    engine.add_object(world_object)
    
    engine.run()
    print("Bye")
