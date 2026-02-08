class CellAction:
    """
    Represents an action a cell wants to perform.
    
    Actions are created by cells during their decision-making phase
    and executed by the world in a controlled manner.
    """
    
    # Action types
    ABSORB = "absorb"
    RELEASE = "release"
    MOVE = "move"
    
    def __init__(self, action_type, **kwargs):
        """
        Initializes a cell action.
        
        Args:
            action_type (str): Type of action (ABSORB, RELEASE, MOVE).
            **kwargs: Action-specific parameters:
                - For ABSORB: molecule (str), amount (float)
                - For RELEASE: molecule (str), amount (float)
                - For MOVE: direction (tuple): (dx, dy)
        """
        self.type = action_type
        self.params = kwargs
    
    def __repr__(self):
        return f"CellAction({self.type}, {self.params})"
