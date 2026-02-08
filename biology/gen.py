import random

class Gen:
    """
    Represents a gene that defines a specific metabolic reaction.
    
    A gene takes certain chemical inputs, consumes energy, and produces chemical outputs
    based on a certain probability. It also defines environmental tolerances for the cell.
    """
    def __init__(self, input, output, cost, prob, energy_yield=0, tolerance=None):
        """
        Initializes a new Gen instance.

        Args:
            input (dict): A dictionary mapping chemical names to the quantity required.
            output (dict): A dictionary mapping chemical names to the quantity produced.
            cost (float): The energy cost required to attempt the reaction.
            prob (float): The probability (0 to 1) that the reaction will succeed if attempted.
            energy_yield (float, optional): The energy produced by the reaction if successful. Defaults to 0.
            tolerance (dict, optional): A dictionary of environmental tolerances (e.g., temperature, pH).
                                       Defaults to an empty dictionary.
        """
        self.input = input
        self.output = output
        self.cost = cost
        self.prob = prob
        self.energy_yield = energy_yield
        self.tolerance = tolerance if tolerance else {}

    def can_react(self, chemistry, energy):
        """
        Checks if the reaction can be performed given the available chemistry and energy.

        Args:
            chemistry (dict): The current chemical composition of the environment/cell.
            energy (float): The current energy available to the cell.

        Returns:
            bool: True if the cell has enough energy (>= cost) and all required input chemicals.
        """
        if energy < self.cost:
            return False

        for mol, cant in self.input.items():
            if chemistry.get(mol,0) < cant:
                return False
        return True

    def reaction(self, chemistry, energy):
        """
        Executes the metabolic reaction defined by this gene.

        If the reaction succeeds (based on the gene's probability), inputs are consumed
        and outputs/energy yield are added. The energy cost is always subtracted.

        Args:
            chemistry (dict): The chemical composition to modify.
            energy (float): The current energy of the cell.

        Returns:
            float: The new energy level after the reaction attempt.
        """
        if random.random() > self.prob:
            return energy - self.cost
        for mol, cant in self.input.items():
            chemistry[mol] -= cant
        for mol, cant in self.output.items():
            chemistry[mol] = chemistry.get(mol, 0) + cant
        return energy - self.cost + self.energy_yield

    def get_id(self):
        """
        Returns a stable string representation of the gene's functional logic.

        This ID is used to compare genes and identify unique genetic traits.
        The ID is deterministic by sorting inputs, outputs, and tolerances.

        Returns:
            str: A string uniquely identifying this gene's logic.
        """
        # Sort inputs and outputs to ensure deterministic string
        inputs = sorted(self.input.items())
        outputs = sorted(self.output.items())
        tolerances = sorted(self.tolerance.items())
        return f"in:{inputs}|out:{outputs}|cost:{self.cost:.4f}|yield:{self.energy_yield:.4f}|tol:{tolerances}"

    def __repr__(self):
        """
        Returns a human-readable string representation of the Gen instance.

        Returns:
            str: A formatted string showing the gene's inputs, outputs, cost, and yield.
        """
        # Format dictionary values if they are floats
        def fmt_dict(d):
            return {k: round(v, 2) for k, v in d.items()}
            
        return f"Gen(in={fmt_dict(self.input)}, out={fmt_dict(self.output)}, cost={self.cost:.2f}, yield={self.energy_yield:.2f})"
