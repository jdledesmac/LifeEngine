
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
    # Use clustered seeding (Rich zones vs Deserts)
    world.seed_clusters("A", total_amount=4000, num_clusters=6)
    world.seed_clusters("C", total_amount=3000, num_clusters=4)

    gen_a = Gen({"A":1}, {"B":0.2, "C":0.8}, cost=0.2, prob=0.98, energy_yield=2)
    gen_c = Gen({"C":1}, {}, cost=0.15, prob=0.95, energy_yield=1.2)
    # Detox gene gives high tolerance to B (Waste)
    gen_detox = Gen(input={"B":1}, output={}, cost=0.3, prob=0.98, energy_yield=0, tolerance={"B":100})
    
    genoma_fast = Genoma([gen_a, gen_detox])
    genoma_slow = Genoma([gen_c])
    genoma_mixed = Genoma([gen_a, gen_c, gen_detox])
    cell_fast = Cell(genoma_fast)
    cell_mixed = Cell(genoma_mixed)

    world.add_cell(cell_fast, 40, 30)
    world.add_cell(cell_mixed, 50, 40)
    
  
    world_object = WorldObject(world)
    engine.add_object(world_object)
    
    engine.run()
    print("Bye")
