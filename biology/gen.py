import random

class Gen:
    def __init__(self, input, output, cost, prob, energy_yield=0):
        self.input = input
        self.output = output
        self.cost = cost
        self.prob = prob
        self.energy_yield = energy_yield

    def can_react(self, chemistry, energy):
        if energy < self.cost:
            return False

        for mol, cant in self.input.items():
            if chemistry.get(mol,0) < cant:
                return False
        return True

    def reaction(self, chemistry, energy):
        if random.random() > self.prob:
            return energy - self.cost
        for mol, cant in self.input.items():
            chemistry[mol] -= cant
        for mol, cant in self.output.items():
            chemistry[mol] = chemistry.get(mol, 0) + cant
        return energy - self.cost + self.energy_yield

    def __repr__(self):
        return f"Gen(in={self.input}, out={self.output}, cost={self.cost}, prob={self.prob}, yield={self.energy_yield})"